# 结算链 + HOT FEPR（325..340；MECH-CHAINS/TASKS-FEPR/FEPR-*）
from __future__ import annotations

from .actions import Action, DecisionRequest
from .enums import ActionKind, CardType, DecisionKind, EventType, Zone
from .errors import IllegalActionError
from .events import emit
from .resources import deal_damage, effective_might, kill, _end_game
from .state import ChainItem, GameState


def push(state: GameState, item: ChainItem) -> ChainItem:
    """入链（329）：追加 pending 项；回合转为闭环（331 派生）。"""
    state.chain_seq += 1
    item.created_seq = state.chain_seq
    state.chain.append(item)
    state.fepr_pass = []
    # 卡牌入链事件由 playing 的步骤 1（354）已发；此处仅技能/触发发入链事件
    if item.kind in ("ability", "trigger", "reflexive"):
        emit(state, EventType.TRIGGER_QUEUED, rule_ids=["R-CR-329"],
             public={"item_id": item.item_id, "kind": item.kind,
                     "controller": item.controller, "seq": item.created_seq})
    return item


def fepr_step(state: GameState) -> None:
    """HOT FEPR 调度（334..340）：先未决任务由 engine.advance 保证；
    确认(337) → 执行(338) → 让过(339) → 结算(340)。"""
    pend = [it for it in state.chain if it.status == "pending"]
    if pend:
        _finalize(state, min(pend, key=lambda it: it.created_seq))
        return
    fin = [it for it in state.chain if it.status == "finalized"]
    if not fin:
        return  # 链空（330）——advance 会继续走阶段/对决
    # 执行窗（338）：两方依次可加入反应；连续让过（339）→结算最新已确认（340）
    if not state.fepr_pass:
        target = fin[-1]
        # 先给非发起者窗口，再给发起者（339 回合序为近似；1v1 双向窗口即完整机会）
        other = 1 - target.controller
        state.current_request = DecisionRequest(
            DecisionKind.REACTION_EXECUTE, other,
            options={"top_item": target.item_id, "reason": "execute_window"},
        ).to_dict()
        state.fepr_pass = ["window", other]
        return
    # fepr_pass = ["window", seat]（等待该 seat 的回答；回答由 handle_execute 处理）
    return


def _finalize(state: GameState, item: ChainItem) -> None:
    """FEPR-确认（337；按加入序）。特殊立即结算分支：
    单位/装备牌与获得资源类技能确认后立即结算（337.2/400.2/429.2）。"""
    item.status = "finalized"
    state.fepr_pass = []
    if item.kind == "card":
        d = state.card_registry[state.obj(item.source_uid).def_id]
        if d.card_types & {CardType.UNIT, CardType.GEAR}:
            emit(state, EventType.FINALIZE, rule_ids=["R-CR-337.2", "R-CR-359.2"],
                 card_ids=[f"uid:{item.source_uid}"],
                 public={"item_id": item.item_id, "immediate": "permanent_enter"})
            _resolve_permanent_enter(state, item)
            return
    if item.kind == "ability" and (item.ability or {}).get("immediate"):
        emit(state, EventType.FINALIZE, rule_ids=["R-CR-337.2", "R-CR-429.2"],
             public={"item_id": item.item_id, "immediate": "gain_resource"})
        from . import playing

        playing.apply_ability_resolution(state, item)
        _remove_item(state, item)
        return
    emit(state, EventType.FINALIZE, rule_ids=["R-CR-337.1"],
         public={"item_id": item.item_id, "controller": item.controller})


def _resolve_permanent_enter(state: GameState, item: ChainItem) -> None:
    """常驻牌确认即入场（359.2）：单位休眠进场（805 急速挂点）；装备/非单位活跃进基地。"""
    from . import playing

    playing.enter_permanent(state, item)
    _remove_item(state, item)


def resolve_top(state: GameState) -> None:
    """FEPR-结算（340）：结算最新已确认项。法术→执行后废牌堆（157）；技能→执行后离链。"""
    fin = [it for it in state.chain if it.status == "finalized"]
    if not fin:
        return
    item = max(fin, key=lambda it: it.created_seq)
    emit(state, EventType.RESOLVE, rule_ids=["R-CR-340.1"],
         public={"item_id": item.item_id, "kind": item.kind, "controller": item.controller})
    from . import playing

    if item.kind == "card":
        playing.resolve_spell(state, item)
    elif item.kind in ("ability", "trigger", "reflexive"):
        playing.apply_ability_resolution(state, item)
    _remove_item(state, item)
    state.fepr_pass = []
    # 链空后的对决焦点传递（346）
    if not state.chain and state.showdown_bf is not None:
        _pass_focus_after_chain(state, item)


