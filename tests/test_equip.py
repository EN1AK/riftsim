# 818 装配（Equip）/ 819 灵便（Quickdraw）接线测试（rq-4 修订版 2026-09-30）：
# 818.1 装配=场上（基地）装备的主动技能（365.1 场上技能惯例+821.1.c.5 同族语义），
# 用户纠正先前「手牌技能」误实现；费用 818.1.c.3；目标 818.1.c.2 你控制的一名单位；
# 818.2/716-719 贴附状态；718.4/137.3.a 战力加成；719.3.a 跟随；719.5 离场卸除。
# 819.1.d 灵便=「[反应]」+「当你打出此牌时，将其贴附于你控制的一名单位上」（打出时触发）。
from pathlib import Path

import pytest

from riftsim import engine
from riftsim.actions import Action
from riftsim.carddb import load_card_db
from riftsim.enums import ActionKind, CardType, Domain, Zone
from riftsim.objects import GameObject
from riftsim.resources import effective_might, kill
from tests.helpers import fresh, place_battlefield_unit, place_base, rune_def

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "cards_bilingual.db"

pytestmark = pytest.mark.skipif(not DB.exists(), reason="cards_bilingual.db 不在仓库根目录")

EQUIP_GEAR = "UNL-019"   # 枯萎战斧：{{装配}}{{1}}{{红色}}
QUICKDRAW_GEAR = "SFD-022"  # 长剑：{{灵便}}+{{装配}}{{红}}（319→819 为我方单位贴附触发）


@pytest.fixture(scope="module")
def real_defs():
    return load_card_db(str(DB)).defs


def _register(st, defs, def_id):
    d = defs[def_id]
    st.card_registry[d.def_id] = d
    return d


def _give(st, player, def_id, zone=Zone.HAND):
    uid = st.new_uid()
    st.objects[uid] = GameObject(
        uid=uid, def_id=def_id, owner=player, controller=player,
        zone=zone, zone_owner=player if zone != Zone.BATTLEFIELD else None)
    if zone == Zone.HAND:
        st.players[player].hand.append(uid)
    return uid


def _place_gear_base(st, player, def_id, *, exhausted=False):
    """装备已在基地（打出完成后状态）：装配/灵便测试的场上源。"""
    uid = st.new_uid()
    st.objects[uid] = GameObject(
        uid=uid, def_id=def_id, owner=player, controller=player,
        zone=Zone.BASE, zone_owner=player, exhausted=exhausted)
    st.base_occupants[player].append(uid)
    return uid


def _fund(st, player, d, extra=0):
    dom = next(iter(d.domains)) if d.domains else Domain.R
    for i in range(d.cost_energy + len(d.cost_power) + extra):
        place_base(st, player, dict(rune_def(f"{player}:{d.def_id}:{i}", domain=dom)))


def _equip_acts(st, player, uid):
    return [a for a in engine.legal_actions(st, player)
            if a.kind == ActionKind.ACTIVATE_ABILITY and a.source_uid == uid
            and a.params.get("ability_id", "").endswith(":equip:0")]


def _pass_chain(st) -> list[dict]:
    evs: list[dict] = []
    while st.chain_live():
        r = engine.step(st, Action(ActionKind.PASS, st.current_request["player"]))
        evs.extend(r.events)
    return evs


def _fresh_gear_on_base(real_defs, gear_id=EQUIP_GEAR, extra=2):
    """fresh 局面 + 装备已在基地 + 符文可付装配费。"""
    st, first = fresh()
    d = _register(st, real_defs, gear_id)
    _fund(st, first, d, extra=extra)
    uid = _place_gear_base(st, first, d.def_id)
    return st, first, d, uid


def _fresh_gear_in_hand(real_defs, gear_id=QUICKDRAW_GEAR, extra=2):
    """fresh 局面 + 装备在手牌 + 符文可付打出费。"""
    st, first = fresh()
    d = _register(st, real_defs, gear_id)
    _fund(st, first, d, extra=extra)
    uid = _give(st, first, d.def_id)
    return st, first, d, uid


def _spawn_base_unit(st, player, uid_hint):
    from riftsim.enums import CardType as _CT
    return place_base(
        st, player,
        {"def_id": f"test:base:unit:{uid_hint}", "card_types": {_CT.UNIT},
         "domains": {Domain.R}, "cost_energy": 1, "might": 3})


# ---------------------------------------------------------------- 818 枚举与费用
def test_equip_enum_from_base_per_friendly_unit(real_defs):
    st, first, d, uid = _fresh_gear_on_base(real_defs)
    host_base = _spawn_base_unit(st, first, uid)
    host_bf = place_battlefield_unit(st, first, 0, might=2)
    acts = _equip_acts(st, first, uid)
    tgts = {a.params.get("target") for a in acts}
    assert tgts == {host_base, host_bf}  # 818.1.b.1 每友方单位一变体


def test_equip_not_available_from_hand(real_defs):
    """装备在手牌时无装配动作（818 是场上装备技能；打出后才可激活）。"""
    st, first = fresh()
    d = _register(st, real_defs, EQUIP_GEAR)
    _fund(st, first, d, extra=2)
    uid = _give(st, first, d.def_id)
    place_battlefield_unit(st, first, 0, might=2)
    assert _equip_acts(st, first, uid) == []


