## Purpose

Defines the HTTP contract of the rift-rag service: the legacy QA request/response invariants, the additive contract-v2 fields for agent mode, and the error semantics that downstream consumers (ygo-rag gateway, kami-man bot) rely on.

## ADDED Requirements

### Requirement: Service accepts legacy and v2 QA requests

The system SHALL accept `POST /api/query` with `query` (required, non-empty string), `top_k` (optional integer 1–20, default 6), `mode` (optional `agent` or `oneshot`, default `agent`), and `trace` (optional boolean, default false), SHALL ignore unknown request keys, and SHALL reject invalid bodies with `400 {"error": <short message>}`.

#### Scenario: Legacy request runs with defaults

- **GIVEN** a request `{"query": "什么是迅捷"}` with no `mode` or `trace`
- **WHEN** the service processes it
- **THEN** the request is accepted with `top_k` defaulted to `6` and `mode` defaulted to `agent`

#### Scenario: Invalid mode rejected

- **GIVEN** a request with `mode` set to `"turbo"`
- **WHEN** the service validates the body
- **THEN** the response status is `400` with a JSON `error` message

#### Scenario: Unknown keys ignored

- **GIVEN** a request containing an extra key `"debug_level": 3`
- **WHEN** the service processes the otherwise valid request
- **THEN** the extra key does not affect validation or execution

### Requirement: Agent responses carry additive v2 fields

The system SHALL return `200` agent responses containing the legacy fields `answer` (string), `warnings` (list of strings), and `sources` (list of `{rule_id, topic}`), plus `mode` (`"agent"`), `exhausted` (boolean), `resolved_cards` (list), and `coverage` with `unresolved_mentions` (list of strings) and `ambiguous_mentions` (list), and SHALL include a `trace` list only when the request set `trace` to true.

#### Scenario: Agent response shape

- **GIVEN** a successful agent-mode question
- **WHEN** the service responds
- **THEN** the body contains `answer`, `warnings`, `sources`, `mode`, `exhausted`, `resolved_cards`, and `coverage`
- **AND** `exhausted` is a boolean

#### Scenario: Trace only on request

- **GIVEN** two identical valid questions, one with `trace: true` and one without
- **WHEN** both are answered
- **THEN** only the `trace: true` response contains a `trace` list of step entries

### Requirement: Coverage reports card resolution outcomes

The system SHALL report every resolved card mention with its `card_id`, the original `mention`, and resolution confidence, SHALL report ambiguous mentions together with their candidate cards, and SHALL report unresolved mentions as strings, all derived from deterministic card resolution over the cards/rules databases without guessing.

#### Scenario: Resolvable mention reported

- **GIVEN** a question mentioning a card whose name resolves to exactly one card
- **WHEN** the agent responds
- **THEN** `resolved_cards` contains an entry with that card's `card_id` and the original mention text

#### Scenario: Ambiguous mention stays visible

- **GIVEN** a question mentioning a card name shared by multiple cards
- **WHEN** the agent responds
- **THEN** `coverage.ambiguous_mentions` contains the mention with its candidate cards
- **AND** the service does not pick one silently

#### Scenario: Unresolvable mention reported

- **GIVEN** a question mentioning a card name absent from the databases
- **WHEN** the agent responds
- **THEN** `coverage.unresolved_mentions` contains that mention string

### Requirement: Oneshot mode preserves legacy behavior

The system SHALL, for requests with `mode` set to `oneshot`, execute exactly one retrieval pass plus one generation call and return a body identical in shape to the pre-v2 response (`answer`, `warnings`, `sources` only), omitting the v2 fields.

#### Scenario: Oneshot response omits v2 fields

- **GIVEN** a valid request with `mode: "oneshot"`
- **WHEN** the service responds successfully
- **THEN** the body contains `answer`, `warnings`, and `sources`
- **AND** it does not contain `exhausted`, `resolved_cards`, or `coverage`

### Requirement: Error and auxiliary endpoint semantics are unchanged

The system SHALL keep the existing semantics: `400 {"error"}` for invalid request bodies, `500 {"error"}` for generation failures, `404`/`405` for unknown paths/methods, and `GET /healthz` returning `200 {"ok": true}` without loading models.

#### Scenario: Generation failure surfaces as 500

- **GIVEN** the LLM generation endpoint is not configured or fails
- **WHEN** a valid question is processed
- **THEN** the response status is `500` with a JSON `error` message

#### Scenario: Health check stays lightweight

- **WHEN** `GET /healthz` is called
- **THEN** the service returns `200 {"ok": true}` without loading the embedding model
