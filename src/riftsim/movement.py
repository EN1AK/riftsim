# 移动/召回/待命（MECH-MOVEMENT/RECALL/ACT-HIDE；144/420-421/445-458/811）
from __future__ import annotations

from .actions import Action
from .enums import ActionKind, CardType, EventType, Keyword, Zone
from .errors import IllegalActionError
from .events import emit
from .resources import _untrack
from .state import GameState


def legal_move_actions(state: GameState, player: int) -> list[Action]:
    """标准移动（144.4；144.1.a 主阶段/144.1.b 开环/144.1.c 非对决）。"""
    if state.turn_player != player or state.chain_live() or state.showdown_live():
        return []
    out: list[Action] = []
    # 基地 → 战场（144.4.a）；战场 → 基地（144.4.b）；游走战场→战场（810）
    for uid in state.player_objects(player, board_only=True):
        o = state.obj(uid)
        d = state.card_registry[o.def_id]
        if CardType.UNIT not in d.card_types or o.attached_to is not None:
            continue
        if o.exhausted:
            continue  # 144.2：标准移动支付休眠
        if o.zone == Zone.BASE:
            for bf in state.battlefields:
                if _battlefield_enterable(state, player, bf.index):
                    out.append(Action(ActionKind.STD_MOVE, player, uid, {"to": ("battlefield", bf.index)}))
        elif o.zone == Zone.BATTLEFIELD:
            out.append(Action(ActionKind.STD_MOVE, player, uid, {"to": ("base", player)}))
            from .playing import keywords_of

            if Keyword.GANKING in keywords_of(state, uid):
                for bf in state.battlefields:
                    if bf.index != o.battlefield and _battlefield_enterable(state, player, bf.index):
                        out.append(Action(ActionKind.STD_MOVE, player, uid, {"to": ("battlefield", bf.index)}))
    return out


def _battlefield_enterable(state: GameState, player: int, bf_index: int) -> bool:
    """终点合法性（449.2/144.4.a.1）：不得移入已有 2 名其他玩家控制单位的战场。"""
    bf = state.battlefields[bf_index]
    others = 0
    for uid in bf.occupants:
        o = state.obj(uid)
        d = state.card_registry[o.def_id]
        if CardType.UNIT in d.card_types and o.controller != player:
            others += 1
    return others < 2


def handle_move(state: GameState, action: Action) -> None:
    """执行移动（446.3 立即完成、不开链不可反应；453 完成后清理由 advance 保证）。"""
    player, uid = action.actor, action.source_uid
    o = state.obj(uid)
    d = state.card_registry[o.def_id]
    if CardType.UNIT not in d.card_types:
        raise IllegalActionError(state.step_id, player, action.digest(), "only units move (R-CR-144)")
    if o.controller != player:
        raise IllegalActionError(state.step_id, player, action.digest(), "not your unit (R-CR-188)")
    if o.exhausted:
        raise IllegalActionError(state.step_id, player, action.digest(), "exhausted: std move cost is [E] (R-CR-144.2)")
    kind, idx = action.params["to"]
    if state.chain_live() or state.showdown_live():
        raise IllegalActionError(state.step_id, player, action.digest(), "no move during closed/showdown (R-CR-144.1.b/c)")
    origin = (o.zone, o.battlefield)
    if kind == "battlefield":
        if not _battlefield_enterable(state, player, idx):
            raise IllegalActionError(state.step_id, player, action.digest(), "battlefield crowded (R-CR-449.2)")
        from .playing import keywords_of

        if o.zone == Zone.BATTLEFIELD and Keyword.GANKING not in keywords_of(state, uid):
            raise IllegalActionError(state.step_id, player, action.digest(), "battlefield-to-battlefield needs [游走] (R-CR-144.4.c.1)")
        _untrack(state, uid)
        bf = state.battlefields[idx]
        o.zone, o.zone_owner, o.battlefield = Zone.BATTLEFIELD, None, idx
        bf.occupants.append(uid)
        o.exhausted = True  # 144.2 费用
        emit(state, EventType.MOVE, rule_ids=["R-CR-144.4.a", "R-CR-446.3"], card_ids=[f"uid:{uid}"],
             public={"uid": uid, "from": _loc_str(origin), "to": f"battlefield:{idx}"})
        # 450 进入未争夺且非己方控制的战场→争夺（发起者=移动方）
        if not bf.contested and bf.controller != player:
            bf.contested = True
            bf.contested_by = player
            emit(state, EventType.CONTEST, rule_ids=["R-CR-450.1"], card_ids=[f"uid:{uid}"],
                 public={"battlefield": idx, "by": player})
    else:  # to base（144.4.b）
        _untrack(state, uid)
        o.zone, o.zone_owner, o.battlefield = Zone.BASE, player, None
        state.base_occupants[player].append(uid)
        o.exhausted = True
        emit(state, EventType.MOVE, rule_ids=["R-CR-144.4.b", "R-CR-446.3"], card_ids=[f"uid:{uid}"],
             public={"uid": uid, "from": _loc_str(origin), "to": "base"})
    state.current_request = None  # 移动完成；453 清理由 engine.advance 保证


