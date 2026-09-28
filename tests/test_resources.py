# 符文/符文池/燃尽（T-0028..T-0034、T-0040/0041/0031/0032）
from riftsim import engine
from riftsim.actions import Action
from riftsim.enums import ActionKind, CardType, Domain, Keyword, Termination, Zone
from riftsim.resources import draw
from tests.helpers import fresh, give_hand, place_base


def _rune_def(idx):
    return {"def_id": f"t:rune:{idx}", "name": f"R 符文{idx}", "card_types": {CardType.RUNE},
            "domains": {Domain.R}, "abilities": (
                __import__("riftsim.cards", fromlist=["AbilityDef"]).AbilityDef(
                    ability_id="rune_exhaust_gain", kind="gain_resource", timing="reaction",
                    cost_exhaust_self=True, grant_energy=1, rules_ref=("R-CR-164.2",)),
                __import__("riftsim.cards", fromlist=["AbilityDef"]).AbilityDef(
                    ability_id="rune_recycle_gain", kind="gain_resource", timing="reaction",
                    cost_recycle_self=True, grant_power_self_domain=True, rules_ref=("R-CR-164.2",)),
            )}


def test_t0029_rune_recycle_gain_c():
    st, first = fresh()
    # 基地放 1 张活跃 R 符文；主阶段激活回收技能
    uid = place_base(st, first, _rune_def(1))
    legal = engine.legal_actions(st, first)
    act = next(a for a in legal if a.kind == ActionKind.ACTIVATE_ABILITY and a.source_uid == uid
               and a.params.get("ability_id") == "rune_recycle_gain")
    engine.step(st, act)
    # 确认后立即结算（429.2）：池 +1[R]；符文回符文堆底
    assert st.players[first].rune_power.get("R") == 1
    assert st.obj(uid).zone == Zone.RUNE_DECK
    assert uid == st.players[first].rune_deck[0]  # 底部


def test_t0028_rune_exhaust_gain_energy():
    st, first = fresh()
    uid = place_base(st, first, _rune_def(2))
    legal = engine.legal_actions(st, first)
    act = next(a for a in legal if a.kind == ActionKind.ACTIVATE_ABILITY and a.source_uid == uid
               and a.params.get("ability_id") == "rune_exhaust_gain")
    engine.step(st, act)
    assert st.players[first].rune_energy == 1
    assert st.obj(uid).exhausted is True
    # 已休眠不能再次激活 [E]
    legal2 = engine.legal_actions(st, first)
    assert not any(a.kind == ActionKind.ACTIVATE_ABILITY and a.source_uid == uid
                   and a.params.get("ability_id") == "rune_exhaust_gain" for a in legal2)


def test_t0032_pool_clear_at_turn_end():
    st, first = fresh()
    st.players[first].rune_energy = 2
    st.players[first].rune_power = {"R": 1}
    st.players[1 - first].rune_power = {"G": 2}
    engine.step(st, Action(ActionKind.END_MAIN, first))
    # 3e 清空全体
    assert st.players[first].rune_energy == 0 and st.players[first].rune_power == {}
    assert st.players[1 - first].rune_power == {}


def test_t0033_domain_mismatch_unplayable():
    st, first = fresh()
    give_g = give_hand(st, first, {"def_id": "t:spg", "name": "G 法术",
                                   "card_types": {CardType.SPELL}, "domains": {Domain.G},
                                   "cost_energy": 1, "cost_power": (Domain.G,)})
    legal = engine.legal_actions(st, first)
    assert not any(a.kind == ActionKind.PLAY_CARD and a.source_uid == give_g for a in legal)


def test_t0034_pay_with_rune_skills_in_window():
    st, first = fresh()
    # 池 0，场上 3 活跃 R 符文；打出 U2（2E+1R）：回收 1 补 R、[E] 2 补法力
    for i in range(3):
        place_base(st, first, _rune_def(10 + i))
    uid = give_hand(st, first, {"def_id": "t:u2x", "name": "U2X", "card_types": {CardType.UNIT},
                                "domains": {Domain.R}, "cost_energy": 2, "cost_power": (Domain.R,),
                                "might": 2})
    legal = engine.legal_actions(st, first)
    play = next(a for a in legal if a.kind == ActionKind.PLAY_CARD and a.source_uid == uid)
    r = engine.step(st, play)
    # 打出完成：U2X 以休眠进场（基地）
    assert st.obj(uid).zone in (Zone.BASE, Zone.BATTLEFIELD)
    assert st.obj(uid).exhausted is True
    assert st.players[first].rune_energy == 0 and st.players[first].rune_power == {}
    # 符文明细：注入 3 + 首回合召出 2 = 5；回收 1 →剩 4（其中 2 张因 [E] 休眠）
    runes = [u for u in st.player_objects(first, board_only=True)
             if CardType.RUNE in st.card_registry[st.obj(u).def_id].card_types]
    assert len(runes) == 4
    assert sum(1 for u in runes if st.obj(u).exhausted) == 2


def test_t0040_burnout_draw_cycle():
    st, first = fresh()
    # 主牌堆空、废牌堆 3 张：抽牌→洗回→对手得 1 分→完成抽牌
    p = st.players[first]
    trashed = p.main_deck[-3:]
    p.trash.extend(trashed)
    for u in trashed:
        st.obj(u).zone = Zone.TRASH
    p.main_deck = []
    old_score = st.players[1 - first].score
    got = draw(st, first, 1)
    assert len(got) == 1
    assert st.players[1 - first].score == old_score + 1
    assert len(st.players[first].main_deck) == 2  # 3-1


def test_t0041_burnout_immediate_win():
    st, first = fresh()
    p = st.players[first]
    trashed = p.main_deck[-3:]
    p.trash.extend(trashed)
    for u in trashed:
        st.obj(u).zone = Zone.TRASH
    p.main_deck = []
    st.players[1 - first].score = 7  # 431.3.c.1：达标即胜，无需清理
    draw(st, first, 1)
    assert st.ended is True
    assert st.winner == 1 - first
    assert st.termination == Termination.BURNOUT
