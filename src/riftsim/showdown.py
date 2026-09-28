# 法术对决（341..348；MECH-SHOWDOWNS/FOCUS）
from __future__ import annotations

from .actions import Action, DecisionRequest
from .enums import ActionKind, DecisionKind, EventType
from .errors import IllegalActionError
from .events import emit
from .state import BattlefieldState, GameState


def start_showdown(state: GameState, bf: BattlefieldState) -> None:
    """清理项 9：开始非战斗法术对决（344）。焦点=争夺发起者（345）。"""
    bf.showdown_active = True
    state.showdown_bf = bf.index
    state.focus = bf.contested_by
    state.sd_pass = []
    state.priority = None
    emit(state, EventType.SHOWDOWN_START, rule_ids=["R-CR-344.1", "R-CR-345.1"],
         public={"battlefield": bf.index, "combat": False, "focus": state.focus})
    state.current_request = DecisionRequest(DecisionKind.SHOWDOWN_FOCUS, state.focus).to_dict()


def legal_focus_actions(state: GameState, req: DecisionRequest) -> list[Action]:
    """对决焦点行动（347）：打出（[迅捷]）/激活（[迅捷]）/让过焦点。"""
    from . import playing

    out = playing.legal_reactions(state, req.player)
    out.append(Action(ActionKind.PASS, req.player))
    return out


def handle_focus(state: GameState, req: DecisionRequest, action: Action) -> None:
    from . import playing

    if action.kind == ActionKind.PASS:
        _focus_pass(state, req.player)
        return
    if action.kind in (ActionKind.PLAY_CARD, ActionKind.ACTIVATE_ABILITY):
        state.sd_pass = []
        state.current_request = None
        if action.kind == ActionKind.PLAY_CARD:
            playing.handle_play_card(state, action, in_reaction=True)
        else:
            playing.handle_activate(state, action, in_reaction=True)
        return
    raise IllegalActionError(state.step_id, action.actor, action.digest(), "focus window: invalid kind (R-CR-347)")


def _focus_pass(state: GameState, player: int) -> None:
    """焦点让过（347/348）：全员连续让过→对决关闭。"""
    state.current_request = None
    emit(state, EventType.PASS, rule_ids=["R-CR-347.1"], public={"player": player, "focus_pass": True})
    if state.sd_pass and state.sd_pass[-1] == 1 - player:
        # 双人连续让过 → 关闭
        end_showdown(state, state.battlefields[state.showdown_bf])
        return
    state.sd_pass = [player]
    nxt = 1 - player
    state.focus = nxt
    state.current_request = DecisionRequest(DecisionKind.SHOWDOWN_FOCUS, nxt).to_dict()


def end_showdown(state: GameState, bf: BattlefieldState) -> None:
    """对决关闭（348）。战斗对决由 combat 模块走 step2；非战斗：
    唯一留场玩家确立控制（348.2；未得分→征服）；不清除控制时维持争夺（190）。"""
    if bf.combat is not None:
        from . import combat

        combat.showdown_closed(state, bf)
        return
    emit(state, EventType.SHOWDOWN_END, rule_ids=["R-CR-348.2"], public={"battlefield": bf.index})
    bf.showdown_active = False
    state.showdown_bf = None
    state.focus = None
    state.sd_pass = []
    sides = _sides_with_units(state, bf)
    if len(sides) == 1:
        winner = next(iter(sides))
        _establish_control(state, bf, winner, rule="R-CR-348.2")
    # 双方皆在场或皆不在场：维持争夺（190）；由清理 7a/8 项后续收敛


def _sides_with_units(state: GameState, bf: BattlefieldState) -> set[int]:
    out = set()
    for uid in bf.occupants:
        o = state.obj(uid)
        from .enums import CardType

        if CardType.UNIT in state.card_registry[o.def_id].card_types:
            out.add(o.controller)
    return out


def _establish_control(state: GameState, bf: BattlefieldState, player: int, *, rule: str) -> None:
    """确立控制通用（348.2/466.5）：清争夺、移除异侧待命牌、征服检查。"""
    from .scoring import score_conquer

    first_time = bf.controller != player
    bf.controller = player
    bf.contested = False
    bf.contested_by = None
    for uid in list(bf.hidden_slot):
        o = state.obj(uid)
        if o.controller != player:
            from .enums import Zone

            bf.hidden_slot.remove(uid)
            state.players[o.owner].trash.append(uid)
            o.zone, o.zone_owner, o.battlefield = Zone.TRASH, o.owner, None
            o.face_down = False
            emit(state, EventType.CLEANUP_ITEM, rule_ids=["R-CR-466.5.c"],
                 card_ids=[f"uid:{uid}"], public={"uid": uid, "to": "trash"})
    emit(state, EventType.CLEANUP_ITEM, rule_ids=[rule],
         public={"battlefield": bf.index, "controller": player})
    if first_time:
        score_conquer(state, player, bf)


def start_combat(state: GameState, bf: BattlefieldState) -> None:
    from . import combat

    combat.start_combat(state, bf)
