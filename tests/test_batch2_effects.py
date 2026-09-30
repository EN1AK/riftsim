# 批次 2 效果/P1 关键词接线集成测试（阶段 4-b/c；真实卡库 def × tests/helpers 脚手架）
# 规则锚点：
#   805.1.a/805.1.a.1/805.1.a.2 急速（可选附加费 [1]+[C]/[A]，活跃进场）
#   807.1.d.1/814.1.d.1 强攻/坚守（身份期内战力 ±X；465.2.c 伤害池与致少口径）
#   809.1.c/809.1.c.1/356.2.a.2 法盾（强制附加费 [A]，任意特性符能可付）
#   816.1.b/816.1.c 瞬息（控制者开始阶段计分前摧毁）
#   817.1.b/817.2.a/436.1/436.4.a 预知→洞察（看顶+可选回收，不燃尽）
#   822.1.b/813.4/822.3 伏击（有己方单位战场的位置选项 + 条件 [反应]；190.3.a.1 争夺）
#   170.11.c 开放战场位置选项；413.1 抽牌；417.1 伤害；359.3.e.9 目标失效
from pathlib import Path

import pytest

from riftsim import engine, playing
from riftsim.actions import Action
from riftsim.carddb import load_card_db
from riftsim.enums import ActionKind, CardType, DecisionKind, Domain, Keyword, Zone
from riftsim.errors import IllegalActionError
from riftsim.objects import GameObject
from riftsim.resources import effective_might
from riftsim.snapshot import restore, snapshot, state_hash
from tests.helpers import fresh, place_base, place_battlefield_unit

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "cards_bilingual.db"

pytestmark = pytest.mark.skipif(not DB.exists(), reason="cards_bilingual.db 不在仓库根目录")

SPELL_DMG = "OGN-009"     # 法术：对战场上的一名单位造成3点伤害
SPELL_DMG_BIG = "OGN-085"  # 法术：造成6点伤害
GEAR_FURY = "OGN-040"     # 装备：[E]—[反应] 获得 [红]
ENTERS_READY = "SFD-006"  # 单位：我以活跃状态进场
ACCELERATE = "OGN-001"    # 单位：[急速]
ASSAULT2 = "UNL-002"      # 单位：[伏击][强攻2]
SHIELD = "OGN-052"        # 单位：[坚守]
DEFLECT = "OGN-013"       # 单位：[法盾]
DEFLECT2 = "OGN-041"      # 单位：[法盾2]
VISION = "OGN-171"        # 单位：[预知]
TEMPORARY = "OGN-274"     # 单位：[瞬息]
OPEN_BF = "OGN-176"       # 单位：你可以将我打出到一处开放的战场
NO_COMBAT = "UNL-171"     # 单位：[法盾][壁垒] 我无法造成战斗伤害
ON_PLAY_DRAW = "VEN-048"  # 单位：当你打出我时，抽一张牌
SPELL_DRAW = "SFD-076"    # 法术：抽一张牌
EXTRA_COST = "SFD-098"    # 单位：你可以选择支付{{1}}作为额外费用（后续效果行仍白名单外）


@pytest.fixture(scope="module")
def real_defs():
    return load_card_db(str(DB)).defs


def _register(st, real_defs, key):
    """真卡 def 注入注册表（绕过组卡界线；管线正确性由 carddb 解析测试覆盖）。"""
    d = real_defs[key]
    st.card_registry[d.def_id] = d
    return d


def _give(st, player: int, def_id: str, zone: Zone, **kw) -> int:
    assert def_id in st.card_registry, def_id
    uid = st.new_uid()
    st.objects[uid] = GameObject(
        uid=uid, def_id=def_id, owner=player, controller=player,
        zone=zone, zone_owner=player if zone != Zone.BATTLEFIELD else None, **kw)
    if zone == Zone.HAND:
        st.players[player].hand.append(uid)
    elif zone == Zone.BASE:
        st.base_occupants[player].append(uid)
    return uid


