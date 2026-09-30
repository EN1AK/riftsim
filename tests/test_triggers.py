# 383 触发注册表首批接线测试（2026-10-01）：kind="trigger" + trigger/payload 声明
# 锚点：383.3 条件满足触发式技能如主动技能入链；383.3.c 可任意玩家回合任意闭环；
# 383.3.d 同时多触发由玩家定序（MVP=uid 确定序，记遗留）；SR 宿主条件（征服/据守同战场宿主）。
# 首批：SFD-115 据守+1分（469.2+383）/SFD-118 征服召符文（167+383）/SFD-124 征服弃1抽1（418+383）。
from pathlib import Path

import pytest

from riftsim import engine, scoring
from riftsim.actions import Action
from riftsim.carddb import load_card_db
from riftsim.enums import ActionKind, CardType, Domain, Zone
from riftsim.objects import GameObject
from tests.helpers import fresh, give_hand, place_battlefield_unit, place_base, rune_def

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "cards_bilingual.db"

pytestmark = pytest.mark.skipif(not DB.exists(), reason="cards_bilingual.db 不在仓库根目录")

SFD_115 = "SFD-115"  # 三相之力：当我据守时+1分
SFD_118 = "SFD-118"  # 碎骨棒：当我征服时召出1枚休眠符文
SFD_124 = "SFD-124"  # 多兰之戒：当我征服时弃1抽1
UNL_019 = "UNL-019"  # 枯萎战斧：回合结束未征服→卸除此牌并对我造成4（719.1 me=宿主）
VEN_011 = "VEN-011"  # 悬摆之刃：当我移动到战场时，给我+2战力本回合（me=宿主）
SFD_190 = "SFD-190"  # 炉火斗篷：当我进攻或防守时，对此处所有敌方单位造成2
SFD_016 = "SFD-016"  # 反曲之弓：当我进攻或防守时，对此处一名敌方单位造成2


@pytest.fixture(scope="module")
def real_defs():
    return load_card_db(str(DB)).defs


def _register(st, defs, def_id):
    d = defs[def_id]
    st.card_registry[d.def_id] = d
    return d


def _host_with_gear(st, defs, player: int, gear_id: str, bf: int = 0, might: int = 2):
    """宿主单位（默认骨架 might2）+ 装备贴附（装备的控制者与宿主同）。"""
    hd = _register(st, defs, gear_id)
    uid_host = place_battlefield_unit(st, player, bf, might=might)
    uid_gear = st.new_uid()
    o_host = st.obj(uid_host)
    st.objects[uid_gear] = GameObject(
        uid=uid_gear, def_id=gear_id, owner=player, controller=player,
        zone=Zone.BATTLEFIELD, battlefield=bf, attached_to=uid_host)
    o_host.attachments.append(uid_gear)
    return uid_host, uid_gear


def _pass_chain(st) -> list[dict]:
    evs: list[dict] = []
    while st.chain_live():
        evs.extend(engine.step(st, Action(ActionKind.PASS, st.current_request["player"])).events)
    return evs


# ---------------------------------------------------------------- 公用
def _hold_score_and_resolve(st, player, bf=0):
    """真实流程中 score_hold 只在 advance 内运行（current_request=None）；
    测试直调需先清停靠决策点，打分后用 advance 踢 FEPR 机（334/337）再逐让过结算。"""
    evs: list[dict] = []
    from riftsim import phaser
    st.current_request = None
    phaser.score_hold(st, player)
    engine.advance(st)
    evs.extend(_pass_chain(st))
    return evs


def test_hold_trigger_scores_extra_point(real_defs):
    """宿主在据守战场 + SFD-115 → trigger 入链结算 → 玩家再获 1 分（383.3+469.2）。"""
    st, first = fresh()
    hd = _register(st, real_defs, SFD_115)
    _host_with_gear(st, real_defs, first, SFD_115, bf=0)
    st.battlefields[0].controller = first  # 315.2 控制据守
    base_score = st.players[first].score
    evs = _hold_score_and_resolve(st, first, bf=0)
    assert st.players[first].score == base_score + 2  # 据守 1 + 触发 1
    assert any("R-CR-383.3" in e["rule_ids"] or "383" in str(e["rule_ids"]) for e in evs) \
        or any(e["type"] == "SCORE" and e["public"].get("kind") == "trigger_hold" for e in evs)