def test_equip_not_affordable_without_runes(real_defs):
    """SFD-124（{{装配紫色}}）：骨架符文全 R 域，无 P 符文 → 费用不可付（818.1.b）。"""
    st, first = fresh()
    d = _register(st, real_defs, "SFD-124")
    uid = _place_gear_base(st, first, d.def_id)
    place_battlefield_unit(st, first, 0, might=2)
    assert _equip_acts(st, first, uid) == []


def test_equip_requires_friendly_unit(real_defs):
    """目标限「你控制的一名单位」（818.1.c.2）：仅敌方单位时无装配动作。"""
    st, first, d, uid = _fresh_gear_on_base(real_defs)
    place_battlefield_unit(st, 1 - first, 0, might=2)
    assert _equip_acts(st, first, uid) == []


def test_equip_unavailable_while_attached(real_defs):
    """装备已贴附于单位时不可再装配（贴附状态唯一宿主，818/718.5.d）。"""
    st, first, d, uid = _fresh_gear_on_base(real_defs)
    host = place_battlefield_unit(st, first, 0, might=2)
    act = next(a for a in _equip_acts(st, first, uid) if a.params["target"] == host)
    engine.step(st, act)
    _pass_chain(st)
    assert _equip_acts(st, first, uid) == []


# ---------------------------------------------------------------- 支付→链→结算→贴附
def test_equip_resolves_attach(real_defs):
    st, first, d, uid = _fresh_gear_on_base(real_defs)
    host = place_battlefield_unit(st, first, 0, might=2)
    act = next(a for a in _equip_acts(st, first, uid) if a.params["target"] == host)
    r = engine.step(st, act)
    evs = list(r.events)
    evs.extend(_pass_chain(st))
    o, h = st.obj(uid), st.obj(host)
    assert o.attached_to == host and uid in h.attachments  # 818.2 贴附关系建立
    assert (o.zone, o.battlefield) == (h.zone, h.battlefield)  # 719.3 同位置
    assert uid not in st.base_occupants[first]  # 贴附后不再独立驻留基地
    assert any(e["type"] == "ATTACH" for e in evs)  # 链结算留痕（377.3）


def test_might_bonus_applies_while_attached(real_defs):
    st, first, d, uid = _fresh_gear_on_base(real_defs)
    host = place_battlefield_unit(st, first, 0, might=2)
    base_might = effective_might(st, host)
    act = next(a for a in _equip_acts(st, first, uid) if a.params["target"] == host)
    engine.step(st, act)
    _pass_chain(st)
    assert effective_might(st, host) == base_might + (d.might_bonus or 0)  # 718.4/137.3.a


# ---------------------------------------------------------------- 719.3.a 跟随 / 719.5 卸除
def test_attachments_follow_host_move(real_defs):
    st, first, d, uid = _fresh_gear_on_base(real_defs)
    host = place_battlefield_unit(st, first, 0, might=2)
    act = next(a for a in _equip_acts(st, first, uid) if a.params["target"] == host)
    engine.step(st, act)
    _pass_chain(st)
    st.obj(host).exhausted = False
    moves = [a for a in engine.legal_actions(st, first)
             if a.kind == ActionKind.STD_MOVE and a.source_uid == host
             and a.params.get("to") == ("base", first)]
    assert moves, "host should move back to base (R-CR-144.4.b)"
    engine.step(st, moves[0])
    o = st.obj(uid)
    assert (o.zone, o.zone_owner) == (Zone.BASE, first)  # 719.3.a 跟随顶部卡位置变化


def test_board_move_does_not_detach(real_defs):
    """719.5 回归（事件流演示抓到）：宿主战场→基地（场上→场上）不得触发卸除。"""
    st, first, d, uid = _fresh_gear_on_base(real_defs)
    host = place_battlefield_unit(st, first, 0, might=2)
    act = next(a for a in _equip_acts(st, first, uid) if a.params["target"] == host)
    engine.step(st, act)
    _pass_chain(st)
    might_with = effective_might(st, host)
    st.obj(host).exhausted = False
    mv = next(a for a in engine.legal_actions(st, first)
              if a.kind == ActionKind.STD_MOVE and a.source_uid == host
              and a.params.get("to") == ("base", first))
    engine.step(st, mv)
    o = st.obj(uid)
    assert o.attached_to == host  # 场上区域内移动：719.3.a 跟随而非 719.5 卸除
    assert uid in st.obj(host).attachments
    assert effective_might(st, host) == might_with  # 加成不因移动失效（718.4）


def test_host_dies_detach_and_bonus_gone(real_defs):
    st, first, d, uid = _fresh_gear_on_base(real_defs)
    host = place_battlefield_unit(st, first, 0, might=2)
    act = next(a for a in _equip_acts(st, first, uid) if a.params["target"] == host)
    engine.step(st, act)
    _pass_chain(st)
    kill(st, host, rule="R-CR-142.4", via="test")  # 宿主离场
    o = st.obj(uid)
    assert o.attached_to is None  # 719.5 卸除
    assert uid not in st.obj(host).attachments
    assert o.zone == Zone.BATTLEFIELD  # 卸除后滞留宿主原区域（719.5）