def _fund(st, player: int, d, extra: int = 0) -> None:
    """按其特性配域给足符文（[E] 产法力、回收产符能；357.1.a 支付窗自动激活）。"""
    from tests.helpers import rune_def, place_base as _pb
    dom = next(iter(d.domains)) if d.domains else Domain.R
    for i in range(d.cost_energy + len(d.cost_power) + extra):
        rd = dict(rune_def(f"{player}:{d.def_id}:{i}", domain=dom))
        _pb(st, player, rd)


def _pass_chain(st) -> list[dict]:
    evs: list[dict] = []
    while st.chain_live():
        r = engine.step(st, Action(ActionKind.PASS, st.current_request["player"]))
        evs.extend(r.events)
    return evs


def _plays(st, player: int, uid: int):
    return [a for a in engine.legal_actions(st, player)
            if a.kind == ActionKind.PLAY_CARD and a.source_uid == uid]


# ---------------------------------------------------------------- h) 法术直伤：目标枚举/结算/失效
def test_spell_damage_target_enum_and_resolve(real_defs):
    st, first = fresh()
    d = _register(st, real_defs, SPELL_DMG)
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    t0 = place_battlefield_unit(st, 1 - first, 0, might=3)
    t1 = place_battlefield_unit(st, 1 - first, 1, might=3)
    plays = _plays(st, first, uid)
    assert plays and all(a.params.get("target") in (t0, t1) for a in plays)
    assert {a.params["target"] for a in plays} == {t0, t1}  # 355.6 目标逐一枚举
    r = engine.step(st, next(a for a in plays if a.params["target"] == t0))
    paid = next(e for e in r.events if e["type"] == "PAID")
    assert paid["public"]["energy"] == d.cost_energy
    evs = _pass_chain(st)
    dmg = next(e for e in evs if e["type"] == "DAMAGE")
    assert dmg["public"]["uid"] == t0 and dmg["public"]["amount"] == 3
    assert "R-CR-417.1" in dmg["rule_ids"]
    assert st.obj(uid).zone == Zone.TRASH  # 157.1 结算后废牌堆
    assert st.obj(t0).zone == Zone.TRASH  # 3 伤=致命（323.5 清理摧毁）


def test_spell_damage_fizzle_when_target_left(real_defs):
    """目标结算时已不在范围 → 伤害指示不执行（359.3.e.9），法术仍入废牌堆。"""
    st, first = fresh()
    d = _register(st, real_defs, SPELL_DMG)
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    tgt = place_battlefield_unit(st, 1 - first, 0, might=9)
    engine.step(st, next(a for a in _plays(st, first, uid) if a.params["target"] == tgt))
    st.battlefields[0].occupants.remove(tgt)  # 响应中态：目标离场（最小模拟）
    o = st.obj(tgt)
    o.zone, o.zone_owner, o.battlefield = Zone.TRASH, 1 - first, None
    st.players[1 - first].trash.append(tgt)
    evs = _pass_chain(st)
    assert not any(e["type"] == "DAMAGE" for e in evs)
    fiz = next(e for e in evs if "R-CR-359.3.e.9" in e["rule_ids"])
    assert fiz["public"]["fizzle"] == "target_invalid"
    assert st.obj(uid).zone == Zone.TRASH


def test_spell_damage_out_of_scope_target_rejected(real_defs):
    """基地中的单位不在 unit_at_battlefield 范围（355.6）：手工提交拒绝且状态不变。"""
    st, first = fresh()
    d = _register(st, real_defs, SPELL_DMG)
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    base_unit = place_base(st, 1 - first, {"def_id": "t:u:base", "name": "基地单位",
                                           "card_types": {CardType.UNIT}, "might": 2,
                                           "cost_energy": 2, "cost_power": (Domain.R,)})
    assert all(a.params.get("target") != base_unit for a in _plays(st, first, uid))
    illegal = Action(ActionKind.PLAY_CARD, first, uid,
                     {"in_reaction": False, "target": base_unit})
    h_before = state_hash(st)
    with pytest.raises(IllegalActionError):
        engine.step(st, illegal)  # 第一层：合法集成员资格（334/358）
    assert state_hash(st) == h_before
    with pytest.raises(IllegalActionError, match=r"355\.6"):
        playing.handle_play_card(st, illegal)  # 第二层：处理器步骤 2 目标预检锚点
    assert state_hash(st) == h_before
    assert uid in st.players[first].hand