# ---------------------------------------------------------------- SFD-118 征服触发召符文
def test_conquer_trigger_channels_rune(real_defs):
    """宿主在征服战场 + SFD-118 → trigger 结算 → 召出 1 枚休眠符文（167）。"""
    st, first = fresh()
    _register(st, real_defs, SFD_118)
    _host_with_gear(st, real_defs, first, SFD_118, bf=0)
    base_runes = len(st.base_occupants[first])
    st.current_request = None
    scoring.score_conquer(st, first, st.battlefields[0])  # 确立 conquor 记分
    engine.advance(st)
    evs = _pass_chain(st)
    assert len(st.base_occupants[first]) == base_runes + 1  # 休眠符文入场（167 召出）
    assert any(e["type"] == "EXECUTE" and "channel" in str(e["public"]) for e in evs) \
        or any("167" in str(e["rule_ids"]) or "383" in str(e["rule_ids"]) for e in evs)


# ---------------------------------------------------------------- SFD-124 征服触发弃1抽1
def test_conquer_trigger_discard_then_draw(real_defs):
    """宿主在征服战场 + SFD-124 → 触发结算时控制者经 CHOOSE_MODE 选弃 1 张手牌，然后抽 1 张
    （383.3+422.1+413.1；目标/选择时点按结算时近似——TODO-383 已登记）。"""
    st, first = fresh()
    _register(st, real_defs, SFD_124)
    _host_with_gear(st, real_defs, first, SFD_124, bf=0)
    drop = give_hand(st, first, {"def_id": "test:fodder", "card_types": {CardType.SPELL}})
    hand_before = len(st.players[first].hand)
    st.current_request = None
    scoring.score_conquer(st, first, st.battlefields[0])
    engine.advance(st)
    _pass_chain(st)  # FEPR：finalize→双方让过→结算发 CHOOSE_MODE
    r = st.current_request
    assert r and r["kind"] == "choose_mode" and r["options"].get("reason") == "trigger_discard"
    assert drop in r["options"]["choices"]  # 手牌 uid 全列为可选
    evs = engine.step(st, Action(ActionKind.RESOLVE_CHOICE, first, None, {"choice": drop})).events
    assert len(st.players[first].hand) == hand_before  # 弃 1 抽 1 净不变
    assert drop in [u for u in st.players[first].trash]  # 已弃入废牌堆（422.1）
    assert any(e["type"] == "DISCARD" and e["public"].get("player") == first for e in evs)
    assert any(e["type"] == "DRAW" and e["public"].get("player") == first for e in evs)


def test_conquer_trigger_discard_no_hand_draws(real_defs):
    """手牌为空：055 尽可能执行→弃置无视、抽 1 仍执行（无 CHOOSE 请求）。"""
    st, first = fresh()
    _register(st, real_defs, SFD_124)
    _host_with_gear(st, real_defs, first, SFD_124, bf=0)
    st.players[first].hand.clear()
    deck_before = len(st.players[first].main_deck)
    st.current_request = None
    scoring.score_conquer(st, first, st.battlefields[0])
    engine.advance(st)
    _pass_chain(st)
    assert st.current_request is None or st.current_request["kind"] != "choose_mode"
    assert len(st.players[first].hand) == 1  # 仅抽的 1 张
    assert len(st.players[first].main_deck) == deck_before - 1


def test_trigger_discard_choices_hidden_from_opponent(real_defs):
    """弃牌选择请求的手牌 uid 对非请求方遮蔽（128 隐藏信息；同 SCOUT_KEEP 过滤范式）。"""
    from riftsim import observation
    st, first = fresh()
    _register(st, real_defs, SFD_124)
    _host_with_gear(st, real_defs, first, SFD_124, bf=0)
    give_hand(st, first, {"def_id": "test:fodder", "card_types": {CardType.SPELL}})
    st.current_request = None
    scoring.score_conquer(st, first, st.battlefields[0])
    engine.advance(st)
    _pass_chain(st)
    assert st.current_request["options"].get("reason") == "trigger_discard"
    obs_foe = observation.observe(st, 1 - first)
    req_view = obs_foe.get("request") or {}
    assert not (req_view.get("options") or {}).get("choices")  # uid 列表被遮蔽
    obs_self = observation.observe(st, first)
    assert (obs_self["request"]["options"]).get("choices")  # 请求方可见全列


