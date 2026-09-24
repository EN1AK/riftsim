## Purpose

Answers Riftbound rules questions through a bounded planner-tool loop over a shared evidence pool, so that card-grounded questions get cited, validated answers with a deterministic one-shot fallback on any agent failure.

## ADDED Requirements

### Requirement: Agent loop executes bounded planner actions

The system SHALL run a loop in which each planner output is a single JSON action selecting a retrieval tool and its arguments, execute the selected tool, feed the observation back, and stop after a configurable maximum number of steps (`RAG_AGENT_MAX_STEPS`, default 4, values clamped to 1–8).

#### Scenario: Valid actions execute in order

- **GIVEN** the planner emits a sequence of valid JSON tool actions
- **WHEN** the agent loop runs
- **THEN** each selected tool executes with the given arguments and its observation is fed back to the planner for the next step

#### Scenario: Step limit stops the loop

- **GIVEN** a maximum of 4 steps and a planner that never submits an answer
- **WHEN** the loop reaches the 4th action
- **THEN** the loop stops requesting planner actions and produces a fallback result

#### Scenario: Step bound is clamped

- **GIVEN** `RAG_AGENT_MAX_STEPS` is set to `99`
- **WHEN** the agent configuration is loaded
- **THEN** the effective maximum is `8`

### Requirement: Agent loop rejects invalid or useless actions deterministically

The system SHALL treat unparseable planner output, unknown tools, and malformed arguments as invalid actions, SHALL reject an action duplicating an earlier `(tool, arguments)` signature as useless, and SHALL stop the loop into fallback after two consecutive invalid planner outputs. An invalid or duplicate action MUST NOT crash the loop.

#### Scenario: Duplicate action rejected

- **GIVEN** the planner repeats an identical `(tool, arguments)` signature it already used in this question
- **WHEN** the loop validates the action
- **THEN** the action is not executed and the planner receives an observation explaining the duplicate

#### Scenario: Two consecutive invalid outputs stop the loop

- **GIVEN** the planner returns unparseable output on two consecutive steps
- **WHEN** the loop processes the second invalid output
- **THEN** the loop stops requesting planner actions and produces a fallback result

### Requirement: Tools accumulate evidence in a shared pool

The system SHALL add every rule row returned by any retrieval tool into a shared evidence pool keyed by `rule_id`, so that evidence gathered across steps is available to later steps and to answer validation.

#### Scenario: Pool grows across steps

- **GIVEN** step 1 returns 3 rule rows and step 2 returns 5 rows with 1 overlap
- **WHEN** both steps complete
- **THEN** the pool contains 7 distinct rule rows

### Requirement: Answers are submitted through citation validation

The system SHALL accept a final answer ONLY via the terminal `submit_answer` action, SHALL extract every bracketed citation marker from the answer text plus every entry of the action's citation list, SHALL require each to be a `rule_id` present in the evidence pool, and on validation failure SHALL return an error observation instead of ending the loop while steps remain.

#### Scenario: Valid submission ends the loop

- **GIVEN** an answer whose `[R-CR-716.1]` marker and citation list are all present in the pool
- **WHEN** `submit_answer` is validated
- **THEN** the loop ends with that answer as the final result
- **AND** the loop is marked not exhausted

#### Scenario: Unknown citation rejected and retried

- **GIVEN** an answer citing `[R-CR-999.9]` which is not in the pool
- **WHEN** `submit_answer` is validated
- **THEN** the loop does NOT end and the planner receives an observation naming the invalid citation
- **AND** the planner may submit a corrected answer while steps remain

### Requirement: Agent failure or exhaustion falls back deterministically

The system SHALL, when the loop ends without a validated submission, generate an answer from the accumulated pool rows using the existing one-shot generation path, and SHALL mark the result `exhausted`. When the pool is empty, the system SHALL return the fixed empty-retrieval answer with the `检索结果为空` warning instead of calling the generator. A planner LLM call failure SHALL also lead to this fallback rather than a user-visible crash.

#### Scenario: Exhausted loop falls back over gathered evidence

- **GIVEN** the loop used all steps and the pool holds 5 rows
- **WHEN** fallback runs
- **THEN** an answer is generated from those 5 pool rows
- **AND** the result is marked `exhausted`

#### Scenario: Empty pool yields the fixed empty answer

- **GIVEN** no tool produced any rule rows
- **WHEN** fallback runs
- **THEN** the result is the fixed empty-retrieval answer with the `检索结果为空` warning
- **AND** the result is marked `exhausted`
