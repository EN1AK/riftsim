# 效果原语集成组合测试（阶段 4；playing.py × 真实卡库 def）
# 卡组：骨架主体 + 真卡替换（同名 ≤3、单特性 ⊆ 传奇特性；decks 校验 103.1..103.4）。
# 规则锚点：R-CR-369.3（文本覆盖进场状态，覆盖 359.3 默认活跃）、R-CR-359.3/359.2.c（默认进场）、
# R-CR-377.1/401（主动技能激活）、R-CR-414.1（[E] 费用休眠）、R-CR-417.1（伤害）、
# R-CR-359.3.e.9（结算时目标失效 → 不执行）、R-CR-355.6（目标合法性）、快照往返（api_contract §8）。
from pathlib import Path

import pytest

from riftsim import engine, playing
from riftsim.actions import Action
from riftsim.carddb import load_card_db
from riftsim.cards import AbilityDef, CardDefinition, DeckList, make_skeleton_deck
from riftsim.config import GameConfig
from riftsim.enums import ActionKind, CardType, Domain, Zone
from riftsim.errors import IllegalActionError
from riftsim.objects import GameObject
from riftsim.snapshot import restore, snapshot, state_hash

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "cards_bilingual.db"

pytestmark = pytest.mark.skipif(not DB.exists(), reason="cards_bilingual.db 不在仓库根目录")

_BALLISTA = "OGN-017"  # 钢铁弩炮：装备，3 费，「以休眠进场」+「[E]：对战场上的一名单位造成2点伤害」

_RUNE_ABILITIES = (
    AbilityDef(ability_id="rune_exhaust_gain", kind="gain_resource", timing="reaction",
               cost_exhaust_self=True, grant_energy=1, rules_ref=("R-CR-164.2",)),
    AbilityDef(ability_id="rune_recycle_gain", kind="gain_resource", timing="reaction",
               cost_recycle_self=True, grant_power_self_domain=True, rules_ref=("R-CR-164.2",)),
)


@pytest.fixture(scope="module")
def real_defs():
    return load_card_db(str(DB)).defs


def _deck_with_real(real_defs, seed_tag: str, hero_tag: str, swaps: dict[str, int]) -> DeckList:
    """骨架卡组主体 + 真卡替换：同名 ≤3（103.2.b）、特性 ⊆ {R}（103.1.b.3）、主牌堆仍 40。"""
    base = make_skeleton_deck(seed_tag, hero_tag)
    main = list(base.main_deck)
    for key, cnt in swaps.items():
        d = real_defs[key]
        assert set(d.domains) <= {Domain.R} and cnt <= 3
        for _ in range(cnt):
            main.pop()          # 移除骨架法术/装备填充位
            main.append(d)
    assert len(main) == 40
    return DeckList(legend=base.legend, chosen_hero=base.chosen_hero, main_deck=tuple(main),
                    rune_deck=base.rune_deck, battlefields=base.battlefields,
                    deck_id=f"{seed_tag}-real")


def _fresh(real_defs, seed: int = 42):
    """双方 0 张调度后停在先手主阶段行动窗；A 组含 3× OGN-017 真卡注册。"""
    cfg = GameConfig(decks=(
        _deck_with_real(real_defs, "A", "hero-a", {_BALLISTA: 3}),
        make_skeleton_deck("B", "hero-b"),
    ))
    st = engine.reset(seed, cfg)
    first = st.meta.config["first_player"]
    engine.step(st, Action(ActionKind.RESOLVE_CHOICE, first, params={"set_aside": []}))
    engine.step(st, Action(ActionKind.RESOLVE_CHOICE, 1 - first, params={"set_aside": []}))
    return st, first


def _give(st, player: int, def_id: str, zone: Zone, **kw) -> int:
    """以注册表中的既有 def 生成对象并落位（真卡/骨架 def 皆可）。"""
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


def _give_rune_board(st, player: int, idx: int) -> int:
    """放置一张活跃符文补足法力（R-CR-164.2 双技能；不占真卡位）。"""
    d = CardDefinition(def_id=f"t:rune:{idx}", name=f"测试符文{idx}",
                       card_types=frozenset({CardType.RUNE}), domains=frozenset({Domain.R}),
                       abilities=_RUNE_ABILITIES)
    st.card_registry[d.def_id] = d
    return _give(st, player, d.def_id, Zone.BASE)


def _give_bf_unit(st, player: int, bf_index: int, tag: str = "u2:1") -> int:
    uid = _give(st, player, f"sk:unit:{tag}", Zone.BATTLEFIELD, battlefield=bf_index)
    st.battlefields[bf_index].occupants.append(uid)
    return uid