# ---------------------------------------------------------------- 条件不满足不触发
def test_trigger_not_fired_without_host_in_battlefield(real_defs):
    """宿主不在据守战场（装备在基地）→ 据守记分时 SFD-115 trigger 不触发（条件不满足）。"""
    st, first = fresh()
    _register(st, real_defs, SFD_115)
    # 装备在基地（未贴附宿主）
    d = real_defs[SFD_115]
    st.card_registry[d.def_id] = d
    uid = st.new_uid()
    st.objects[uid] = GameObject(uid=uid, def_id=SFD_115, owner=first, controller=first,
                                 zone=Zone.BASE, zone_owner=first)
    st.base_occupants[first].append(uid)
    st.battlefields[0].controller = first
    base_score = st.players[first].score
    from riftsim import phaser
    phaser.score_hold(st, first)
    evs = _pass_chain(st)
    assert st.players[first].score == base_score + 1  # 只有据守本身的 +1
    assert not any("trigger" in str(e["public"]) for e in evs)


def test_trigger_not_fired_before_score(real_defs):
    """战场无据守记录（controller=None）→ 不触发。"""
    st, first = fresh()
    _register(st, real_defs, SFD_115)
    _host_with_gear(st, real_defs, first, SFD_115, bf=0)
    base_score = st.players[first].score
    from riftsim import phaser
    phaser.score_hold(st, first)
    _pass_chain(st)
    assert st.players[first].score == base_score  # controller=None 无据守得分


# ---------------------------------------------------------------- UNL-019 回合结束触发（383+719.1+435.1）
def _end_turn_and_resolve(st):
    """结束阶段触发链全流（advance-context）：fire→advance 踢 FEPR→双方让过→链净→续段清理移交。"""
    from riftsim import phaser
    st.current_request = None
    phaser.end_turn(st)
    engine.advance(st)
    evs = _pass_chain(st)
    engine.advance(st)
    return evs


def test_end_of_turn_trigger_unattach_and_damage(real_defs):
    """UNL-019（宿主 might=5）：回合结束未征服 → 卸除装备 + 宿主吃 4（719.1 me=宿主）→
    存活后 3c 治疗移除伤害（317.2.b）；装备留宿主区域。"""
    st, first = fresh()
    _register(st, real_defs, UNL_019)
    host, gear = _host_with_gear(st, real_defs, first, UNL_019, bf=0, might=5)
    evs = _end_turn_and_resolve(st)
    o_host, o_gear = st.obj(host), st.obj(gear)
    assert o_gear.attached_to is None and gear not in o_host.attachments  # 435.1.b 卸除
    # 终态：卸除先留宿主区域（435 面），随即由场地清理召回所属者基地（323.7：战场未贴附装备不得驻留）
    assert o_gear.zone == Zone.BASE and gear in st.base_occupants[first]
    assert gear not in st.battlefields[0].occupants
    assert any(e["type"] == "DAMAGE" and e["public"].get("uid") == host
               and e["public"].get("amount") == 4 for e in evs)
    assert any(e["type"] == "DETACH" and e["public"].get("gear") == gear for e in evs)
    assert o_host.zone == Zone.BATTLEFIELD  # might=5 存活
    assert o_host.damage == 0  # 链净后续段 3c 治疗移除（317.2.b）
    assert st.turn_player == 1 - first  # 移交正常（306）


def test_end_of_turn_trigger_kills_host(real_defs):
    """UNL-019（宿主 might=2）：自伤 4 ≥ might → state-based 摧毁（323.5，先于 3c 治疗）；
    装备已先行卸除→留战场。"""
    st, first = fresh()
    _register(st, real_defs, UNL_019)
    host, gear = _host_with_gear(st, real_defs, first, UNL_019, bf=0, might=2)
    evs = _end_turn_and_resolve(st)
    assert st.obj(host).zone == Zone.TRASH
    assert st.obj(gear).attached_to is None
    # 卸除→留战场→323.7 场地清理召回基地（终态）
    assert st.obj(gear).zone == Zone.BASE and gear in st.base_occupants[first]
    assert any(e["type"] == "KILL" and e["public"].get("uid") == host for e in evs)