# ---------------------------------------------------------------- i/j) 抽牌效果：法术抽牌 / 打出触发抽牌
def test_spell_draw_resolves(real_defs):
    st, first = fresh()
    d = _register(st, real_defs, SPELL_DRAW)
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    before = len(st.players[first].hand)
    engine.step(st, _plays(st, first, uid)[0])
    evs = _pass_chain(st)
    draws = [e for e in evs if e["type"] == "DRAW" and "R-CR-413.1" in e["rule_ids"]]
    assert draws and draws[0]["public"]["count"] == d.abilities[0].draw_count == 1
    assert len(st.players[first].hand) == before  # 打出 -1 / 抽牌 +1


def test_on_play_draw_trigger_after_enter(real_defs):
    """常驻确认先入链结算进场（337.2），「打出我时」触发再上链（383.1）；结算抽 1。"""
    st, first = fresh()
    d = _register(st, real_defs, ON_PLAY_DRAW)
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    before = len(st.players[first].hand)
    r = engine.step(st, next(a for a in _plays(st, first, uid)
                             if a.params.get("location", ("base",))[0] == "base"))
    assert st.obj(uid).zone == Zone.BASE  # 337.2 常驻确认即进场
    assert st.chain_live()  # 触发仍在链上（可被反应，327）
    evs = _pass_chain(st)
    draws = [e for e in evs + r.events if e["type"] == "DRAW" and "R-CR-413.1" in e["rule_ids"]]
    assert draws
    assert len(st.players[first].hand) == before


# ---------------------------------------------------------------- f) 活跃进场
def test_enters_ready_overrides_default_exhaust(real_defs):
    st, first = fresh()
    d = _register(st, real_defs, ENTERS_READY)
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    r = engine.step(st, next(a for a in _plays(st, first, uid)
                             if a.params.get("location", ("base",))[0] == "base"))
    res = next(e for e in r.events if e["type"] == "RESOLVE" and e["public"].get("entered"))
    assert st.obj(uid).exhausted is False
    assert res["public"]["exhausted"] is False


def test_default_unit_enters_exhausted_contrast(real_defs):
    st, first = fresh()
    uid = place_base(st, first, {"def_id": "t:u:plain", "name": "普通单位", "card_types": {CardType.UNIT},
                                 "cost_energy": 2, "cost_power": (Domain.R,), "might": 2})
    from tests.helpers import rune_def
    for i in range(3):
        place_base(st, first, rune_def(f"r{i}"))
    st.players[first].hand.append(uid)
    o = st.obj(uid)
    o.zone, o.zone_owner, o.battlefield = Zone.HAND, first, None
    st.base_occupants[first].remove(uid)
    r = engine.step(st, next(a for a in _plays(st, first, uid)
                             if a.params.get("location", ("base",))[0] == "base"))
    assert st.obj(uid).exhausted is True  # 359.2.c 默认休眠


# ---------------------------------------------------------------- 805 急速
def test_accelerate_variant_cost_and_ready(real_defs):
    st, first = fresh()
    d = _register(st, real_defs, ACCELERATE)
    assert set(d.domains) == {Domain.R}, "单特性样本（多特性变体 MVP 暂缓，805.1.a.1）"
    _fund(st, first, d, extra=2)
    uid = _give(st, first, d.def_id, Zone.HAND)
    plays = _plays(st, first, uid)
    accel = [a for a in plays if a.params.get("accelerate") is True]
    base = [a for a in plays if not a.params.get("accelerate")]
    assert accel and base  # 可选手续两分支都枚举（805.1.a「可以选择」）
    r = engine.step(st, next(a for a in accel if a.params["location"][0] == "base"))
    paid = next(e for e in r.events if e["type"] == "PAID")
    assert paid["public"]["energy"] == d.cost_energy + 1
    assert paid["public"]["power"].get("R", 0) == len(d.cost_power) + 1  # [C]=特性匹配（805.1.a.1）
    res = next(e for e in r.events if e["type"] == "RESOLVE" and e["public"].get("entered"))
    assert st.obj(uid).exhausted is False  # 活跃进场
    assert "R-CR-805.1.a" in res["rule_ids"]


