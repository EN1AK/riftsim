# legal_actions：六门判定的装配（rule_dependencies.md §3；MECH-*）。
# 每个分支产出完整合法 Action 实例；step() 只接受其中的成员。
from __future__ import annotations

import itertools
from typing import Any

from .actions import Action, DecisionRequest
from .enums import ActionKind, DecisionKind
from .state import GameState


def legal_actions(state: GameState, player: int) -> list[Action]:
    """玩家当前全部合法动作（docs/api_contract.md：非请求玩家为空，终局为空）。
    CONCEDE 恒合法（650.1）——任一未终局状态都可认输。"""
    if state.ended:
        return []
    out: list[Action] = []
    if state.current_request:
        req = DecisionRequest.from_dict(state.current_request)
        if req.player == player:
            out.extend(legal_for_request(state, req))
    out.append(Action(ActionKind.CONCEDE, player))
    return out


def legal_for_request(state: GameState, req: DecisionRequest) -> list[Action]:
    k = req.kind
    if k == DecisionKind.MULLIGAN:
        return _mulligan_actions(state, req)
    if k == DecisionKind.MAIN_ACTION:
        from . import playing, movement

        acts = [Action(ActionKind.END_MAIN, req.player)]
        acts.extend(playing.legal_play_actions(state, req.player))
        acts.extend(playing.legal_activate_actions(state, req.player))
        acts.extend(movement.legal_move_actions(state, req.player))
        acts.extend(movement.legal_hide_actions(state, req.player))
        return acts
    if k == DecisionKind.REACTION_EXECUTE:
        from . import chain_sys

        return chain_sys.legal_execute_actions(state, req)
    if k == DecisionKind.SHOWDOWN_FOCUS:
        from . import showdown

        return showdown.legal_focus_actions(state, req)
    if k == DecisionKind.ASSIGN_DAMAGE:
        from . import combat

        return combat.legal_assign_actions(state, req)
    if k == DecisionKind.CHOOSE_BATTLEFIELD_NEXT:
        return [
            Action(ActionKind.RESOLVE_CHOICE, req.player, params={"battlefield": i})
            for i in req.options["choices"]
        ]
    if k in (DecisionKind.CHOOSE_TARGETS, DecisionKind.CHOOSE_LOCATION, DecisionKind.CHOOSE_MODE):
        return [
            Action(ActionKind.RESOLVE_CHOICE, req.player, params={"choice": c})
            for c in req.options.get("choices", [])
        ]
    if k == DecisionKind.ORDER_TRIGGERS:
        return [
            Action(ActionKind.RESOLVE_CHOICE, req.player, params={"order": o})
            for o in req.options.get("orders", [])
        ]
    return []


def _mulligan_actions(state: GameState, req: DecisionRequest) -> list[Action]:
    hand = list(state.players[req.player].hand)
    out = [Action(ActionKind.RESOLVE_CHOICE, req.player, params={"set_aside": []})]
    max_n = min(req.options.get("max_set_aside", 2), len(hand))
    for n in range(1, max_n + 1):
        for combo in itertools.combinations(hand, n):
            out.append(Action(ActionKind.RESOLVE_CHOICE, req.player, params={"set_aside": list(combo)}))
    return out
