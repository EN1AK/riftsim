# Add Riftbound Rules Agent Mode

## Why

The rift-rag service (`scripts/rag/rag_server.py`) currently answers every question with a single one-shot retrieval+generation pass. That is weak for card questions: nothing grounds a Chinese card mention to a card and its rules, there is no visibility into unresolved/ambiguous mentions, and nothing prevents hallucinated citations. The deterministic card resolver (`card_resolver.py`) and the retrieval tool layer (`EvidencePool`, `get_card_rules`, `search_rules`, `lookup_rule` in `rag_query.py`) are already implemented and tested but unused by the server. Meanwhile the downstream chain (kami-man client → ygo-rag gateway) is already contract-v2-ready — it sends `mode`/`trace` and tolerantly parses `resolved_cards`/`coverage`/`exhausted` — so only the server is missing.

## What Changes

- New `scripts/rag/agent_loop.py`: a bounded planner→tool loop with no agent framework. The planner (DeepSeek, OpenAI-compatible) emits strict JSON actions against tools operating on a shared evidence pool; `submit_answer` is the only terminal action and is citation-validated against the pool (every `[…]` marker and citation must be a pool `rule_id`). Any planner failure degrades deterministically to the existing one-shot pipeline.
- `scripts/rag/rag_server.py` upgraded to contract v2, additively: requests accept `mode` (`agent` default | `oneshot`) and `trace` (bool, default false); agent responses add `mode`, `exhausted`, `resolved_cards`, `coverage` (`unresolved_mentions`, `ambiguous_mentions`), plus `trace` when requested. Legacy fields (`answer`, `warnings`, `sources`) and all error semantics stay unchanged.
- `RagService` wires the pieces: pre-run deterministic card resolution on the query, run the agent loop in `agent` mode, and keep the current one-shot pipeline verbatim for `oneshot` mode (also the escape hatch/rollback).
- New env `RAG_AGENT_MAX_STEPS` (default 4, clamped 1–8); existing resolver/LLM envs (`RAG_CARD_RESOLUTION_*`, `RAG_LLM_CARD_EXTRACTION`, `RAG_LLM_CARD_SELECTION`, `RAG_CARDS_DB_PATH`) are documented as-is.

## Capabilities

### New Capabilities

- `riftbound-rules-agent`: Bounded planner-tool agent loop over an evidence pool for Riftbound rules QA — tool execution, step/action bounds, citation-validated answer submission, and deterministic fallback to one-shot generation.
- `rift-rag-service-contract`: The HTTP contract of the rift-rag service — legacy request/response invariants, additive v2 fields, mode selection, and error semantics (404/405/400/500, healthz).

### Modified Capabilities

(None — this repository has no existing capability specs.)

## Impact

- Affected code: new `scripts/rag/agent_loop.py`; modified `scripts/rag/rag_server.py`; minimal additions to `scripts/rag/rag_query.py` only if the loop needs small wrappers (existing tool functions are reused, not rewritten).
- New `scripts/rag/tests/test_agent_loop.py` (fixture LLM, no network) plus server contract cases for both modes.
- Downstream consumers (kami-man `rift_rag_api.py`, ygo-rag `rift_gateway` in change `add-riftbound-rules-gateway`): no code change needed — v2 fields are additive and already tolerated on both sides.
- Deployment: agent mode needs the same LLM envs as generation today (`RAG_LLM_MODEL`, `OPENAI_API_KEY`); rollback is `mode=oneshot` from the caller or redeploy.
- Out of scope: any change to `card_resolver.py` matching logic, reranking, multi-turn memory, and changes in kami-man/ygo-rag repos.