def test_accelerate_not_offered_without_keyword(real_defs):
    st, first = fresh()
    uid = place_battlefield_unit(st, first, 0)  # 任意非手牌干扰
    plain = _give(st, first, "sk:unit:u2:1", Zone.HAND)
    assert all(not a.params.get("accelerate") for a in _plays(st, first, plain))
    # 手工构造 accelerate 参数的防御：无关键词即非法
    illegal = Action(ActionKind.PLAY_CARD, first, plain,
                     {"location": ("base", first), "in_reaction": False, "accelerate": True})
    with pytest.raises(IllegalActionError, match=r"805"):
        playing.handle_play_card(st, illegal)


# ---------------------------------------------------------------- 807/814 战斗身份战力
def test_assault_adds_attacker_pool(real_defs):
    st, first = fresh()
    d = _register(st, real_defs, ASSAULT2)
    atk = _give(st, first, d.def_id, Zone.BATTLEFIELD, battlefield=1)
    st.battlefields[1].occupants.append(atk)
    bf = st.battlefields[1]
    bf.controller = 1 - first
    bf.contested, bf.contested_by = True, first
    place_battlefield_unit(st, 1 - first, 1, might=2)
    from riftsim import combat
    combat.start_combat(st, bf)
    combat.showdown_closed(st, bf)
    pool = bf.combat.pool
    assert pool == effective_might(st, atk) + 2  # 强攻2（807.1.d.1 进攻身份）
    assert effective_might(st, atk, role="attacker") == effective_might(st, atk) + 2


def test_shield_adds_defender_pool_and_cap(real_defs):
    st, first = fresh()
    d = _register(st, real_defs, SHIELD)
    bf = st.battlefields[1]
    bf.controller = 1 - first
    df = _give(st, 1 - first, d.def_id, Zone.BATTLEFIELD, battlefield=1)
    bf.occupants.append(df)
    place_battlefield_unit(st, first, 1, might=3, name="攻")
    bf.contested, bf.contested_by = True, first
    from riftsim import combat
    combat.start_combat(st, bf)
    combat.showdown_closed(st, bf)
    # 进攻方分配后切防守方
    assign_atk = next(a for a in engine.legal_actions(st, first)
                      if a.kind == ActionKind.ASSIGN_DAMAGE)
    engine.step(st, assign_atk)
    req = st.current_request
    assert req["options"]["side"] == 1 - first
    assert req["options"]["pool"] == effective_might(st, df) + 1  # 坚守（814.1.d.1）
    # 防守方致少口径含坚守：攻方 3 战力 vs 守方（2+1）→ 致命需 3
    assert effective_might(st, df, role="defender") == effective_might(st, df) + 1


def test_no_combat_damage_excluded_from_pool(real_defs):
    st, first = fresh()
    d = _register(st, real_defs, NO_COMBAT)
    u = _give(st, first, d.def_id, Zone.BATTLEFIELD, battlefield=1)
    st.battlefields[1].occupants.append(u)
    place_battlefield_unit(st, first, 1, might=2, name="攻2")
    bf = st.battlefields[1]
    bf.controller = 1 - first
    bf.contested, bf.contested_by = True, first
    place_battlefield_unit(st, 1 - first, 1, might=2)
    from riftsim import combat
    combat.start_combat(st, bf)
    combat.showdown_closed(st, bf)
    assert bf.combat.pool == 2  # UNL-171（might=2）被排除（卡面「无法造成战斗伤害」）


