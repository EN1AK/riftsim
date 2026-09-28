# 战斗三步（T-0083..0093/0086/0087/0088/0089/0091/0092）
from riftsim import engine
from riftsim.actions import Action
from riftsim.enums import ActionKind, DecisionKind, EventType, Keyword, Zone
from tests.helpers import fresh, place_base, place_battlefield_unit


def _mk_unit_def(st, might, keywords=(), name="单位"):
    from riftsim.enums import CardType, Domain

    return {"def_id": f"t:cb:{st.next_uid}", "name": name, "card_types": {CardType.UNIT},
            "domains": {Domain.R}, "cost_energy": might, "cost_power": (Domain.R,),
            "might": might, "keywords": keywords}


def _setup_battle(st, first, def_units_spec, atk_might=3):
    """构造战斗：P2 控制战场 1；守方第 1 单位正常放置（拥挤上限），
    first 一单位移入触发战斗标记，随后以 fixture 注入守方其余单位
    （双方增援分步合法到达的等效终态）；推进至伤害分配请求。"""
    bf = st.battlefields[1]
    bf.controller = 1 - first
    def_uids = []
    m0, kws0 = def_units_spec[0]
    def_uids.append(place_battlefield_unit(st, 1 - first, 1, might=m0, keywords=kws0, name="守"))
    atk_uid = place_base(st, first, _mk_unit_def(st, atk_might, name="攻"))
    a = next(a for a in engine.legal_actions(st, first)
             if a.kind == ActionKind.STD_MOVE and a.source_uid == atk_uid
             and a.params["to"] == ("battlefield", 1))
    engine.step(st, a)
    for (m, kws) in def_units_spec[1:]:
        def_uids.append(place_battlefield_unit(st, 1 - first, 1, might=m, keywords=kws, name="守"))
    # 注入守方增援触发清理（若战斗未起则开战）；再推进对决焦点连续让过至 ASSIGN_DAMAGE
    guard = 0
    while st.current_request and st.current_request["kind"] in (
        DecisionKind.SHOWDOWN_FOCUS.value, DecisionKind.CHOOSE_BATTLEFIELD_NEXT.value
    ):
        guard += 1
        assert guard < 20, "focus loop"
        req = st.current_request
        if req["kind"] == DecisionKind.CHOOSE_BATTLEFIELD_NEXT.value:
            engine.step(st, Action(ActionKind.RESOLVE_CHOICE, req["player"],
                                   params={"battlefield": req["options"]["choices"][0]}))
        else:
            engine.step(st, Action(ActionKind.PASS, req["player"]))
    # 若注入后清理尚未重评（战斗未开），补一次空操作触发：直接断言 combat 已存在
    return bf, atk_uid, def_uids


def _assign_all(state, side, plan):
    return engine.step(state, Action(ActionKind.ASSIGN_DAMAGE, side, params={"assign": plan}))


def test_t0083_t0086_combat_starts_and_attacker_assigns_first():
    st, first = fresh()
    bf, atk, defs = _setup_battle(st, first, [(2, ())], atk_might=3)
    assert bf.combat is not None
    assert bf.combat.attacker == first
    assert bf.combat.defender == 1 - first
    req = st.current_request
    assert req["kind"] == DecisionKind.ASSIGN_DAMAGE.value
    assert req["player"] == first  # 进攻方先分配（T-0086）
    assert req["options"]["pool"] == 3


def test_t0087_lethal_first_then_spillover():
    st, first = fresh()
    # 防守方两单位：均 2/2无伤害；进攻池 3
    bf, atk, defs = _setup_battle(st, first, [(2, ()), (2, ())], atk_might=3)
    legal = engine.legal_actions(st, first)
    assigns = [a for a in legal if a.kind == ActionKind.ASSIGN_DAMAGE]
    assert assigns, "no assignments enumerated"
    for a in assigns:
        plan = a.params["assign"]
        total = sum(plan.values())
        pool = st.current_request["options"]["pool"]
        caps = {u: 2 for u in defs}
        assert total == min(pool, sum(caps.values()))
        # 每目标不超致少
        for u, v in plan.items():
            assert 0 <= v <= caps[u]


