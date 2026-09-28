# snapshot/restore/clone/state_hash（docs/api_contract.md §8）
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

from .state import GameState
from .version import SNAPSHOT_VERSION


def canonical_state_json(state: GameState) -> str:
    """规范序列化：剔除派生/缓冲字段（pending_events 不入哈希）。"""
    d = state.to_dict()
    return json.dumps(d, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def state_hash(state: GameState) -> str:
    return hashlib.sha256(canonical_state_json(state).encode("utf-8")).hexdigest()


def snapshot(state: GameState) -> dict[str, Any]:
    return {
        "snapshot_version": SNAPSHOT_VERSION,
        "state": state.to_dict(),
        "state_hash": state_hash(state),
    }


def restore(snap: dict[str, Any]) -> GameState:
    ver = snap.get("snapshot_version")
    if ver != SNAPSHOT_VERSION:
        from .errors import TraceFormatError

        raise TraceFormatError(f"unsupported snapshot_version: {ver}")
    from .errors import EngineInvariantError

    st = GameState.from_dict(snap["state"])
    if state_hash(st) != snap["state_hash"]:
        raise EngineInvariantError("restore: state_hash mismatch")
    return st


def clone(state: GameState) -> GameState:
    """可信内部执行者专用（docs/training_architecture.md §7）。"""
    return copy.deepcopy(state)