def test_last_damage_assigned_last(real_defs):
    """「最后承担伤害」与后排同级（465.2.c.6）：其它单位未致少前不得为其分配。"""
    st, first = fresh()
    from riftsim.cards import AbilityDef
    from tests.helpers import spawn_card
    last_d = {"def_id": "t:last", "name": "最后", "card_types": {CardType.UNIT},
              "might": 2, "cost_energy": 2, "cost_power": (Domain.R,),
              "abilities": (AbilityDef(ability_id="t:last:0", kind="last_damage", timing="passive"),)}
    bf = st.battlefields[1]
    bf.controller = 1 - first
    last_u = spawn_card(st, last_d, 1 - first, Zone.BATTLEFIELD, battlefield=1)
    bf.occupants.append(last_u)
    normal = place_battlefield_unit(st, 1 - first, 1, might=2, name="守普")
    place_battlefield_unit(st, first, 1, might=3, name="攻")
    bf.contested, bf.contested_by = True, first
    from riftsim import combat
    combat.start_combat(st, bf)
    combat.showdown_closed(st, bf)
    assigns = [a for a in engine.legal_actions(st, first)
               if a.kind == ActionKind.ASSIGN_DAMAGE]
    assert assigns
    for a in assigns:
        plan = a.params["assign"]
        if plan.get(last_u, 0) > 0:
            assert plan.get(normal, 0) >= 2  # 普通单位须先达致少


# ---------------------------------------------------------------- 809 法盾
def test_deflect_adds_any_domain_power_cost(real_defs):
    st, first = fresh()
    sd = _register(st, real_defs, SPELL_DMG)
    dd = _register(st, real_defs, DEFLECT)
    _fund(st, first, sd, extra=1)  # [A] 附加费需多一枚可回收符文（809.1.c.1 任意特性可付）
    uid = _give(st, first, sd.def_id, Zone.HAND)
    tgt = _give(st, 1 - first, dd.def_id, Zone.BATTLEFIELD, battlefield=0)
    st.battlefields[0].occupants.append(tgt)
    r = engine.step(st, next(a for a in _plays(st, first, uid) if a.params["target"] == tgt))
    paid = next(e for e in r.events if e["type"] == "PAID")
    assert paid["public"]["power"].get("A", 0) == 1  # 809.1.c 强制附加（356.2.a.2）


def test_deflect2_stacks(real_defs):
    st, first = fresh()
    sd = _register(st, real_defs, SPELL_DMG_BIG)
    dd = _register(st, real_defs, DEFLECT2)
    _fund(st, first, sd, extra=2)
    uid = _give(st, first, sd.def_id, Zone.HAND)
    tgt = _give(st, 1 - first, dd.def_id, Zone.BATTLEFIELD, battlefield=0)
    st.battlefields[0].occupants.append(tgt)
    d = real_defs[DEFLECT2]
    assert d.keyword_values.get("deflect") == 2
    r = engine.step(st, next(a for a in _plays(st, first, uid) if a.params["target"] == tgt))
    paid = next(e for e in r.events if e["type"] == "PAID")
    assert paid["public"]["power"].get("A", 0) == 2


def test_friendly_target_no_deflect(real_defs):
    """法盾只加诸对手控制的单位（809.1.c）：以己方单位为目标不产生附加费。"""
    st, first = fresh()
    sd = _register(st, real_defs, SPELL_DMG)
    dd = _register(st, real_defs, DEFLECT)
    _fund(st, first, sd)
    uid = _give(st, first, sd.def_id, Zone.HAND)
    friendly = _give(st, first, dd.def_id, Zone.BATTLEFIELD, battlefield=0)
    st.battlefields[0].occupants.append(friendly)
    r = engine.step(st, next(a for a in _plays(st, first, uid) if a.params["target"] == friendly))
    paid = next(e for e in r.events if e["type"] == "PAID")
    assert "A" not in paid["public"]["power"]


