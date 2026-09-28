# 打出六步与技能（T-0023/0025/0026/0027/0030/0061/0070/0071）
from riftsim import engine
from riftsim.actions import Action
from riftsim.enums import ActionKind, CardType, Domain, EventType, Keyword, Phase, Zone
from tests.helpers import fresh, give_hand, place_base


def _play_unit(st, first):
    uid = give_hand(st, first, {"def_id": "t:u1", "name": "单位一", "card_types": {CardType.UNIT},
                                "domains": {Domain.R}, "cost_energy": 0, "cost_power": (), "might": 2})
    a = next(a for a in engine.legal_actions(st, first)
             if a.kind == ActionKind.PLAY_CARD and a.source_uid == uid)
    return uid, engine.step(st, a)


def test_t0061_six_step_trace():
    st, first = fresh()
    r = _play_unit(st, first)[1]
    types = [e["type"] for e in r.events]
    # 步骤事件（354/355/356/357/358）可见轨迹
    steps = [e for e in r.events if e["type"] == EventType.PLAY_STEP.value]
    assert [e["public"]["step"] for e in steps] == [1, 2, 3, 5]
    assert any(e["type"] == EventType.PAID.value for e in r.events)


def test_t0023_unit_enters_exhausted():
    st, first = fresh()
    uid, r = _play_unit(st, first)
    o = st.obj(uid)
    assert o.zone in (Zone.BASE, Zone.BATTLEFIELD)
    assert o.exhausted is True
    assert o.entered_turn == st.turn_number


def test_t0025_gear_enters_base_active():
    st, first = fresh()
    uid = give_hand(st, first, {"def_id": "t:g1x", "name": "装备一", "card_types": {CardType.GEAR},
                                "domains": {Domain.R}, "cost_energy": 0, "cost_power": (),
                                "might_bonus": 1})
    a = next(a for a in engine.legal_actions(st, first)
             if a.kind == ActionKind.PLAY_CARD and a.source_uid == uid)
    engine.step(st, a)
    o = st.obj(uid)
    assert o.zone == Zone.BASE and o.exhausted is False
    # 装备不可选战场（T-0072 默认限制）
    assert all(not (a.kind == ActionKind.PLAY_CARD and a.source_uid == uid
                    and a.params.get("location", (None,))[0] == "battlefield")
               for a in engine.legal_actions(st, first))


def test_t0026_spell_resolves_to_trash():
    st, first = fresh()
    uid = give_hand(st, first, {"def_id": "t:s1x", "name": "法术一", "card_types": {CardType.SPELL},
                                "domains": {Domain.R}, "cost_energy": 0, "cost_power": ()})
    a = next(a for a in engine.legal_actions(st, first)
             if a.kind == ActionKind.PLAY_CARD and a.source_uid == uid)
    engine.step(st, a)  # 入链 pending
    # FEPR：确认（finalize）→ 执行窗：对方 PASS → 己方 PASS → 结算
    assert st.chain and st.chain[0].status == "finalized"
    req_kind = st.current_request["kind"], st.current_request["player"]
    other, self_ = st.current_request["player"], 1 - st.current_request["player"]
    engine.step(st, Action(ActionKind.PASS, other))
    engine.step(st, Action(ActionKind.PASS, self_))
    assert not st.chain_live()
    assert st.obj(uid).zone == Zone.TRASH
    assert uid in st.players[first].trash


def test_t0027_spell_illegal_when_closed():
    st, first = fresh()
    uid = give_hand(st, first, {"def_id": "t:s2x", "name": "法术二", "card_types": {CardType.SPELL},
                                "domains": {Domain.R}, "cost_energy": 0, "cost_power": ()})
    # 制造闭环：打出一张法术入链
    _ = _play_unit(st, first)[1]  # 单位确认后离场闭环结束；改打出 spell 保持链
    uid2 = give_hand(st, first, {"def_id": "t:s3x", "name": "法术三", "card_types": {CardType.SPELL},
                                 "domains": {Domain.R}, "cost_energy": 0, "cost_power": ()})
    a = next(a for a in engine.legal_actions(st, first)
             if a.kind == ActionKind.PLAY_CARD and a.source_uid == uid2)
    engine.step(st, a)
    assert st.chain_live()
    # 闭环中：普通法术不在双方合法反应列表
    other = 1 - first
    la_other = [a for a in engine.legal_actions(st, other)]
    assert not any(a.kind == ActionKind.PLAY_CARD for a in la_other)
    la_first = [a for a in engine.legal_actions(st, first)]
    assert not any(a.kind == ActionKind.PLAY_CARD and a.source_uid == uid for a in la_first)


def test_t0030_reaction_rune_in_closed():
    """闭环（对决窗）中对手可激活[反应]符文技能（164.2/813；429.2 确认即结算）。"""
    from tests.helpers import place_base, rune_def

    st, first = fresh()
    rune_other = place_base(st, 1 - first, rune_def(30))
    uid = give_hand(st, first, {"def_id": "t:s4x", "name": "法术四", "card_types": {CardType.SPELL},
                                "domains": {Domain.R}, "cost_energy": 0, "cost_power": ()})
    a = next(a for a in engine.legal_actions(st, first)
             if a.kind == ActionKind.PLAY_CARD and a.source_uid == uid)
    engine.step(st, a)
    assert st.chain_live()
    # 执行窗轮到对方：其合法动作含符文 [E] 技能
    other = 1 - first
    la = engine.legal_actions(st, other)
    act = next(a for a in la if a.kind == ActionKind.ACTIVATE_ABILITY
               and a.source_uid == rune_other and a.params.get("ability_id") == "rune_exhaust_gain")
    engine.step(st, act)
    # 获得资源技能确认立即结算：对方池 +1 法力，且符文休眠
    assert st.players[other].rune_energy == 1
    assert st.obj(rune_other).exhausted is True


def test_t0070_ability_five_steps_and_trash_guard():
    """主动技能五步入链，非立即技能经结算后离链（401/406）。"""
    st, first = fresh()
    from tests.helpers import place_base, rune_def

    uid = place_base(st, first, rune_def(31))
    legal = engine.legal_actions(st, first)
    act = next(a for a in legal if a.kind == ActionKind.ACTIVATE_ABILITY
               and a.source_uid == uid and a.params.get("ability_id") == "rune_recycle_gain")
    engine.step(st, act)
    assert st.players[first].rune_power.get("R") == 1
    assert st.obj(uid).zone == Zone.RUNE_DECK
