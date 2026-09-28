# GameEvent 构造（docs/api_contract.md §7；引擎产生事件，UI 不推断）
from __future__ import annotations

from typing import Any

from .enums import EventType
from .state import GameState


def emit(
    state: GameState,
    type_: EventType,
    *,
    rule_ids: list[str] | None = None,
    card_ids: list[str] | None = None,
    public: dict[str, Any] | None = None,
    privileged: dict[str, Any] | None = None,
) -> None:
    """追加事件到 state.pending_events（before/after hash 由 engine.step 统一补充）。"""
    state.event_seq += 1
    state.pending_events.append(
        {
            "event_seq": state.event_seq,
            "step_id": state.step_id,
            "type": type_.value,
            "rule_ids": rule_ids or [],
            "card_ids": card_ids or [],
            "public": public or {},
            "privileged": privileged,
            "before_state_hash": None,
            "after_state_hash": None,
        }
    )


def drain_events(state: GameState) -> list[dict]:
    out = state.pending_events
    state.pending_events = []
    return out