# ---------------------------------------------------------------- 822 伏击 / 开放战场 / 争夺
def test_ambush_location_option_and_contest(real_defs):
    st, first = fresh()
    d = _register(st, real_defs, ASSAULT2)  # UNL-002 [伏击]
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    bf = st.battlefields[1]
    bf.controller = 1 - first  # 敌方控制战场
    place_battlefield_unit(st, first, 1, might=2, name="己方在场")  # 有己方单位
    bf.contested, bf.contested_by = True, first
    plays = _plays(st, first, uid)
    assert any(a.params.get("location") == ("battlefield", 1) for a in plays)  # 822.1.b 位置选项
    engine.step(st, next(a for a in plays if a.params["location"] == ("battlefield", 1)))
    assert st.obj(uid).zone == Zone.BATTLEFIELD and st.obj(uid).battlefield == 1


def test_ambush_reaction_play_during_closed_chain(real_defs):
    """闭环中无印刷 [反应]：仅允许向有己方单位的战场伏击（813.4），基地选项不出现。"""
    st, first = fresh()
    d = _register(st, real_defs, ASSAULT2)
    _fund(st, 1 - first, d)
    amb = _give(st, 1 - first, d.def_id, Zone.HAND)
    # 敌方战场 1：玩家 1-first 有己方单位（敌方控制）
    bf = st.battlefields[1]
    bf.controller = first
    place_battlefield_unit(st, 1 - first, 1, might=2, name="己方在场")
    # 造一个闭环：first 打出骨架法术
    spell = _give(st, first, "sk:spell:s1:1", Zone.HAND)
    place_base(st, first, {"def_id": "t:rune:x", "name": "r", "card_types": {CardType.RUNE},
                           "domains": {Domain.R}, "abilities": ()})
    from tests.helpers import rune_def
    place_base(st, first, rune_def("rx1"))
    engine.step(st, next(a for a in _plays(st, first, spell)))
    assert st.chain_live()
    # 对方执行窗：能列出伏击动作（仅向有己方单位的战场）
    req = st.current_request
    assert req["player"] == 1 - first
    legal = engine.legal_actions(st, 1 - first)
    amb_plays = [a for a in legal if a.kind == ActionKind.PLAY_CARD and a.source_uid == amb]
    assert amb_plays, "伏击应在闭环给出反应式打出选项（813.4.a）"
    assert all(a.params.get("location") == ("battlefield", 1) for a in amb_plays)


def test_ambush_step5_recheck_rejects_empty_location():
    """822.3：步骤 5 复核时位置已无己方单位 → 非法。"""
    st, first = fresh()
    d = dict(def_id="t:amb", name="伏击单位", card_types={CardType.UNIT}, might=2,
             cost_energy=2, cost_power=(Domain.R,), keywords={Keyword.AMBUSH})
    from tests.helpers import rune_def, spawn_card
    uid = spawn_card(st, d, first, Zone.HAND)
    st.players[first].hand.append(uid)
    for i in range(3):
        place_base(st, first, rune_def(f"rr{i}"))
    bf = st.battlefields[1]
    bf.controller = 1 - first  # 敌方控制、此刻空无单位（822.3 不满足）
    act = Action(ActionKind.PLAY_CARD, first, uid,
                 {"location": ("battlefield", 1), "in_reaction": False})
    with pytest.raises(IllegalActionError, match=r"822"):
        playing.handle_play_card(st, act)