def _pass_chain(st) -> list[dict]:
    """FEPR 双方连续让过直至链空（339/340），返回累计事件。"""
    evs: list[dict] = []
    while st.chain_live():
        r = engine.step(st, Action(ActionKind.PASS, st.current_request["player"]))
        evs.extend(r.events)
    return evs


def _activate_options(st, player: int, uid: int):
    return [a for a in engine.legal_actions(st, player)
            if a.kind == ActionKind.ACTIVATE_ABILITY and a.source_uid == uid]


# ---------------------------------------------------------------- a) enters_exhausted 覆盖进场状态
def test_real_gear_enters_exhausted_via_3693(real_defs):
    """OGN-017（此牌以休眠状态进场）打出结算后为休眠（369.3 覆盖 359.3 默认活跃）。"""
    st, first = _fresh(real_defs)
    for i in range(3):  # 3 张活跃符文付 3 法力（357.1.a 支付窗自动激活 [E]）
        _give_rune_board(st, first, i)
    uid = _give(st, first, _BALLISTA, Zone.HAND)
    play = next(a for a in engine.legal_actions(st, first)
                if a.kind == ActionKind.PLAY_CARD and a.source_uid == uid)
    r = engine.step(st, play)
    o = st.obj(uid)
    assert o.zone == Zone.BASE and o.exhausted is True
    paid = next(e for e in r.events if e["type"] == "PAID")
    assert paid["public"]["energy"] == 3  # 206 印刷费用
    res = next(e for e in r.events if e["type"] == "RESOLVE"
               and e["rule_ids"] == ["R-CR-359.3", "R-CR-369.3"])
    assert res["public"]["exhausted"] is True


def test_textless_gear_enters_active_control(real_defs):
    """对照组：无进场文本的装备仍按 359.3 默认活跃进场（不被 enters_exhausted 误覆盖）。"""
    st, first = _fresh(real_defs)
    for i in range(3):
        _give_rune_board(st, first, 10 + i)
    sk_gear = next(k for k in st.card_registry if k.startswith("sk:gear:"))
    uid = _give(st, first, sk_gear, Zone.HAND)
    play = next(a for a in engine.legal_actions(st, first)
                if a.kind == ActionKind.PLAY_CARD and a.source_uid == uid)
    r = engine.step(st, play)
    o = st.obj(uid)
    assert o.zone == Zone.BASE and o.exhausted is False
    assert not any(e["rule_ids"] == ["R-CR-359.3", "R-CR-369.3"] for e in r.events)


# ---------------------------------------------------------------- b) deal_damage 激活 + 结算
def test_deal_damage_activate_per_target_and_resolve(real_defs):
    """ACTIVATE_ABILITY 按目标逐个展开（355 步骤 2）；激活休眠自身（414.1）；
    结算造成损害事件（417.1，OGN-017=2 点）。"""
    st, first = _fresh(real_defs)
    ballista = _give(st, first, _BALLISTA, Zone.BASE)  # 布置为活跃（跳过打出路径）
    t0 = _give_bf_unit(st, 1 - first, 0, tag="u2:1")
    t1 = _give_bf_unit(st, 1 - first, 1, tag="u2:2")
    acts = _activate_options(st, first, ballista)
    deal_acts = [a for a in acts
                 if a.params.get("ability_id") == f"{_BALLISTA}:exhaust_deal_damage:1"]
    assert {a.params.get("target") for a in deal_acts} == {t0, t1}  # per-target 展开
    assert all(a.params.get("in_reaction") is False for a in deal_acts)
    # enters_exhausted 静态技能绝不入激活选项（377.1）
    assert not any(a.params.get("ability_id") == f"{_BALLISTA}:enters_exhausted:0" for a in acts)

    r = engine.step(st, next(a for a in deal_acts if a.params["target"] == t1))
    assert st.obj(ballista).exhausted is True  # [E] 费用（414.1）
    assert any(e["type"] == "EXHAUST" and "R-CR-414.1" in e["rule_ids"] for e in r.events)
    evs = _pass_chain(st)
    assert st.obj(t1).damage == 2
    dmg = next(e for e in evs if e["type"] == "DAMAGE")
    assert "R-CR-417.1" in dmg["rule_ids"]
    assert dmg["public"]["amount"] == 2 and dmg["public"]["uid"] == t1
    assert any("R-CR-406" in e["rule_ids"] for e in evs)  # 技能结算后离链（406）
    assert st.obj(t0).damage == 0  # 未选目标不受伤害


