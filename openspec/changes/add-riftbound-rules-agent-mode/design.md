# Design: Riftbound Rules Agent Mode

## Context

See proposal.md - Why for motivation. Current state and constraints:

- **Existing one-shot pipeline** (`scripts/rag/`): `rag_server.py` (bare ASGI + uvicorn on `127.0.0.1:7862`, `RagService` with lazy sqlite/vector/embedder, `parse_request`, `create_app(service)` handler injection, `GenerationError` → 500) serving `POST /api/query` `{query, top_k}` → `{answer, warnings, sources}`; `rag_query.py` hybrid retrieval (dense BGE-M3 top-30 in a persistent subprocess worker + keyword/rule-id LIKE top-30 → RRF k=60 → top-k) and `generate()` with bracket-citation extraction.
- **Already built, unused by the server** (previous session, tested): `card_resolver.py` (`CardResolver.resolve(query) -> {resolved, ambiguous, unresolved}`; deterministic-first alias index over `cards_bilingual.db` + R-CARD topics; env knobs `RAG_CARDS_DB_PATH`, `RAG_CARD_RESOLUTION_TOP_K`, `RAG_CARD_RESOLUTION_RETRY`, `RAG_LLM_CARD_EXTRACTION`, `RAG_LLM_CARD_SELECTION`) and the retrieval tool layer in `rag_query.py` (`EvidencePool`, `get_card_rules`, `search_rules(..., expansion_texts)`, `lookup_rule`). This change wires them in — it does not rebuild them.
- **Consumers are v2-ready**: kami-man's client sends `mode`/`trace` and tolerantly parses `resolved_cards`/`coverage`/`exhausted`; the ygo-rag gateway (`add-riftbound-rules-gateway`) passes both directions through. The full chain is kami-man → ygo-rag `/api/rift/query` → this service.
- **Data facts** (verified): `workspace/final/rules.db` (`rules` 2984 rows, `rule_cards` 7046 links, `rules_fts` unusable for Chinese), `cards_bilingual.db` (`cards` 1267 rows; composite CN names via sub_title + name; same names recur across variants).
- Architecture reference (read-only): ygo-rag `assistant_agent.py` (bounded planner→tool loop with strict JSON actions, duplicate-signature suppression, deterministic end) and `adjudication_agent.py` (deterministic card-resolution loop with visible coverage). We adopt the architecture, not the dependencies.

## Goals / Non-Goals

**Goals:**

- Bounded, citation-validated agent loop: the planner chooses tools but can only answer through `submit_answer` with pool-validated citations.
- Contract v2 additive: nothing breaks for existing `{answer, warnings, sources}` consumers.
- Deterministic fallback: any planner failure degrades to the current one-shot pipeline, never a user-visible crash.
- Fully testable without network/LLM (fixture planner), following the existing `scripts/rag/tests` pattern.

**Non-Goals:**

- No agent framework (LangGraph/LangChain) dependency; no new model dependencies.
- No multi-turn memory, clarification round-trips, reranking, or card images.
- No changes to `card_resolver.py` matching logic, the embedding worker, or consumers (kami-man/ygo-rag).

## Decisions

### D1. Contract v2 is additive; `agent` is the default mode

Request: legacy `query`/`top_k` unchanged; new optional `mode` (`agent` default | `oneshot`) and `trace` (bool, default false); invalid `mode`/`top_k` → same `400 {"error"}` shape. Response (agent mode): legacy fields plus `mode`, `exhausted`, `resolved_cards`, `coverage {unresolved_mentions, ambiguous_mentions}` — `trace` only when requested. `oneshot` omits v2 fields entirely, preserving today's exact response shape. Rationale: kami-man and the ygo-rag gateway already parse both shapes tolerantly, so `agent` can be the default with `oneshot` as the escape hatch and rollback path. Alternative considered (default `oneshot`, opt-in agent): rejected — it would leave the new capability dark until every caller flips a flag with no compatibility benefit.

### D2. Hand-rolled planner loop, no framework

New `scripts/rag/agent_loop.py`: `planner → validate action → execute tool → append observation → planner → … → submit_answer → end`. Each planner call must return one JSON `{tool, arguments, rationale}`; the system prompt lists tool schemas, the pre-resolved cards, and the rules (cite only pool `rule_id`s; finish via `submit_answer`; never guess card/rule ids). Rationale: the repo has no LangChain-style deps, the loop surface is ~5 tools, and a hand-rolled loop keeps every failure mode deterministic and unit-testable. Framework adoption was considered and rejected as dependency weight with no behavioral need.

### D3. Tools operate on the existing tool layer and a per-question evidence pool