def test_open_battlefield_option_and_contest(real_defs):
    st, first = fresh()
    d = _register(st, real_defs, OPEN_BF)
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    bf_open = next(bf for bf in st.battlefields if bf.controller is None and not bf.occupants)
    idx = bf_open.index  # 开放=未占领且未受控制（170.11.a/c）
    plays = _plays(st, first, uid)
    assert any(a.params.get("location") == ("battlefield", idx) for a in plays)
    r = engine.step(st, next(a for a in plays if a.params["location"] == ("battlefield", idx)))
    assert st.obj(uid).battlefield == idx
    # 190.3.a.1：打出到非控战场 → 战场进入争夺
    assert bf_open.contested and bf_open.contested_by == first
    assert any(e["type"] == "CONTEST" and "R-CR-190.3.a.1" in e["rule_ids"] for e in r.events)
    # 有敌单位占据的未控制战场不属开放
    st2, first2 = fresh()
    _register(st2, real_defs, OPEN_BF)
    _fund(st2, first2, d)
    uid2 = _give(st2, first2, d.def_id, Zone.HAND)
    place_battlefield_unit(st2, 1 - first2, 1, might=1)
    st2.battlefields[1].controller = None
    assert all(a.params.get("location") != ("battlefield", 1) for a in _plays(st2, first2, uid2))


# ---------------------------------------------------------------- 817 预知 → 洞察
def test_vision_scout_keep_and_recycle(real_defs):
    st, first = fresh()
    d = _register(st, real_defs, VISION)
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    top = st.players[first].main_deck[-1]
    engine.step(st, next(a for a in _plays(st, first, uid)
                         if a.params.get("location", ("base",))[0] == "base"))
    _pass_chain(st)  # 触发结算 → 洞察请求（817.1.b/436.1）
    req = st.current_request
    assert req["kind"] == DecisionKind.SCOUT_KEEP.value
    assert req["player"] == first
    assert req["options"]["uids"] == [top]
    # 对手观察不得透视（隐藏信息隔离；observation 请求过滤）
    opp_view = engine.observe(st, 1 - first)
    assert "uids" not in (opp_view["request"]["options"] or {})
    legal = engine.legal_actions(st, first)
    choices = {a.params.get("choice") for a in legal if a.kind == ActionKind.RESOLVE_CHOICE}
    assert choices == {"keep", "recycle"}  # 817.2.a 每次可选回收或不回收
    engine.step(st, next(a for a in legal if a.params.get("choice") == "keep"))
    assert st.players[first].main_deck[-1] == top  # keep：留顶（817.2.b）

    # 回收路径
    st2, first2 = fresh()
    _register(st2, real_defs, VISION)
    _fund(st2, first2, d)
    uid2 = _give(st2, first2, d.def_id, Zone.HAND)
    top2 = st2.players[first2].main_deck[-1]
    bottom_before = st2.players[first2].main_deck[0] if len(st2.players[first2].main_deck) > 1 else None
    engine.step(st2, next(a for a in _plays(st2, first2, uid2)
                          if a.params.get("location", ("base",))[0] == "base"))
    _pass_chain(st2)
    legal2 = engine.legal_actions(st2, first2)
    engine.step(st2, next(a for a in legal2 if a.params.get("choice") == "recycle"))
    deck = st2.players[first2].main_deck
    assert deck[0] == top2 and deck[-1] != top2  # 回收置于牌堆底（436.1）
    assert bottom_before != top2


def test_vision_scout_empty_deck_no_burnout(real_defs):
    """牌堆空 → 尽可能多地洞察（436.4），不发生燃尽（436.4.a），无决策点。"""
    st, first = fresh()
    d = _register(st, real_defs, VISION)
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    st.players[first].main_deck = []
    r = engine.step(st, next(a for a in _plays(st, first, uid)
                             if a.params.get("location", ("base",))[0] == "base"))
    evs = _pass_chain(st)
    assert not any(e["type"] == "BURNOUT" for e in r.events + evs)
    assert st.current_request is None or st.current_request["kind"] != DecisionKind.SCOUT_KEEP.value