def test_end_of_turn_no_trigger_when_conquered(real_defs):
    """本回合已征服 → 卡面条件不满足不注册（383.3 前置）：装备保持贴附、宿主无伤害。"""
    st, first = fresh()
    _register(st, real_defs, UNL_019)
    host, gear = _host_with_gear(st, real_defs, first, UNL_019, bf=0, might=5)
    st.current_request = None
    scoring.score_conquer(st, first, st.battlefields[0])  # 置 conquered_this_turn
    engine.advance(st)
    _pass_chain(st)
    evs = _end_turn_and_resolve(st)
    assert st.obj(gear).attached_to == host
    assert gear in st.obj(host).attachments
    assert not any(e["type"] == "DAMAGE" and e["public"].get("uid") == host for e in evs)
    assert st.turn_player == 1 - first


# ---------------------------------------------------------------- VEN-011 移动触发（383+719.1+317.2.c）
def _host_with_gear_base(st, defs, player: int, gear_id: str, might: int = 3):
    """宿主单位放基地 + 装备贴附（zone=BASE 跟随）。VEN-011 场景：基地→战场移动触发。"""
    _register(st, defs, gear_id)
    uid_host = place_base(st, player, {
        "def_id": f"test:unit-base:{st.next_uid}", "name": "宿主",
        "card_types": {CardType.UNIT}, "cost_energy": might, "cost_power": (Domain.R,),
        "might": might})
    uid_gear = st.new_uid()
    o_host = st.obj(uid_host)
    st.objects[uid_gear] = GameObject(
        uid=uid_gear, def_id=gear_id, owner=player, controller=player,
        zone=Zone.BASE, zone_owner=player, attached_to=uid_host)
    o_host.attachments.append(uid_gear)
    return uid_host, uid_gear


def test_move_trigger_pumps_host(real_defs):
    """宿主带 VEN-011 从基地 STD_MOVE 到战场 → 触发入链结算 → 宿主 might_temp +2（本回合）；
    effective_might 含修正（719.1 me=宿主；触发挂点在 719.3.a 跟随之后）。"""
    from riftsim.resources import effective_might
    st, first = fresh()
    _register(st, real_defs, VEN_011)
    host, gear = _host_with_gear_base(st, real_defs, first, VEN_011, might=3)
    might_before = effective_might(st, host)
    evs = engine.step(st, Action(ActionKind.STD_MOVE, first, host,
                                 {"to": ("battlefield", 0)})).events
    evs += _pass_chain(st)
    o = st.obj(host)
    assert o.zone == Zone.BATTLEFIELD and o.battlefield == 0  # 移动完成（446.3）
    assert st.obj(gear).battlefield == 0  # 719.3.a 贴附跟随
    assert o.might_temp == 2
    assert effective_might(st, host) == might_before + 2
    assert any(e["type"] == "TRIGGER_QUEUED" for e in evs)
    assert any(e["type"] == "RESOLVE" and e["public"].get("pump") == 2
               and e["public"].get("uid") == host for e in evs)


def test_move_trigger_expires_at_end_of_turn(real_defs):
    """317.2.c/d：+2 本回合修正随回合结束清除（3d 失效）。"""
    st, first = fresh()
    _register(st, real_defs, VEN_011)
    host, gear = _host_with_gear_base(st, real_defs, first, VEN_011, might=3)
    engine.step(st, Action(ActionKind.STD_MOVE, first, host, {"to": ("battlefield", 0)}))
    _pass_chain(st)
    assert st.obj(host).might_temp == 2
    _end_turn_and_resolve(st)
    assert st.obj(host).might_temp == 0


def test_move_to_base_does_not_trigger(real_defs):
    """移回基地非「移动到一处战场」→ 不触发。"""
    st, first = fresh()
    _register(st, real_defs, VEN_011)
    host, gear = _host_with_gear(st, real_defs, first, VEN_011, bf=0, might=3)
    evs = engine.step(st, Action(ActionKind.STD_MOVE, first, host,
                                 {"to": ("base", first)})).events
    _pass_chain(st)
    assert st.obj(host).zone == Zone.BASE
    assert st.obj(host).might_temp == 0
    assert not any(e["type"] == "TRIGGER_QUEUED" for e in evs)


