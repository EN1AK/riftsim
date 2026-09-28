# replay 与 trace 回放校验（T-0131/0132/0133）
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Sequence

from . import engine, legality
from .actions import Action, DecisionRequest
from .config import GameConfig
from .errors import ReplayMismatchError
from .snapshot import restore, state_hash
from .state import GameState


def action_from_digest(digest: str) -> Action:
    d = json.loads(digest)
    from .enums import ActionKind

    return Action(kind=ActionKind(d["kind"]), actor=d["actor"],
                  source_uid=d.get("source_uid"), params=d.get("params") or {})


def replay(initial, action_log: Sequence[Action], *, seed: int | None = None) -> GameState:
    """(initial snapshot | seed+config), 逐动作重放，返回终态。"""
    if isinstance(initial, dict) and initial.get("snapshot_version"):
        state = restore(initial)
    elif isinstance(initial, int):
        state = engine.reset(initial, None)
    else:
        state = engine.reset(seed, initial)
    for a in action_log:
        engine.step(state, a)
    return state


def trace_replay_check(trace_path: str | Path) -> dict:
    """T-0131 回放校验：逐步校验 chosen ∈ legal、事件 hash 链（[before,after] 区间一致）、
    终态 hash 与 footer 一致。"""
    recs = [json.loads(x) for x in Path(trace_path).read_text(encoding="utf-8").splitlines() if x.strip()]
    header = recs[0]
    footer = recs[-1]
    # state_hash 覆盖运行配置（含 trace_level）：回放须以同等级复位，
    # 否则 debug/summary 之间的 meta 差异会造成确定性“假分叉”。
    from .cards import make_skeleton_deck
    from .config import GameConfig as _Cfg

    cfg = _Cfg(
        decks=(make_skeleton_deck("A", "hero-a"), make_skeleton_deck("B", "hero-b")),
        trace_level=header.get("trace_level", "summary"),
    )
    state = engine.reset(header["seed"], cfg)
    checked = 0
    hash_chain_ok = True
    for r in recs:
        if r.get("type") != "decision":
            continue
        req = DecisionRequest.from_dict(state.current_request) if state.current_request else None
        assert req is not None, f"step {r['step_id']}: no open request during replay"
        legal = legality.legal_for_request(state, req)
        legal_digests = {a.digest() for a in legal}
        chosen = r["chosen_action_id"]
        if chosen not in legal_digests and json.loads(chosen)["kind"] != "concede":
            raise ReplayMismatchError(r["step_id"], "chosen∈legal", chosen)
        engine.step(state, action_from_digest(chosen))
        checked += 1
    final_ok = state_hash(state) == footer["final_state_hash"]
    return {
        "match_id": header["match_id"],
        "decisions_checked": checked,
        "final_hash_ok": final_ok,
        "winner": state.winner,
        "termination": state.termination.value if state.termination else None,
        "footer_winner": footer["result"]["winner"],
        "incomplete": not footer.get("trace_completeness", {}).get("ok", False),
    }
