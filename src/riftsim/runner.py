# run_episode / EpisodeResult / export_trace（docs/api_contract.md §5；T-0134 收敛保障循环）
from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from . import engine, legality
from .actions import Action, DecisionRequest
from .config import GameConfig
from .errors import IllegalActionError
from .snapshot import state_hash
from .state import GameState
from .trace import schema as tschema
from .trace.sink import TraceSink


@dataclass
class EpisodeResult:
    match_id: str
    winner: int | None
    termination: str
    length_steps: int
    final_scores: tuple[int, int]
    reward: dict[int, float]
    invalid_action_count: int
    final_state_hash: str
    trace_path: str | None
    seed: int
    policy_ids: list[str]
    duration_ms: int = 0


def _reward(state: GameState, win: float = 1.0, loss: float = -1.0, truncated: float = 0.0) -> dict[int, float]:
    if state.winner in (0, 1):
        return {state.winner: win, 1 - state.winner: loss}
    return {0: truncated, 1: truncated}


def run_episode(
    policy_a,
    policy_b,
    seed: int,
    *,
    trace_level: str = "summary",
    config: GameConfig | None = None,
    out_dir: str | Path | None = "runs",
) -> EpisodeResult:
    """完整对局（T-0131/0132/0134）。policy_x 须实现 act(obs, legal, rng)->Action。"""
    t0 = time.perf_counter()
    if config is None:
        from .cards import make_skeleton_deck

        cfg = GameConfig(
            decks=(make_skeleton_deck("A", "hero-a"), make_skeleton_deck("B", "hero-b")),
            trace_level=trace_level,
        )
    else:
        cfg = config
    state = engine.reset(seed, cfg)
    state.meta.trace_level = trace_level
    policies = [policy_a, policy_b]
    policy_ids = [getattr(p, "policy_id", type(p).__name__) for p in policies]
    sink = TraceSink(trace_level, sample_every=cfg.sample_every)
    sink.on_header(tschema.header(state, policy_ids))
    obs_rng = random.Random(seed ^ 0x5EED)

    steps = 0
    while not state.ended and steps < state.meta.max_steps:
        if state.current_request is None:
            raise RuntimeError("engine stalled: no decision point and not ended")
        req = state.current_request
        player = req["player"]
        legal = legality.legal_for_request(state, DecisionRequest.from_dict(req))
        # CONCEDE 恒合法但不出现在 for_request；训练默认不发起
        obs = engine.observe(state, player)
        try:
            action = policies[player].act(obs, legal, obs_rng)
        except Exception as e:  # 策略异常归因为该局失败（训练诊断入口）
            state.ended, state.termination = True, __import__("riftsim.enums", fromlist=["Termination"]).Termination.ERROR
            state.winner = 1 - player
            break
        if action.kind.value == "concede":
            pass  # 允许策略主动认输（恒合法）
        elif not any(_same(a, action) for a in legal):
            state.invalid_action_count += 1
            from .enums import Termination

            state.ended, state.termination, state.winner = True, Termination.ERROR, 1 - player
            break
        # 策略异常归因为该局失败（训练诊断入口）——上方 except 同理
        sink.on_decision(tschema.decision(state, req, legal, action))
        result = engine.step(state, action)
        for e in result.events:
            sink.on_event(tschema.event(state, e))
        if sink.level in ("sampled", "debug"):
            sink.on_snapshot(tschema.snapshot_record(state), step_id=state.step_id)
        steps += 1
    # 截断由 engine._finish_step 统一处理（max_steps 到达即 TRUNCATED 终局）

    reward = _reward(state)
    footer = tschema.footer(state, reward, ok=True)
    footer["final_state_hash"] = state_hash(state)
    footer["trace_completeness"]["written_events"] = state.event_seq
    sink.on_footer(footer)
    trace_path = None
    if out_dir is not None:
        trace_path = sink.flush(out_dir)
    return EpisodeResult(
        match_id=state.meta.match_id,
        winner=state.winner,
        termination=state.termination.value if state.termination else "error",
        length_steps=state.step_id,
        final_scores=(state.players[0].score, state.players[1].score),
        reward=reward,
        invalid_action_count=state.invalid_action_count,
        final_state_hash=footer["final_state_hash"],
        trace_path=str(trace_path) if trace_path else None,
        seed=seed,
        policy_ids=policy_ids,
        duration_ms=int((time.perf_counter() - t0) * 1000),
    )


def _same(a: Action, b: Action) -> bool:
    return a.kind == b.kind and a.actor == b.actor and a.source_uid == b.source_uid and a.digest() == b.digest()


def export_trace(match_id: str, *, visibility: str = "public", out_dir: str | Path = "runs") -> dict[str, Any]:
    """读取 trace 并做基础校验（visualization_spec §3.6；T-0131 配套）。"""
    if visibility != "public":
        raise NotImplementedError("privileged trace 通道预留；默认 public")
    path = Path(out_dir) / f"{match_id}.jsonl"
    if not path.exists():
        raise FileNotFoundError(path)
    recs = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    header, footer = recs[0], recs[-1]
    ok = footer.get("trace_completeness", {}).get("ok", False)
    chosen_ok = all(
        r.get("chosen_action_id") in (r.get("legal_action_ids") or [])
        for r in recs if r.get("type") == "decision"
    )
    return {"match_id": match_id, "records": len(recs), "header": header,
            "footer": footer, "completeness_ok": ok, "chosen_in_legal": chosen_ok}