# ---------------------------------------------------------------- SFD-190/016 攻守触发（383+464）
def _start_combat_and_resolve(st, bf_index: int = 0):
    """战斗开始全流（advance-context）：身份确立→触发入链→advance 踢 FEPR→双方让过。"""
    from riftsim import combat
    st.current_request = None
    combat.start_combat(st, st.battlefields[bf_index])
    engine.advance(st)
    return _pass_chain(st)


def test_atk_defend_deals_all_enemy_units(real_defs):
    """攻方宿主带 SFD-190 → 对此处全部敌方单位各造成 2；己方单位/宿主不受（「敌方」限定）。"""
    st, first = fresh()
    _register(st, real_defs, SFD_190)
    host, gear = _host_with_gear(st, real_defs, first, SFD_190, bf=0, might=3)
    foe1 = place_battlefield_unit(st, 1 - first, 0, might=4, name="敌1")
    foe2 = place_battlefield_unit(st, 1 - first, 0, might=5, name="敌2")
    ally = place_battlefield_unit(st, first, 0, might=3, name="友军")
    st.battlefields[0].contested_by = first  # 攻方=first
    evs = _start_combat_and_resolve(st)
    assert st.obj(foe1).damage == 2 and st.obj(foe2).damage == 2
    assert st.obj(host).damage == 0 and st.obj(ally).damage == 0
    assert any(e["type"] == "TRIGGER_QUEUED" and e["public"].get("kind") == "trigger" for e in evs)


def test_atk_defend_defender_side_also_fires(real_defs):
    """守方带 SFD-190 同样触发（「我进攻或防守」双身份；464 攻方先、守方后入链）。"""
    st, first = fresh()
    _register(st, real_defs, SFD_190)
    host, gear = _host_with_gear(st, real_defs, 1 - first, SFD_190, bf=0, might=3)
    att1 = place_battlefield_unit(st, first, 0, might=4, name="攻1")
    att2 = place_battlefield_unit(st, first, 0, might=6, name="攻2")
    st.battlefields[0].contested_by = first  # 攻方=first；守方=1-first
    evs = _start_combat_and_resolve(st)
    assert st.obj(att1).damage == 2 and st.obj(att2).damage == 2
    assert st.obj(host).damage == 0


def test_atk_defend_choose_target(real_defs):
    """SFD-016：「对此处的一名敌方单位造成 2」→ 结算时 CHOOSE_MODE 选目标→指定敌方吃 2。"""
    st, first = fresh()
    _register(st, real_defs, SFD_016)
    host, gear = _host_with_gear(st, real_defs, first, SFD_016, bf=0, might=3)
    foe1 = place_battlefield_unit(st, 1 - first, 0, might=4, name="敌1")
    foe2 = place_battlefield_unit(st, 1 - first, 0, might=5, name="敌2")
    st.battlefields[0].contested_by = first
    _start_combat_and_resolve(st)
    r = st.current_request
    assert r and r["kind"] == "choose_mode" and r["options"].get("reason") == "trigger_deal_enemy_here"
    assert sorted(r["options"]["choices"]) == sorted([foe1, foe2])  # 仅此处敌单位
    evs = engine.step(st, Action(ActionKind.RESOLVE_CHOICE, first, None, {"choice": foe2})).events
    assert st.obj(foe2).damage == 2 and st.obj(foe1).damage == 0
    assert any(e["type"] == "EXECUTE" and e["public"].get("trigger_followup") == "deal_enemy_here"
               and e["public"].get("target") == foe2 for e in evs)


def test_atk_defend_not_fired_outside_combat_battlefield(real_defs):
    """宿主不在战斗战场（在另一战场）→ 不触发。"""
    st, first = fresh()
    _register(st, real_defs, SFD_190)
    host, gear = _host_with_gear(st, real_defs, first, SFD_190, bf=1, might=3)
    foe = place_battlefield_unit(st, 1 - first, 0, might=4, name="敌")
    st.battlefields[0].contested_by = first
    evs = _start_combat_and_resolve(st, bf_index=0)
    assert st.obj(foe).damage == 0
    assert not any(e["type"] == "TRIGGER_QUEUED" for e in evs)
