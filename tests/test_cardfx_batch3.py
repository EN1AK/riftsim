# cardfx 批次 3：手写脚本卡 + 临时修正原语（spell_pump / on_play_pump）集成测试
# 规则锚点：
#   R-CR-317.2.c「本回合内」效果回合结束失效（317.2/3.d 特殊清理同时执行）
#   R-CR-474 修正层-加减计算；R-CR-355.6 目标选取；359.3.e.9 目标结算时失效
#   R-CR-383.1 打出触发；413.1 抽牌；157.1 法术结算
from pathlib import Path

import pytest

from riftsim import engine, phaser
from riftsim.actions import Action
from riftsim.carddb import load_card_db
from riftsim.enums import ActionKind, CardType, Domain, Zone
from riftsim.objects import GameObject
from riftsim.resources import effective_might
from riftsim.snapshot import restore, snapshot, state_hash
from tests.helpers import fresh, place_base, place_battlefield_unit

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "cards_bilingual.db"

pytestmark = pytest.mark.skipif(not DB.exists(), reason="cards_bilingual.db 不在仓库根目录")

SPELL_PUMP7 = "OGN-154"    # 法术{{迅捷}}：让一名单位在本回合内{{S}}+7
SPELL_PUMP5 = "SFD-097"    # 法术{{迅捷}}：让一名单位在本回合内{{S}}+5
ON_PLAY_PUMP = "OGN-197"   # 单位{{待命}}：当你打出我时，让我本回合内{{S}}+3
SPELL_DRAW2 = "OGN-083"    # 法术{{反应}}：抽两张牌


@pytest.fixture(scope="module")
def real_defs():
    return load_card_db(str(DB)).defs


def _register(st, real_defs, key):
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


# ---------------------------------------------------------------- spell_pump：目标枚举/结算/范围
def test_spell_pump_target_enum_and_resolve(real_defs):
    st, first = fresh()
    d = _register(st, real_defs, SPELL_PUMP7)
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    base_u = place_base(st, first, {"def_id": "test:pump:base", "name": "基地测试单位",
                                    "card_types": {CardType.UNIT}, "domains": {Domain.R},
                                    "cost_energy": 1, "might": 1})  # 基地单位也在 "unit" scope 内
    own_bf = place_battlefield_unit(st, first, 0, might=2)
    foe_bf = place_battlefield_unit(st, 1 - first, 1, might=3)
    plays = _plays(st, first, uid)
    tgts = {a.params["target"] for a in plays}
    assert {base_u, own_bf, foe_bf} <= tgts  # 355.6 任一单位（基地/战场、敌我皆可）
    before = effective_might(st, foe_bf)
    engine.step(st, next(a for a in plays if a.params["target"] == foe_bf))
    _pass_chain(st)
    assert st.obj(foe_bf).might_temp == 7
    assert effective_might(st, foe_bf) == before + 7  # 474 加减层贯通战力读数
    assert st.obj(uid).zone == Zone.TRASH  # 157.1 结算后废牌堆


def test_spell_pump_value_variants(real_defs):
    """同原语不同数值（+5 卡）——原语参数化而非逐卡独立逻辑。"""
    st, first = fresh()
    d = _register(st, real_defs, SPELL_PUMP5)
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    t = place_battlefield_unit(st, 1 - first, 0, might=4)
    before = effective_might(st, t)
    engine.step(st, next(a for a in _plays(st, first, uid) if a.params["target"] == t))
    _pass_chain(st)
    assert effective_might(st, t) == before + 5


def test_spell_pump_fizzle_when_target_left(real_defs):
    """结算时目标已离场 → 泵指示不执行（359.3.e.9），法术仍入废牌堆。"""
    st, first = fresh()
    d = _register(st, real_defs, SPELL_PUMP7)
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    t = place_battlefield_unit(st, 1 - first, 0, might=3)
    engine.step(st, next(a for a in _plays(st, first, uid) if a.params["target"] == t))
    # 链未结算时目标被杀（直接移走模拟：击杀入废牌堆）
    from riftsim.playing import kill_
    kill_(st, t)
    evs = _pass_chain(st)
    fiz = [e for e in evs if e["type"] == "RESOLVE" and e["public"].get("fizzle") == "target_invalid"]
    assert fiz and "R-CR-359.3.e.9" in fiz[0]["rule_ids"]
    assert st.obj(uid).zone == Zone.TRASH


def test_spell_pump_expires_end_of_turn(real_defs):
    """R-CR-317.2.c：「本回合内」效果在回合结束特殊清理（3.d）时失效。"""
    st, first = fresh()
    d = _register(st, real_defs, SPELL_PUMP7)
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    t = place_battlefield_unit(st, 1 - first, 0, might=3)
    before = effective_might(st, t)
    engine.step(st, next(a for a in _plays(st, first, uid) if a.params["target"] == t))
    _pass_chain(st)
    assert st.obj(t).might_temp == 7
    phaser.end_turn(st)  # 317.2 回合结束：3.c 伤害 +3.d「本回合」效果 +3.e[直到回合结束]
    assert st.obj(t).might_temp == 0
    assert effective_might(st, t) == before


