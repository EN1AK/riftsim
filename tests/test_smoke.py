# 冒烟：模块装配、reset 形状、调度流转、回合推进主循环
from riftsim import engine
from riftsim.config import GameConfig
from riftsim.cards import make_skeleton_deck
from riftsim.enums import ActionKind, DecisionKind, Phase, Zone
from riftsim.actions import Action, DecisionRequest


def cfg() -> GameConfig:
    return GameConfig(decks=(make_skeleton_deck("A", "hero-a"), make_skeleton_deck("B", "hero-b")))


def test_reset_shape_t0007():
    st = engine.reset(42, cfg())
    # 对象数：每侧 传奇1+英雄1+主牌堆40+符文12+战场3（上场与搁置均实例化）=57
    assert len(st.objects) == 57 * 2
    assert len(st.battlefields) == 2
    assert st.current_request["kind"] == DecisionKind.MULLIGAN.value
    # 手牌各 4（R-CR-116）
    assert len(st.players[0].hand) == 4 and len(st.players[1].hand) == 4
    # 传奇/英雄落位（R-CR-111/112）
    for s in (0, 1):
        assert len(st.players[s].legend_zone) == 1
        assert len(st.players[s].hero_zone) == 1
    # 确定性：同 seed 完全同构
    st2 = engine.reset(42, cfg())
    from riftsim.snapshot import state_hash
    assert state_hash(st) == state_hash(st2)


def test_mulligan_flow_t0010_t0012():
    st = engine.reset(42, cfg())
    first = st.meta.config["first_player"]
    legal = engine.legal_actions(st, first)
    assert any(a.kind == ActionKind.RESOLVE_CHOICE for a in legal)
    # 双方 0 张调度 → 进入首回合主阶段
    r = engine.step(st, Action(ActionKind.RESOLVE_CHOICE, first, params={"set_aside": []}))
    assert r.request is not None and r.request.kind == DecisionKind.MULLIGAN
    second = 1 - first
    r = engine.step(st, Action(ActionKind.RESOLVE_CHOICE, second, params={"set_aside": []}))
    assert r.request is not None and r.request.kind == DecisionKind.MAIN_ACTION
    assert st.phase == Phase.MAIN
    assert st.turn_player == first
    # 首回合召出：先手 2 符文（活跃、在基地）
    runes = [u for u in st.base_occupants[first]]
    assert len(runes) == 2
    assert all(not st.obj(u).exhausted for u in runes)
    # 后手首回合召出 3（485 补偿）
    r = engine.step(st, Action(ActionKind.END_MAIN, first))
    assert r.request is not None and r.request.kind == DecisionKind.MAIN_ACTION
    assert st.turn_player == second
    assert len(st.base_occupants[second]) == 3
    # 回合轮转与序号（T-0012）：再走一轮先手续回合
    r = engine.step(st, Action(ActionKind.END_MAIN, second))
    assert st.turn_player == first and st.turn_number == 3
    assert st.phase == Phase.MAIN