def _pass_focus_after_chain(state: GameState, item: ChainItem) -> None:
    """346：玩家行动引发的链结算完→焦点按回合序传递；触发/获得技能引发→不传递（346.1）。
    本函数只维护 focus/sd_pass；SHOWDOWN_FOCUS 窗口由 engine.advance 统一重建。"""
    origin = (item.ability or {}).get("origin", "player_action") if item.kind != "card" else "player_action"
    if item.kind == "ability" and (item.ability or {}).get("immediate"):
        origin = "gain_ability"
    if origin != "player_action":
        return
    if state.focus is None:
        return
    state.focus = 1 - state.focus  # 1v1 回合序即交换
    state.sd_pass = []


def _remove_item(state: GameState, item: ChainItem) -> None:
    if item in state.chain:
        state.chain.remove(item)


def legal_execute_actions(state: GameState, req: DecisionRequest) -> list[Action]:
    """执行窗合法动作：加入反应（[反应]/[迅捷] 或支付窗获得资源技能）或让过。"""
    from . import playing

    player = req.player
    out = playing.legal_reactions(state, player)
    out.append(Action(ActionKind.PASS, player))
    return out


def handle_execute(state: GameState, req: DecisionRequest, action: Action) -> None:
    from . import playing

    if action.kind == ActionKind.PASS:
        _execute_pass(state, req.player)
        return
    if action.kind in (ActionKind.PLAY_CARD, ActionKind.ACTIVATE_ABILITY):
        state.fepr_pass = []  # 加入新反应→连续让过重置（339）
        state.current_request = None
        if action.kind == ActionKind.PLAY_CARD:
            playing.handle_play_card(state, action, in_reaction=True)
        else:
            playing.handle_activate(state, action, in_reaction=True)
        return
    raise IllegalActionError(state.step_id, action.actor, action.digest(), "execute window: invalid kind")


def _execute_pass(state: GameState, player: int) -> None:
    """FEPR-让过（339）状态机：
    fepr_pass=["window", X] 表示等待 X；X 让过→转 ["passed", X] 并等另一方；
    另一方再让过→连续全员让过→结算最新已确认项（340）。"""
    state.current_request = None
    emit(state, EventType.PASS, rule_ids=["R-CR-339.1"], public={"player": player})
    if len(state.fepr_pass) == 2 and state.fepr_pass[0] == "passed" and state.fepr_pass[1] == 1 - player:
        # 对方刚让过、本玩家再让过 → 全员连续让过
        state.fepr_pass = []
        resolve_top(state)
        return
    other = 1 - player
    state.fepr_pass = ["passed", player]
    state.current_request = DecisionRequest(
        DecisionKind.REACTION_EXECUTE, other, options={"reason": "execute_window"}
    ).to_dict()


def handle_choice(state: GameState, req: DecisionRequest, action: Action) -> None:
    """CHOOSE_* 回答。reason="trigger_discard"：383 触发弃抽续段（弃 1 手牌→抽 N，422.1+413.1）。"""
    options = req.options or {}
    if options.get("reason") == "trigger_discard":
        from .resources import discard, draw

        player = req.player
        uid = action.params.get("choice")
        if uid not in state.players[player].hand:
            raise IllegalActionError(state.step_id, action.actor, action.digest(),
                                     "trigger_discard: choice not in hand (R-CR-422.1)")
        state.current_request = None
        discard(state, player, [uid], rule="R-CR-422.1")
        n = int(options.get("then_draw") or 0)
        if n > 0:
            draw(state, player, n, rule="R-CR-413.1")
        emit(state, EventType.EXECUTE, rule_ids=["R-CR-383.3"],
             public={"player": player, "trigger_followup": "discard_draw",
                     "item_id": options.get("item_id")})
        return
    if options.get("reason") == "trigger_deal_enemy_here":
        # 383 触发「此处一名敌方单位」目标续段：结算时选择（时点近似）+ 复查（359.3.e.9）
        from .resources import deal_damage

        player = req.player
        uid = action.params.get("choice")
        o = state.objects.get(uid)
        legal_target = (
            o is not None and o.zone == Zone.BATTLEFIELD and o.attached_to is None
            and o.controller != player
            and CardType.UNIT in state.card_registry[o.def_id].card_types
        )
        if not legal_target:
            raise IllegalActionError(state.step_id, action.actor, action.digest(),
                                     "trigger_deal_enemy_here: not a legal foe unit (R-CR-359.3.e.9)")
        state.current_request = None
        deal_damage(state, uid, int(options.get("damage") or 0),
                    source=f"trigger:uid{options.get('source_uid')}", rule="R-CR-417.1")
        emit(state, EventType.EXECUTE, rule_ids=["R-CR-383.3"],
             public={"player": player, "trigger_followup": "deal_enemy_here",
                     "item_id": options.get("item_id"), "target": uid})
        return
    raise IllegalActionError(state.step_id, action.actor, action.digest(),
                             f"choose not supported in skeleton pool: {req.kind}")