# ---------------------------------------------------------------- on_play_pump：打出触发
def test_on_play_pump_triggers_and_stacks(real_defs):
    st, first = fresh()
    d = _register(st, real_defs, ON_PLAY_PUMP)
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    base_might = d.might or 0
    plays = _plays(st, first, uid)
    assert plays
    engine.step(st, plays[0])
    evs = _pass_chain(st)  # 383.1 触发入链 → 双方放权 → 结算
    pumps = [e for e in evs if e["type"] == "RESOLVE" and e["public"].get("uid") == uid
             and e["public"].get("pump")]
    assert pumps and pumps[0]["public"]["pump"] == 3
    assert "R-CR-317.2.c" in pumps[0]["rule_ids"]
    assert st.obj(uid).might_temp == 3
    assert effective_might(st, uid) == base_might + 3


def test_on_play_pump_ignored_when_source_left(real_defs):
    """触发结算时源已离场 → 无从施加（359.3.e.9 类 ignore 事件）。"""
    st, first = fresh()
    d = _register(st, real_defs, ON_PLAY_PUMP)
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    engine.step(st, _plays(st, first, uid)[0])
    from riftsim.playing import kill_
    kill_(st, uid)  # 触发尚在链上时单位被杀
    evs = _pass_chain(st)
    ig = [e for e in evs if e["type"] == "RESOLVE" and e["public"].get("ignore") == "source_left_board"]
    assert ig and ig[0]["public"]["uid"] == uid


# ---------------------------------------------------------------- OGN-083：中文数字「抽两张牌」手写登记
def test_ogn083_spell_draw_two(real_defs):
    st, first = fresh()
    d = _register(st, real_defs, SPELL_DRAW2)
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    assert len(st.players[first].main_deck) >= 2  # fresh 骨架主堆足以抽两张
    n_hand_before = len(st.players[first].hand)
    plays = _plays(st, first, uid)
    # 无目标法术：动作不带 target
    assert all("target" not in a.params for a in plays)
    engine.step(st, plays[0])
    _pass_chain(st)
    assert len(st.players[first].hand) == n_hand_before + 1  # -1 打出 +2 抽取 = 净 +1
    assert st.obj(uid).zone == Zone.TRASH


# ---------------------------------------------------------------- rq-2a 补充：负向修正/抽三/FND-196
def test_negative_pump_reduces_effective_might(real_defs):
    """UNL-066（{{S}}-10）：负向修正照加不 clamp（无「不得低于」下限语）。"""
    st, first = fresh()
    d = _register(st, real_defs, "UNL-066")
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    t = place_battlefield_unit(st, 1 - first, 0, might=3)
    before = effective_might(st, t)
    engine.step(st, next(a for a in _plays(st, first, uid) if a.params["target"] == t))
    _pass_chain(st)
    assert st.obj(t).might_temp == -10
    assert effective_might(st, t) == before - 10  # 可为负（修正层照算）


def test_sfd087_draws_three(real_defs):
    st, first = fresh()
    d = _register(st, real_defs, "SFD-087")
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    assert len(st.players[first].main_deck) >= 3
    n = len(st.players[first].hand)
    engine.step(st, _plays(st, first, uid)[0])
    _pass_chain(st)
    assert len(st.players[first].hand) == n + 2  # -1 打出 +3 抽取


def test_fnd196_loaded_and_pumps(real_defs):
    """FND-196（type_en 缺省、type_cn 兜底路径）登记与结算同 OGN-197 原语。"""
    assert "FND-196" in real_defs
    st, first = fresh()
    d = _register(st, real_defs, "FND-196")
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    engine.step(st, _plays(st, first, uid)[0])
    _pass_chain(st)
    assert st.obj(uid).might_temp == 3


# ---------------------------------------------------------------- 快照往返：pump_value 字段保真
def test_snapshot_roundtrip_keeps_pump_value(real_defs):
    st, first = fresh()
    d = _register(st, real_defs, SPELL_PUMP7)
    _fund(st, first, d)
    uid = _give(st, first, d.def_id, Zone.HAND)
    t = place_battlefield_unit(st, 1 - first, 0, might=3)
    engine.step(st, next(a for a in _plays(st, first, uid) if a.params["target"] == t))
    _pass_chain(st)
    h = state_hash(st)
    snap = snapshot(st)
    st2 = restore(snap)
    assert state_hash(st2) == h
    d2 = st2.card_registry[SPELL_PUMP7]
    assert next(ab for ab in d2.abilities if ab.kind == "spell_pump").pump_value == 7
