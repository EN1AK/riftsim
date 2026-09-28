# 移动/争夺/对决（T-0036/0058..0060/0077..0079/0094/0100）
from riftsim import engine
from riftsim.actions import Action
from riftsim.enums import ActionKind, CardType, DecisionKind, Domain, EventType, Keyword, Phase, Termination, Zone
from tests.helpers import fresh, place_base, place_battlefield_unit


def _give_mobile_unit(st, first, keywords=(), might=2):
    return place_base(st, first, {"def_id": f"t:mv:{st.next_uid}", "name": "机动单位",
                                  "card_types": {CardType.UNIT}, "domains": {Domain.R},
                                  "cost_energy": might, "cost_power": (Domain.R,), "might": might,
                                  "keywords": keywords})


def test_t0077_std_move_and_exhaust_cost():
    st, first = fresh()
    st.battlefields[0].controller = first
    place_battlefield_unit(st, first, 0)  # 维持控制（避免失控）
    uid = _give_mobile_unit(st, first)
    a = next(a for a in engine.legal_actions(st, first)
             if a.kind == ActionKind.STD_MOVE and a.source_uid == uid
             and a.params["to"] == ("battlefield", 0))
    r = engine.step(st, a)
    assert st.obj(uid).zone == Zone.BATTLEFIELD and st.obj(uid).battlefield == 0
    assert st.obj(uid).exhausted is True  # 144.2 费用
    assert any(e["type"] == EventType.MOVE.value for e in r.events)


def test_t0079_crowded_battlefield_illegal():
    st, first = fresh()
    place_battlefield_unit(st, 1 - first, 0)
    place_battlefield_unit(st, 1 - first, 0)
    uid = _give_mobile_unit(st, first)
    la = engine.legal_actions(st, first)
    assert not any(a.kind == ActionKind.STD_MOVE and a.source_uid == uid
                   and a.params["to"] == ("battlefield", 0) for a in la)


def test_t0078_t0036_contest_and_showdown_mode():
    st, first = fresh()
    # 无主战场（控制需单位维持 323.6；无控制者则此前清理后 controller=None）
    bf = st.battlefields[1]
    bf.controller = None
    # P1 单位移入非己方控制战场→争夺→非战斗对决，焦点=P1，四态=对决开环
    uid = _give_mobile_unit(st, first)
    a = next(a for a in engine.legal_actions(st, first)
             if a.kind == ActionKind.STD_MOVE and a.source_uid == uid
             and a.params["to"] == ("battlefield", 1))
    r = engine.step(st, a)
    assert bf.contested is True and bf.contested_by == first
    assert st.showdown_bf == 1 and bf.showdown_active is True
    assert st.focus == first
    assert st.current_request["kind"] == DecisionKind.SHOWDOWN_FOCUS.value
    from riftsim.observation import turn_state
    ts = turn_state(st)
    assert ts["mode"] == "showdown" and ts["link"] == "open"


def test_t0060_showdown_close_unique_survivor_controls():
    st, first = fresh()
    bf = st.battlefields[1]
    bf.controller = None  # 空战场
    uid = _give_mobile_unit(st, first)
    a = next(a for a in engine.legal_actions(st, first)
             if a.kind == ActionKind.STD_MOVE and a.source_uid == uid
             and a.params["to"] == ("battlefield", 1))
    engine.step(st, a)
    assert st.showdown_bf == 1
    # 双方让过对决关闭（T-0058 焦点轮）；P1 唯一留场→确立控制+征服
    engine.step(st, Action(ActionKind.PASS, first))
    engine.step(st, Action(ActionKind.PASS, 1 - first))
    assert st.showdown_bf is None
    assert bf.controller == first
    assert bf.contested is False
    assert st.players[first].score == 1  # 征服（T-0060）


def test_t0094_showdown_close_both_stay_keeps_contest():
    st, first = fresh()
    bf = st.battlefields[1]
    bf.controller = 1 - first
    place_battlefield_unit(st, 1 - first, 1)  # 对方单位在场
    uid = _give_mobile_unit(st, first)
    a = next(a for a in engine.legal_actions(st, first)
             if a.kind == ActionKind.STD_MOVE and a.source_uid == uid
             and a.params["to"] == ("battlefield", 1))
    engine.step(st, a)
    # 有敌单位→战斗 pending 优先（323.10 流程）；先转换或直接开始战斗对决
    # 关闭对决：连续让过
    cur = st.current_request
    assert cur["kind"] in ("showdown_focus", "choose_battlefield_next")
    if cur["kind"] == "showdown_focus":
        engine.step(st, Action(ActionKind.PASS, cur["player"]))
        cur2 = st.current_request
        if cur2 and cur2["kind"] == "showdown_focus":
            engine.step(st, Action(ActionKind.PASS, cur2["player"]))
    # 战斗对决已转化为战斗（10a 或项10），此时 combat 已启动或对决仍在
    # 该战场双方仍在→战斗进行中；此处只断言未确立控制
    assert bf.controller == 1 - first


def test_t0100_move_cleanup_lethal():
    st, first = fresh()
    st.battlefields[0].controller = first
    u_guard = place_battlefield_unit(st, first, 0)
    st.obj(u_guard).damage = 5  # 致命标记待清理（伤害≥战力）
    uid = _give_mobile_unit(st, first)
    a = next(a for a in engine.legal_actions(st, first)
             if a.kind == ActionKind.STD_MOVE and a.source_uid == uid)
    engine.step(st, a)
    # 移动完成即清理（453）：守位单位被摧毁
    assert st.obj(u_guard).zone == Zone.TRASH