def test_t0088_tank_forces_first():
    from riftsim.enums import Keyword

    st, first = fresh()
    bf, atk, defs = _setup_battle(st, first, [(2, (Keyword.TANK,)), (2, ())], atk_might=3)
    tank, normal = defs[0], defs[1]
    legal = engine.legal_actions(st, first)
    assigns = [a for a in legal if a.kind == ActionKind.ASSIGN_DAMAGE]
    assert assigns
    for a in assigns:
        plan = a.params["assign"]
        if plan.get(normal, 0) > 0:
            # 须先为壁垒分配致命（致少 2）后才可分给普通单位
            assert plan.get(tank, 0) >= 2


def test_t0091_defender_survives_attacker_recalled_and_reflag():
    st, first = fresh()
    # 守 3/3、攻 2/2：攻方伤害不足致命；守方击杀攻方? 攻 2 vs 守 3
    bf, atk, defs = _setup_battle(st, first, [(3, ())], atk_might=2)
    # 攻方分配：全给守方（2 < 3 无致命）
    assign_atk = next(a for a in engine.legal_actions(st, first)
                      if a.kind == ActionKind.ASSIGN_DAMAGE)
    engine.step(st, assign_atk)
    # 守方分配：3 点全给攻方（致命 2）
    assign_def = next(a for a in engine.legal_actions(st, 1 - first)
                      if a.kind == ActionKind.ASSIGN_DAMAGE)
    engine.step(st, assign_def)
    # 3b 致命摧毁攻方→防守方唯一留场→确立控制（征服）；3d 无召回（进攻方已死）
    assert st.obj(atk).zone == Zone.TRASH
    assert bf.controller == 1 - first
    assert bf.contested is False
    # 守方单位保留其已受 2 伤已在 3c 清除
    assert all(st.obj(u).damage == 0 for u in defs)


def test_t0092_attacker_wins_and_conquers():
    st, first = fresh()
    bf, atk, defs = _setup_battle(st, first, [(2, ())], atk_might=5)
    assign_atk = next(a for a in engine.legal_actions(st, first)
                      if a.kind == ActionKind.ASSIGN_DAMAGE)
    engine.step(st, assign_atk)
    # 守 2 伤 ≤ 攻池 5 →守方被摧毁；守方反击分配（守已死则跳过分配直接结算）
    if st.current_request and st.current_request["kind"] == DecisionKind.ASSIGN_DAMAGE.value:
        assign_def = next(a for a in engine.legal_actions(st, 1 - first)
                          if a.kind == ActionKind.ASSIGN_DAMAGE)
        engine.step(st, assign_def)
    # 攻方确立控制+征服
    assert bf.controller == first
    assert st.players[first].score >= 1
    assert st.obj(atk).zone.value in ("battlefield", "base")


def test_t0085_assault_trigger_scope_guard():
    """攻守触发每场战斗仅一次（383.4/464.3）——骨架池无触发，此处只验证 combat context 的
    身份字段与重置（466.7）。"""
    st, first = fresh()
    bf, atk, defs = _setup_battle(st, first, [(2, ())], atk_might=5)
    assign_atk = next(a for a in engine.legal_actions(st, first)
                      if a.kind == ActionKind.ASSIGN_DAMAGE)
    engine.step(st, assign_atk)
    if st.current_request and st.current_request["kind"] == DecisionKind.ASSIGN_DAMAGE.value:
        engine.step(st, next(a for a in engine.legal_actions(st, 1 - first)
                             if a.kind == ActionKind.ASSIGN_DAMAGE))
    assert bf.combat is None
    assert bf.showdown_active is False
    assert st.showdown_bf is None
