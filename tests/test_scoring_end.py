# 得分/终局/认输（T-0014/0039/0095..0099/0101/0043/0044/0045/0055）
from riftsim import engine
from riftsim.actions import Action
from riftsim.enums import ActionKind, DecisionKind, EventType, Phase, Termination, Zone
from riftsim.errors import IllegalActionError
from tests.helpers import fresh, place_battlefield_unit, place_base


def test_t0039_hold_score_train():
    """据守：控制战场一方在其回合开始阶段计分步骤得 1 分（315.2/469.2/470）。"""
    st, first = fresh()
    second = 1 - first
    # first 控制战场 0；等待 first 的下一个开始阶段（两个 END_MAIN 回环）
    st.battlefields[0].controller = first
    place_battlefield_unit(st, first, 0)
    old = st.players[first].score
    engine.step(st, Action(ActionKind.END_MAIN, first))
    # first 尚未到其新回合；控制只在 first 的开始阶段计分
    assert st.players[first].score == old
    engine.step(st, Action(ActionKind.END_MAIN, second))
    # first 新回合开始阶段已计分
    assert st.players[first].score == old + 1


def test_t0095_conquer_unique_per_battlefield_per_turn():
    st, first = fresh()
    bf = st.battlefields[0]
    p = st.players[first]
    p.score_marks.setdefault(bf.uid, []).append(st.turn_number)
    from riftsim.scoring import score_conquer

    score_conquer(st, first, bf)
    assert p.score == 0  # 本回合已得过 → 封锁


def test_t0096_hold_then_conquer_same_bf_same_turn_blocked():
    st, first = fresh()
    bf = st.battlefields[0]
    p = st.players[first]
    # 据守标记本回合已计
    p.score_marks.setdefault(bf.uid, []).append(st.turn_number)
    p.score = 1
    from riftsim.scoring import score_conquer

    score_conquer(st, first, bf)
    assert p.score == 1


def test_t0097_final_point_forbidden_draws_instead():
    st, first = fresh()
    p = st.players[first]
    p.score = st.meta.win_score - 1  # 7
    # 两个战场：bf0 本回合已得分、bf1 未得分 → 不满足"每个战场"
    p.score_marks.setdefault(st.battlefields[0].uid, []).append(st.turn_number)
    from riftsim.scoring import score_conquer

    hand_before = len(p.hand)
    score_conquer(st, first, st.battlefields[1])
    assert p.score == st.meta.win_score - 1  # 未得分
    assert len(p.hand) == hand_before + 1   # 改为抽 1


def test_t0099_tie_no_winner():
    st, first = fresh()
    st.players[0].score = 8
    st.players[1].score = 8
    from riftsim.cleanup_sys import win_check

    assert win_check(st) is False
    assert st.ended is False


def test_t0014_score_win_at_cleanup():
    st, first = fresh()
    st.players[first].score = 8
    st.players[1 - first].score = 6
    engine.step(st, Action(ActionKind.END_MAIN, first))
    assert st.ended and st.winner == first
    assert st.termination == Termination.SCORE


def test_t0101_concede():
    st, first = fresh()
    engine.step(st, Action(ActionKind.CONCEDE, 1 - first))
    assert st.ended and st.winner == first
    assert st.termination == Termination.CONCEDE
    # 终局后不再有合法动作
    assert engine.legal_actions(st, first) == []


def test_t0043_end_cleanup_removes_damage_and_temp_effects():
    st, first = fresh()
    bf = st.battlefields[0]
    bf.controller = first
    u = place_battlefield_unit(st, first, 0)
    st.obj(u).damage = 2
    st.obj(u).might_temp = 1
    st.obj(u).stunned = True
    from riftsim.enums import Keyword

    st.obj(u).keywords_extra[Keyword.GANKING] = "turn"
    engine.step(st, Action(ActionKind.END_MAIN, first))
    o = st.obj(u)
    assert o.damage == 0 and o.might_temp == 0 and o.stunned is False
    assert Keyword.GANKING not in o.keywords_extra


def test_t0045_cleanup_blocks_play():
    """清理中无行动窗（320）：引擎设计上清理只在 advance 内自动运行，玩家永不可在清理中行动——
    以不变量断言：任何停在决策点的状态，cleanup 已静默（无致命待处理单位）。"""
    from riftsim.cleanup_sys import lethal_marked

    st, first = fresh()
    assert st.current_request is not None
    assert not any(lethal_marked(st, u) for u in st.objects)


def test_illegal_action_no_state_change():
    st, first = fresh()
    from riftsim.snapshot import state_hash

    before = state_hash(st)
    other = 1 - first
    try:
        engine.step(st, Action(ActionKind.END_MAIN, other))  # 非请求玩家
        raise AssertionError("should have raised")
    except IllegalActionError:
        pass
    assert state_hash(st) == before
