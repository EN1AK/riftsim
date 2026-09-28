# trace 记录构造（docs/visualization_spec.md §2.1-2.5）
from __future__ import annotations

import time
from typing import Any

from ..actions import Action
from ..state import GameState
from ..version import (
    ACTION_LAYOUT_VERSION, CARD_POOL_VERSION, ENGINE_VERSION, RULESET_VERSION,
    TRACE_SCHEMA_VERSION,
)


def header(state: GameState, policy_ids: list[str]) -> dict[str, Any]:
    m = state.meta
    return {
        "type": "header",
        "schema_version": TRACE_SCHEMA_VERSION,
        "engine_version": ENGINE_VERSION,
        "ruleset_version": m.ruleset_version,
        "card_db_version": m.card_pool_version or CARD_POOL_VERSION,
        "spec_hash": m.spec_hash,
        "action_layout_version": ACTION_LAYOUT_VERSION,
        "match_id": m.match_id,
        "seed": m.seed,
        "config": m.config,
        "policy_ids": policy_ids,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "visibility": "public",
        "trace_level": m.trace_level,
    }


def decision(state: GameState, request: dict, legal: list[Action], chosen: Action) -> dict[str, Any]:
    return {
        "type": "decision",
        "match_id": state.meta.match_id,
        "step_id": state.step_id,
        "player_id": chosen.actor,
        "request_kind": request.get("kind"),
        "legal_action_ids": [a.digest() for a in legal],
        "chosen_action_id": chosen.digest(),
        "rng_state_ref": state.rng.counts(),
    }


def event(state: GameState, e: dict) -> dict[str, Any]:
    return {
        "type": "event",
        "match_id": state.meta.match_id,
        "event_seq": e["event_seq"],
        "step_id": e["step_id"],
        "rule_ids": e["rule_ids"],
        "card_ids": e["card_ids"],
        "event_type": e["type"],
        "public_payload": e["public"],
        "privileged_payload": e.get("privileged"),
        "before_state_hash": e.get("before_state_hash"),
        "after_state_hash": e.get("after_state_hash"),
    }


def snapshot_record(state: GameState) -> dict[str, Any]:
    from ..observation import observe
    from ..snapshot import state_hash

    return {
        "type": "snapshot",
        "match_id": state.meta.match_id,
        "step_id": state.step_id,
        "public_view_by_player": {"0": observe(state, 0), "1": observe(state, 1)},
        "privileged_state_ref": None,
        "rng_state_ref": state.rng.counts(),
        "state_hash": state_hash(state),
    }


def footer(state: GameState, reward: dict[int, float], *, ok: bool) -> dict[str, Any]:
    m = state.meta
    reason = state.termination.value if state.termination else None
    return {
        "type": "footer",
        "match_id": m.match_id,
        "result": {"winner": state.winner, "termination_reason": reason, "modal_winner": False},
        "reward_by_player": {str(k): v for k, v in reward.items()},
        "length": {"decision_steps": state.step_id, "turns": state.turn_number,
                   "events": state.event_seq},
        "invalid_action_count": state.invalid_action_count,
        "final_state_hash": None,  # 由 runner 填
        "trace_completeness": {"expected_events": state.event_seq, "written_events": None, "ok": ok},
    }
