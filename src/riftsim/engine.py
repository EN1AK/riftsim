# step()/transition 主入口 + 主循环调度（architecture §5 不变量）
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import cleanup_sys, legality, phaser
from .actions import Action, DecisionRequest
from .config import GameConfig
from .enums import ActionKind, DecisionKind, EventType, Phase, Termination, Zone
from .errors import EngineInvariantError, IllegalActionError
from .events import drain_events, emit
from .snapshot import state_hash
from .state import GameState


def reset(seed: int, config: GameConfig | None = None) -> GameState:
    from .setup import reset as _reset

    return _reset(seed, config)


def observe(state: GameState, player: int) -> dict:
    from .observation import observe as _observe

    return _observe(state, player)


def legal_actions(state: GameState, player: int) -> list[Action]:
    return legality.legal_actions(state, player)


@dataclass
class StepResult:
    state: GameState
    events: list[dict]
    request: DecisionRequest | None
    done: bool
    info: dict[str, Any]


def step(state: GameState, action: Action) -> StepResult:
    """对一个决策点提交回答（architecture §3）。原地修改 state（调用方用 clone/snapshot 保旧值）。"""
    if state.ended:
        raise IllegalActionError(state.step_id, action.actor, action.digest(), "game already ended (R-CR-196)")
    # CONCEDE 恒合法（650.1）
    if action.kind == ActionKind.CONCEDE:
        if action.actor not in (0, 1):
            raise IllegalActionError(state.step_id, action.actor, action.digest(), "unknown player")
        before = state_hash(state)
        _handle_concede(state, action.actor)
        return _finish_step(state, before)

    if state.current_request is None:
        raise IllegalActionError(state.step_id, action.actor, action.digest(), "engine not awaiting action (R-CR-334)")
    req = DecisionRequest.from_dict(state.current_request)
    if action.actor != req.player:
        raise IllegalActionError(
            state.step_id, action.actor, action.digest(),
            f"not actor's request (R-CR-312): request player={req.player}",
        )
    legal = legality.legal_for_request(state, req)
    if not any(_same(a, action) for a in legal):
        raise IllegalActionError(
            state.step_id, action.actor, action.digest(),
            "action not in legal set (R-CR-334/358)", legal_digest=repr([a.digest() for a in legal][:20]),
        )
    before = state_hash(state)
    _dispatch(state, req, action)
    return _finish_step(state, before)


def _finish_step(state: GameState, before: str) -> StepResult:
    state.step_id += 1
    advance(state)
    after = state_hash(state)
    events = drain_events(state)
    for e in events:
        e["before_state_hash"] = e["before_state_hash"] or before
        e["after_state_hash"] = after
    if state.step_id >= state.meta.max_steps and not state.ended:
        from .resources import _end_game

        _end_game(state, -1, Termination.TRUNCATED, rule="engine:max_steps")
        state.winner = None
        ev = drain_events(state)
        for e in ev:
            e["before_state_hash"] = e["before_state_hash"] or before
            e["after_state_hash"] = state_hash(state)
        events.extend(ev)
    return StepResult(
        state=state,
        events=events,
        request=DecisionRequest.from_dict(state.current_request) if state.current_request else None,
        done=state.ended,
        info={"invalid_action_count": state.invalid_action_count},
    )


def _same(a: Action, b: Action) -> bool:
    return a.kind == b.kind and a.actor == b.actor and a.source_uid == b.source_uid and a.digest() == b.digest()


def _dispatch(state: GameState, req: DecisionRequest, action: Action) -> None:
    k, ak = req.kind, action.kind
    if k == DecisionKind.MULLIGAN:
        _handle_mulligan(state, req, action)
        return
    if k == DecisionKind.MAIN_ACTION:
        if ak == ActionKind.END_MAIN:
            state.current_request = None
            phaser.end_turn(state)
            state.sub_step = "pending_start"
            return
        from . import movement, playing

        if ak == ActionKind.PLAY_CARD:
            playing.handle_play_card(state, action)
            return
        if ak == ActionKind.ACTIVATE_ABILITY:
            playing.handle_activate(state, action)
            return
        if ak == ActionKind.STD_MOVE:
            movement.handle_move(state, action)
            return
        if ak == ActionKind.HIDE:
            movement.handle_hide(state, action)
            return
    if k == DecisionKind.REACTION_EXECUTE:
        from . import chain_sys

        chain_sys.handle_execute(state, req, action)
        return
    if k == DecisionKind.SHOWDOWN_FOCUS:
        from . import showdown

        showdown.handle_focus(state, req, action)
        return
    if k == DecisionKind.ASSIGN_DAMAGE:
        from . import combat

        combat.handle_assign(state, req, action)
        return
    if k == DecisionKind.CHOOSE_BATTLEFIELD_NEXT:
        state.current_request = None
        _open_pending_at(state, action.params["battlefield"])
        return
    if k in (DecisionKind.CHOOSE_TARGETS, DecisionKind.CHOOSE_LOCATION, DecisionKind.CHOOSE_MODE,
             DecisionKind.ORDER_TRIGGERS):
        from . import chain_sys

        chain_sys.handle_choice(state, req, action)
        return
    raise IllegalActionError(state.step_id, action.actor, action.digest(), f"unhandled request {k}")


