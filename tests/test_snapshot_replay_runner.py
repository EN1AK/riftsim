# snapshot/restore/replay、runner、trace（T-0013/0053/0054/0131/0132/0133/0134/真随机收敛）
import json
from pathlib import Path

import pytest

from riftsim import engine
from riftsim.actions import Action
from riftsim.enums import ActionKind, Zone
from riftsim.runner import export_trace, run_episode
from riftsim.replay import action_from_digest, trace_replay_check
from riftsim.snapshot import restore, snapshot, state_hash
from riftsim.policies import EndTurnPolicy, RandomPolicy, ScriptedPolicy
from tests.helpers import fresh, give_hand
from riftsim.enums import ActionKind as AK, CardType, Domain


def test_t0133_snapshot_restore_equivalent():
    st, first = fresh()
    # 制造闭环：打出法术 pending
    uid = give_hand(st, first, {"def_id": "t:sx:1", "name": "法术", "card_types": {CardType.SPELL},
                                "domains": {Domain.R}, "cost_energy": 0, "cost_power": ()})
    a = next(a for a in engine.legal_actions(st, first)
             if a.kind == AK.PLAY_CARD and a.source_uid == uid)
    engine.step(st, a)
    assert st.chain_live()
    snap = snapshot(st)
    # 原路径：双方让过→法术结算
    other = st.current_request["player"]
    engine.step(st, Action(AK.PASS, other))
    engine.step(st, Action(AK.PASS, 1 - other))
    h1 = state_hash(st)
    # 恢复路径：同样动作序列
    st2 = restore(snap)
    other2 = st2.current_request["player"]
    engine.step(st2, Action(AK.PASS, other2))
    engine.step(st2, Action(AK.PASS, 1 - other2))
    assert state_hash(st2) == h1


def test_t0013_same_seed_same_hash_after_fixfixed_script():
    st1, first = fresh(42)
    st2 = engine.reset(42, None)
    # 相同动作脚本：双调度 0 + END_MAIN
    from riftsim.policies import ScriptedPolicy

    for st in (st1, st2):
        if st.current_request and st.current_request["kind"] == "mulligan":
            engine.step(st, Action(AK.RESOLVE_CHOICE, st.current_request["player"], params={"set_aside": []}))
        if st.current_request and st.current_request["kind"] == "mulligan":
            engine.step(st, Action(AK.RESOLVE_CHOICE, st.current_request["player"], params={"set_aside": []}))
        if st.current_request and st.current_request["kind"] == "main_action":
            engine.step(st, Action(AK.END_MAIN, st.current_request["player"]))
    assert state_hash(st1) == state_hash(st2)


def test_t0132_endturn_episode_deterministic(tmp_path):
    r1 = run_episode(EndTurnPolicy(), EndTurnPolicy(), 7, trace_level="off", out_dir=None)
    r2 = run_episode(EndTurnPolicy(), EndTurnPolicy(), 7, trace_level="off", out_dir=None)
    assert r1.final_state_hash == r2.final_state_hash
    assert r1.termination == r2.termination


def test_t0134_random_episodes_converge(tmp_path):
    results = []
    for seed in range(30):
        r = run_episode(RandomPolicy(seed * 2 + 1), RandomPolicy(seed * 2 + 2), seed,
                        trace_level="off", out_dir=None)
        results.append(r)
    assert all(r.termination in ("score", "effect_win", "concede", "burnout", "truncated") for r in results)
    assert all(r.invalid_action_count == 0 for r in results)
    # 骨架对局应具收敛性：允许少量 truncated，但大多数应规则内终止
    truncated = sum(1 for r in results if r.termination == "truncated")
    assert truncated <= 5, f"too many truncations: {truncated}/30"
    # 终局态一致性：胜者分数合法（非 truncated 时 winner 非 None）
    for r in results:
        if r.termination != "truncated":
            assert r.winner in (0, 1)


def test_t0131_trace_roundtrip_and_checks(tmp_path):
    r = run_episode(RandomPolicy(1), RandomPolicy(2), 11, trace_level="debug", out_dir=tmp_path)
    assert r.trace_path and Path(r.trace_path).exists()
    info = export_trace(r.match_id, out_dir=tmp_path)
    assert info["completeness_ok"] and info["chosen_in_legal"]
    checks = trace_replay_check(r.trace_path)
    assert checks["final_hash_ok"]
    assert checks["winner"] == checks["footer_winner"]
    assert checks["decisions_checked"] > 0


def test_t0053_t0054_fifo_resolve_latest_first():
    """连锁结算后进先出（339/340）：法术 A 入链→让过轮流入窗；
    A 结算前无其他反应则直接结算。"""
    st, first = fresh()
    uid = give_hand(st, first, {"def_id": "t:fy:1", "name": "法术甲", "card_types": {CardType.SPELL},
                                "domains": {Domain.R}, "cost_energy": 0, "cost_power": ()})
    a = next(a for a in engine.legal_actions(st, first)
             if a.kind == AK.PLAY_CARD and a.source_uid == uid)
    engine.step(st, a)
    players_seq = []
    while st.chain_live():
        req = st.current_request
        assert req, "chain live but no request"
        players_seq.append(req["player"])
        engine.step(st, Action(AK.PASS, req["player"]))
    assert not st.chain_live()
    assert st.obj(uid).zone == Zone.TRASH