| Tool | Behavior |
| --- | --- |
| `resolve_cards(mentions: [str])` | Runs `CardResolver` (incl. optional LLM-assisted rounds, off by default). The service also pre-runs deterministic resolution on the raw query and injects the result into the planner prompt. |
| `get_card_rules(card_id, top_k?)` | Direct `rules ⋈ rule_cards` join; observation includes card display name and canonical text snippet. |
| `search_rules(query, top_k?)` | Existing hybrid retrieve via `rag_query.search_rules`; when cards are resolved, up to 2 canonical card texts are passed as `expansion_texts`. |
| `lookup_rule(ref)` | Exact `R-CR-716.1` / `R-CARD-OGN-242`, or `716.1` → `rule_id LIKE`. |
| `submit_answer(answer, citations)` | Terminal; citation-validated (D5), on failure returns an error observation instead of ending. |

Every tool call adds returned rows to one `EvidencePool` and appends to the trace (`step`, `tool`, `arguments`, `ok`, row counts). Dup-signature check compares `(tool, canonical JSON arguments)`.

### D4. Bounds: max steps, duplicate rejection, two-strike invalid stop

`RAG_AGENT_MAX_STEPS` default 4, clamped 1–8. Duplicate `(tool, arguments)` signatures are rejected with an observation (not counted as progress). Two consecutive unparseable/invalid planner outputs, or any planner LLM call failure → break to fallback. Rationale: these three bounds keep worst-case behavior deterministic in both latency and cost (≤ 4 planner calls + final generation, well under the downstream 200s gateway / 240s bot timeouts).

### D5. Citation validation on `submit_answer` (adapted from ygo-rag `submit_ruling`)

On submit, code regex-scans the answer for `[…]` markers; every marker must be a `rule_id` in the pool, and every `citations` entry must be in the pool. Invalid → error observation naming the bad citation; the planner may fix and resubmit while steps remain. An unvalidated submit never reaches the user. Rationale: this is the hard guarantee against hallucinated citations; the planner prompt alone is not trusted.

### D6. Deterministic fallback to the current one-shot path

When the loop ends without a validated submit: run the existing one-shot `generate(query, pool_rows)` over whatever the pool holds; empty pool → the existing fixed `EMPTY_RETRIEVAL_ANSWER` + `检索结果为空` warning; result marked `exhausted: true`. Generation failure inside generation (missing key/model) still raises `GenerationError` → HTTP 500, unchanged semantics. Rationale: worst case equals today's service quality; `exhausted` lets the bot show "答案基于部分证据" styling without treating it as an error.

### D7. Trace is request-scoped diagnostics only

Trace entries are lightweight dicts (`step`, `tool`, `arguments`, `ok`, `summary`); collected always, returned only when `trace: true`. No persistence in this change; tuning decisions later use sampled traces.

### D8. Runtime/deployment unchanged except wiring

`RagService` gains a lazily-built `CardResolver` (alias index from `cards_bilingual.db`, degrades to id-only matching with an stderr warning if missing) and the agent runner. Embedding subprocess worker, vector index memory profile, LLM envs (`RAG_LLM_MODEL`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`), and `--preload` behavior are unchanged; preload additionally warms the cards index.

## Risks / Trade-offs

- **Planner JSON drift wastes steps** → Strict schema prompt, 2-strike invalid stop, duplicate-signature rejection, fallback always yields an answer.
- **2–5 LLM calls per question raise group-chat latency/cost** → Small planner prompts, `max_steps=4` default, `mode=oneshot` escape hatch, and the planner model is the same cheap chat model already used for generation.
- **Hallucinated citations** → D5 pool validation; invalid submits never ship.
- **`agent` as default changes legacy callers' latency profile** → Additive contract means functional compatibility is preserved; any caller can pin `mode=oneshot`; kami-man already sends `mode` explicitly.
- **Ambiguous/fuzzy card matches misfire on short names** → Existing resolver keeps ambiguity visible in `coverage`; LLM extraction/selection stay off by default.
- **Fallback answer quality depends on pool content** when the planner flails → Accepted; equals or beats today's recall (pre-resolution expansion adds evidence today's pipeline lacks).

## Migration Plan

1. Implement `agent_loop.py` with fixture-planner unit tests (no network/LLM).
2. Wire `rag_server.py`: request parsing (`mode`/`trace`), agent path, v2 response assembly, resolver construction.
3. Verify: full `scripts/rag/tests` suite, `py_compile`, `openspec validate --strict`.
4. Live smoke: start the service; curl `agent` (card question, pure-rule question, garbage input) and `oneshot`; confirm response shapes and `Connection: close` behavior unchanged.
5. Rollout: kami-man's default already sends `mode=agent`, so v2 fields appear once deployed — through the ygo-rag gateway once `add-riftbound-rules-gateway` lands, or direct on 7862 meanwhile.
6. Rollback: callers set `mode=oneshot`, or redeploy previous rift-rag code; consumers tolerate both shapes.

## Open Questions

- Tune `RAG_AGENT_MAX_STEPS` (3 vs 4) against answer quality once trace data accumulates.
- If deterministic resolution miss-rate proves high (heavy slang/abbreviation), flip `RAG_LLM_CARD_EXTRACTION=1` and measure; default stays off to keep the hot path cheap.