def advance(state: GameState) -> None:
    """规则自动推进至下一个决策点或终局（architecture §5 主循环）。"""
    guard = 0
    while not state.ended and state.current_request is None:
        guard += 1
        if guard > 4096:
            raise EngineInvariantError(f"advance did not reach a decision point (step={state.step_id})")
        cleanup_sys.cleanup(state)
        if state.ended or state.current_request is not None:
            continue
        if state.chain:
            from . import chain_sys

            chain_sys.fepr_step(state)
            continue
        if state.sub_step == "pending_start":
            state.sub_step = ""
            phaser.start_turn(state)
            continue
        if state.phase == Phase.SETUP:
            if len(state.mulligan_set) == 2 and not state.current_request:
                phaser.start_turn(state)
                continue
            return
        # 对决焦点窗重建：对决/战斗对决进行中、链空且未在伤害分配等自有请求中
        if state.showdown_bf is not None and not state.chain_live() and state.current_request is None:
            bf = state.battlefields[state.showdown_bf]
            if state.focus is None and bf.combat is not None:
                state.focus = bf.combat.attacker
            elif state.focus is None:
                state.focus = bf.contested_by if bf.contested_by is not None else state.turn_player
            state.sd_pass = []
            state.current_request = DecisionRequest(
                DecisionKind.SHOWDOWN_FOCUS, state.focus
            ).to_dict()
            continue
        # 主阶段行动窗重开：普通开环且不在对决/连锁中（R-CR-305/335）
        if (
            state.phase == Phase.MAIN
            and not state.chain_live()
            and not state.showdown_live()
            and state.current_request is None
        ):
            state.priority = state.turn_player
            state.current_request = DecisionRequest(
                DecisionKind.MAIN_ACTION, state.turn_player
            ).to_dict()
            continue
        return


def _handle_mulligan(state: GameState, req: DecisionRequest, action: Action) -> None:
    from .resources import draw, recycle_many_main

    seat = req.player
    set_aside = list(action.params.get("set_aside", []))
    p = state.players[seat]
    if len(set_aside) > req.options.get("max_set_aside", 2):
        raise IllegalActionError(state.step_id, seat, action.digest(), "mulligan > 2 (R-CR-117.1)")
    if any(u not in p.hand for u in set_aside):
        raise IllegalActionError(state.step_id, seat, action.digest(), "set_aside not in hand (R-CR-117.1)")
    for u in set_aside:
        p.hand.remove(u)
        p.aside.append(u)
        o = state.obj(u)
        o.zone, o.zone_owner = Zone.ASIDE, seat
    draw(state, seat, len(set_aside), rule="R-CR-117.2")
    emit(state, EventType.MULLIGAN, rule_ids=["R-CR-117.1", "R-CR-117.2", "R-CR-117.3", "R-CR-416.1"],
         public={"player": seat, "set_aside_count": len(set_aside)},
         privileged={"set_aside": set_aside})
    recycle_many_main(state, set_aside, seat)
    state.mulligan_set.add(seat)
    state.current_request = None
    if len(state.mulligan_set) < 2:
        nxt = 1 - seat
        state.current_request = DecisionRequest(
            DecisionKind.MULLIGAN, nxt, options={"max_set_aside": 2}
        ).to_dict()


def _handle_concede(state: GameState, actor: int) -> None:
    from .resources import _end_game

    state.players[actor].conceded = True
    emit(state, EventType.CONCEDE, rule_ids=["R-CR-650.1", "R-CR-651"], public={"player": actor})
    _end_game(state, 1 - actor, Termination.CONCEDE, rule="R-CR-195.1")


def _open_pending_at(state: GameState, bf_index: int) -> None:
    """项 9/10 回答：在指定战场开始对决/战斗。"""
    bf = state.battlefields[bf_index]
    if bf.combat_pending:
        bf.combat_pending = False
        bf.showdown_pending = False
        from . import showdown  # circular-safe：运行期导入

        showdown.start_combat(state, bf)
    elif bf.showdown_pending:
        bf.showdown_pending = False
        from . import showdown

        showdown.start_showdown(state, bf)
    else:
        raise EngineInvariantError(f"open_pending_at: nothing pending at bf {bf_index}")