# ---------------------------------------------------------------- 816 瞬息
def test_temporary_destroyed_before_scoring(real_defs):
    st, first = fresh()
    d = _register(st, real_defs, TEMPORARY)
    # 由先手玩家 END_MAIN → 对手回合开始阶段触发其 [瞬息]
    tmp = _give(st, 1 - first, d.def_id, Zone.BATTLEFIELD, battlefield=0)
    st.battlefields[0].occupants.append(tmp)
    st.battlefields[0].controller = 1 - first  # 对手据守（验证「计分前」摧毁：杀后不得分）
    r = engine.step(st, Action(ActionKind.END_MAIN, first))
    evs = list(r.events)
    while st.chain_live():
        rr = engine.step(st, Action(ActionKind.PASS, st.current_request["player"]))
        evs.extend(rr.events)
    kill = next(e for e in evs if e["type"] == "KILL" and e["card_ids"] == [f"uid:{tmp}"])
    assert "R-CR-816.1.b" in kill["rule_ids"]
    assert st.obj(tmp).zone == Zone.TRASH
    # 计分在摧毁之后：该战场本回合未为对手产出据守分（单位已无，但据守看控制——断言顺序）
    seq = [i for i, e in enumerate(evs) if e["type"] == "KILL"]
    holds = [i for i, e in enumerate(evs)
             if e["type"] == "SCORE" and e["public"].get("battlefield") == 0
             and e["public"].get("player") == 1 - first]
    # 据守计分看控制权而非单位（469.2）——战场仍受控可得分；断言语义为 KILL 先于任何 SCORE
    all_scores = [i for i, e in enumerate(evs) if e["type"] == "SCORE"]
    assert not all_scores or seq[0] < all_scores[0]


# ---------------------------------------------------------------- d) 装备资源技能
def test_gear_gain_resource_activates_for_domain_power(real_defs):
    st, first = fresh()
    d = _register(st, real_defs, GEAR_FURY)
    uid = _give(st, first, d.def_id, Zone.BASE)  # 活跃布置
    acts = [a for a in engine.legal_actions(st, first)
            if a.kind == ActionKind.ACTIVATE_ABILITY and a.source_uid == uid]
    assert acts and acts[0].params.get("ability_id", "").startswith(f"{GEAR_FURY}:")
    r = engine.step(st, acts[0])
    assert st.obj(uid).exhausted is True  # [E] 费用（414.1）
    execs = [e for e in r.events if e["type"] == "EXECUTE" and e["public"].get("gain_power") == "R"]
    assert execs, "获得 [红] 符能（批次 2-d 句式；429.2 立即结算不经 FEPR 窗）"
    assert st.players[first].rune_power.get("R", 0) == 1
    assert not st.chain_live()  # 立即结算后即离链


# ---------------------------------------------------------------- e) 可选附加费（费用侧；效果行白名单外不猜）
def test_optional_extra_cost_payment_variant(real_defs):
    st, first = fresh()
    d = _register(st, real_defs, EXTRA_COST)
    _fund(st, first, d, extra=1)
    uid = _give(st, first, d.def_id, Zone.HAND)
    plays = _plays(st, first, uid)
    extra = [a for a in plays if a.params.get("pay_extra") is True]
    assert extra, "「可以选择支付」应给出付费变体（355 步骤 2 选择）"
    r = engine.step(st, next(a for a in extra if a.params["location"][0] == "base"))
    paid = next(e for e in r.events if e["type"] == "PAID")
    assert paid["public"]["energy"] == d.cost_energy + 1  # {{1}} 附加
    base = [a for a in plays if not a.params.get("pay_extra")]
    assert base  # 不付费的基础打出仍存在（选择性费用）


# ---------------------------------------------------------------- 快照往返：新字段
def test_snapshot_restores_keyword_values_and_ability_fields(real_defs):
    st, first = fresh()
    d41 = _register(st, real_defs, DEFLECT2)
    d40 = _register(st, real_defs, GEAR_FURY)
    _give(st, first, d41.def_id, Zone.HAND)
    _give(st, first, d40.def_id, Zone.BASE)
    snap = snapshot(st)
    st2 = restore(snap)
    d41r = st2.card_registry[DEFLECT2]
    assert d41r.keyword_values == {"deflect": 2}
    ab = next(a for a in st2.card_registry[GEAR_FURY].abilities if a.kind == "gain_resource")
    assert ab.grant_power_domain == "R" and ab.cost_exhaust_self is True
    assert state_hash(st2) == state_hash(st)