def test_deal_damage_fizzle_when_target_left(real_defs):
    """目标在结算时已离场 → 不再符合范围：指示不执行（359.3.e.9），无伤害。"""
    st, first = _fresh(real_defs)
    ballista = _give(st, first, _BALLISTA, Zone.BASE)
    tgt = _give_bf_unit(st, 1 - first, 1)
    act = next(a for a in _activate_options(st, first, ballista)
               if a.params.get("target") == tgt)
    engine.step(st, act)
    # 目标离场（响应窗中态变化的最小模拟）
    st.battlefields[1].occupants.remove(tgt)
    o = st.obj(tgt)
    o.zone, o.zone_owner, o.battlefield = Zone.TRASH, 1 - first, None
    st.players[1 - first].trash.append(tgt)
    evs = _pass_chain(st)
    assert st.obj(tgt).damage == 0
    assert not any(e["type"] == "DAMAGE" for e in evs)
    fizzle = next(e for e in evs if "R-CR-359.3.e.9" in e["rule_ids"])
    assert fizzle["type"] == "RESOLVE"
    assert fizzle["public"]["fizzle"] == "target_invalid"
    assert fizzle["card_ids"] == [f"uid:{tgt}"]


# ---------------------------------------------------------------- c) 静态技能不可激活（377.1）
def test_static_enters_exhausted_not_activatable(real_defs):
    st, first = _fresh(real_defs)
    ballista = _give(st, first, _BALLISTA, Zone.BASE)
    illegal = Action(ActionKind.ACTIVATE_ABILITY, first, ballista,
                     {"ability_id": f"{_BALLISTA}:enters_exhausted:0",
                      "in_reaction": False, "target": None})
    assert not any(a.digest() == illegal.digest() for a in engine.legal_actions(st, first))
    h_before = state_hash(st)
    with pytest.raises(IllegalActionError):
        engine.step(st, illegal)
    assert state_hash(st) == h_before  # 拒绝非法动作不改变状态（api_contract §6）
    # 处理器守卫同样带 377.1 锚点（绕开 legal 集合的手工构造路径）
    with pytest.raises(IllegalActionError, match=r"377\.1"):
        playing.handle_activate(st, illegal)
    assert state_hash(st) == h_before


# ---------------------------------------------------------------- d) 范围外目标拒绝（355.6）
def test_deal_damage_out_of_scope_target_rejected(real_defs):
    """scope=unit_at_battlefield：基地中的单位不在合法目标集，手工提交被拒且状态不变。"""
    st, first = _fresh(real_defs)
    ballista = _give(st, first, _BALLISTA, Zone.BASE)
    base_unit = _give(st, 1 - first, "sk:unit:u2:1", Zone.BASE)  # 敌方单位在基地=范围外
    assert all(a.params.get("target") != base_unit
               for a in _activate_options(st, first, ballista))
    illegal = Action(ActionKind.ACTIVATE_ABILITY, first, ballista,
                     {"ability_id": f"{_BALLISTA}:exhaust_deal_damage:1",
                      "in_reaction": False, "target": base_unit})
    h_before = state_hash(st)
    with pytest.raises(IllegalActionError):
        engine.step(st, illegal)
    assert state_hash(st) == h_before
    with pytest.raises(IllegalActionError, match=r"355\.6"):
        playing.handle_activate(st, illegal)
    assert state_hash(st) == h_before
    assert st.obj(ballista).exhausted is False  # 拒绝后不得消耗 [E]


# ---------------------------------------------------------------- e) snapshot/restore 技能字段往返
def test_snapshot_restore_ability_fields_and_determinism(real_defs):
    st, first = _fresh(real_defs)
    ballista = _give(st, first, _BALLISTA, Zone.BASE)
    tgt = _give_bf_unit(st, 1 - first, 1)
    snap = snapshot(st)

    def run_path(stx: object) -> tuple[str, int]:
        act = next(a for a in _activate_options(stx, first, ballista)
                   if a.params.get("target") == tgt)
        engine.step(stx, act)
        _pass_chain(stx)
        return state_hash(stx), stx.obj(tgt).damage

    h_orig, dmg_orig = run_path(st)
    st2 = restore(snap)
    restored = next(a for a in st2.card_registry[_BALLISTA].abilities
                    if a.kind == "deal_damage")
    assert restored.damage == 2 and restored.target_scope == "unit_at_battlefield"
    assert restored.cost_exhaust_self is True and restored.timing == "action"
    passive = next(a for a in st2.card_registry[_BALLISTA].abilities
                   if a.kind == "enters_exhausted")
    assert passive.timing == "passive"
    h_rest, dmg_rest = run_path(st2)
    assert h_rest == h_orig  # 恢复快照后同动作序列同终态（确定性）
    assert dmg_rest == dmg_orig == 2