# ---------------------------------------------------------------- 目标失效 → fizzle；装备滞留基地
def test_target_gone_before_resolution_fizzles(real_defs):
    st, first, d, uid = _fresh_gear_on_base(real_defs)
    host = place_battlefield_unit(st, first, 0, might=2)
    act = next(a for a in _equip_acts(st, first, uid) if a.params["target"] == host)
    engine.step(st, act)  # 支付并入链
    kill(st, host, rule="R-CR-142.4", via="test")  # 结算前目标离场
    evs = _pass_chain(st)
    o = st.obj(uid)
    assert o.attached_to is None
    assert uid in st.base_occupants[first] and o.zone == Zone.BASE  # 失效指示无视→滞留基地（359.3.e.6；821.1.c.5 同原则）
    assert any("R-CR-359.3.e.9" in e["rule_ids"] for e in evs)  # 精确成员匹配


# ---------------------------------------------------------------- 非法构造防御
def test_activate_equip_rejects_hostile_target(real_defs):
    st, first, d, uid = _fresh_gear_on_base(real_defs)
    enemy_host = place_battlefield_unit(st, 1 - first, 0, might=2)
    act = Action(ActionKind.ACTIVATE_ABILITY, first, uid,
                 {"ability_id": f"{EQUIP_GEAR}:equip:0", "equip": True, "target": enemy_host})
    with pytest.raises(Exception):
        engine.step(st, act)  # 敌方单位非装配合法目标（818.1.c.2 你控制的）


# ---------------------------------------------------------------- 819 灵便：打出时触发贴附
def test_quickdraw_target_variants(real_defs):
    """SFD-022（{{灵便}}装备）：手牌打出枚举=无触发变体 + 每友方单位一变体。"""
    st, first, d, uid = _fresh_gear_in_hand(real_defs)
    host = place_battlefield_unit(st, first, 0, might=2)
    plays = [a for a in engine.legal_actions(st, first)
             if a.kind == ActionKind.PLAY_CARD and a.source_uid == uid]
    tgts = {a.params.get("target") for a in plays}
    assert None in tgts and host in tgts  # 基础打出 + 灵便触发变体（819.1.d）


def test_quickdraw_play_triggers_attach(real_defs):
    st, first, d, uid = _fresh_gear_in_hand(real_defs)
    host = place_battlefield_unit(st, first, 0, might=2)
    base_might = effective_might(st, host)
    act = next(a for a in engine.legal_actions(st, first)
               if a.kind == ActionKind.PLAY_CARD and a.source_uid == uid
               and a.params.get("target") == host)
    r = engine.step(st, act)
    evs = list(r.events)
    evs.extend(_pass_chain(st))
    o, h = st.obj(uid), st.obj(host)
    assert o.attached_to == host and uid in h.attachments  # 819.1.d 打出即贴附
    assert effective_might(st, host) == base_might + (d.might_bonus or 0)
    assert any(e["type"] == "ATTACH" for e in evs)


def test_quickdraw_fizzle_gear_stays_in_base(real_defs):
    """灵便触发结算前目标离场→指示无视（359.3.e.6）；装备已入场滞留基地。"""
    st, first, d, uid = _fresh_gear_in_hand(real_defs)
    host = place_battlefield_unit(st, first, 0, might=2)
    act = next(a for a in engine.legal_actions(st, first)
               if a.kind == ActionKind.PLAY_CARD and a.source_uid == uid
               and a.params.get("target") == host)
    engine.step(st, act)
    kill(st, host, rule="R-CR-142.4", via="test")  # 触发结算前目标离场
    evs = _pass_chain(st)
    o = st.obj(uid)
    assert o.attached_to is None
    assert uid in st.base_occupants[first] and o.zone == Zone.BASE  # 已入场永久物滞留基地
    assert any("R-CR-359.3.e.9" in e["rule_ids"] for e in evs)


def test_quickdraw_grants_reaction_timing(real_defs):
    """819.1.b 自带[反应]：闭环状态下 SFD-022 出现在反应打出枚举中。"""
    from riftsim import chain_sys, playing
    from riftsim.state import ChainItem
    st, first, d, uid = _fresh_gear_in_hand(real_defs)
    sk_spell = next(u for u in st.players[1 - first].hand
                    if CardType.SPELL in st.card_registry[st.obj(u).def_id].card_types)
    chain_sys.push(st, ChainItem(
        item_id=st.new_uid(), kind="card", source_uid=sk_spell,
        controller=1 - first, choices={"in_reaction": False}, origin=st.obj(sk_spell).zone))
    assert st.chain_live()
    reactions = playing.legal_reactions(st, first)
    playable = [a for a in reactions if a.kind == ActionKind.PLAY_CARD and a.source_uid == uid]
    assert playable, "quickdraw gear should be playable in closed chain (819.1.b)"