def _loc_str(origin: tuple) -> str:
    z, bf = origin
    if z == Zone.BATTLEFIELD:
        return f"battlefield:{bf}"
    return z.value if z else "?"


def legal_hide_actions(state: GameState, player: int) -> list[Action]:
    """待命（811.1.b/421.2.a）：己方回合开环；手牌/英雄区带[待命]的卡；付 [A]；
    目标战场：己方控制且无待命牌（107.3.b/c）。"""
    if state.turn_player != player or state.chain_live() or state.showdown_live():
        return []
    from .playing import keywords_of

    out: list[Action] = []
    p = state.players[player]
    if _any_power(p.rune_power) < 1:
        return []  # [A]=任意特性符能 1 点
    for uid in list(p.hand) + list(p.hero_zone):
        if Keyword.HIDDEN not in keywords_of(state, uid):
            continue
        for bf in state.battlefields:
            if bf.controller == player and not bf.hidden_slot:
                out.append(Action(ActionKind.HIDE, player, uid, {"battlefield": bf.index}))
    return out


def _any_power(power: dict[str, int]) -> int:
    return sum(power.values())


def handle_hide(state: GameState, action: Action) -> None:
    from .playing import keywords_of

    player, uid = action.actor, action.source_uid
    o = state.obj(uid)
    p = state.players[player]
    if Keyword.HIDDEN not in keywords_of(state, uid):
        raise IllegalActionError(state.step_id, player, action.digest(), "no [待命] (R-CR-811)")
    if not (uid in p.hand or uid in p.hero_zone):
        raise IllegalActionError(state.step_id, player, action.digest(), "hide from hand/hero only (R-CR-811.1.b)")
    bf = state.battlefields[action.params["battlefield"]]
    if bf.controller != player or bf.hidden_slot:
        raise IllegalActionError(state.step_id, player, action.digest(), "battlefield invalid for hide (R-CR-107.3.b/c)")
    if _any_power(p.rune_power) < 1:
        raise IllegalActionError(state.step_id, player, action.digest(), "need [A] (R-CR-811.1.b)")
    # 支付 [A]：任意特性符能 1 点
    for d in list(p.rune_power):
        p.rune_power[d] -= 1
        if p.rune_power[d] <= 0:
            del p.rune_power[d]
        break
    from .playing import _untrack_source

    _untrack_source(state, uid)
    o.zone, o.zone_owner, o.battlefield = Zone.HIDDEN_SLOT, None, bf.index
    o.face_down = True
    o.entered_turn = state.turn_number
    bf.hidden_slot.append(uid)
    # 待命非打出、不开链（811.1.c.1/2）；公共信息仅"存在一张待命牌"
    emit(state, EventType.PLAY_STEP, rule_ids=["R-CR-811.1.b", "R-CR-421.2.a"],
         public={"player": player, "hide_at": bf.index},
         privileged={"uid": uid})
    state.current_request = None


def recall(state: GameState, uid: int, *, rule: str = "R-CR-455.1") -> None:
    """召回（454..458）：至所属者基地、状态保留；非移动（456.1）。"""
    from .cleanup_sys import recycle_to_base

    recycle_to_base(state, uid, rule=rule)
