# 清理（318..324，323.1-14 清单 + 322 迭代 + 320/321 抑制由 engine 调度保证）
from __future__ import annotations

from .enums import CardType, EventType, LinkState, Termination, Zone
from .events import emit
from .resources import effective_might, kill, recycle, _end_game
from .state import BattlefieldState, CombatContext, GameState


def win_check(state: GameState) -> bool:
    """323.1：分≥胜利分且高于所有对手→获胜（472/194）。仅清理项 1 与燃尽即时线调用。"""
    if state.ended:
        return True
    ws = state.meta.win_score
    best, best_score = None, -1
    tie = False
    for p in state.players:
        if p.score > best_score:
            best, best_score, tie = p.seat, p.score, False
        elif p.score == best_score:
            tie = True
    if best is not None and best_score >= ws and not tie:
        _end_game(state, best, Termination.SCORE, rule="R-CR-472")
        return True
    return False


def lethal_marked(state: GameState, uid: int) -> bool:
    """致命标记（142.4/323.5）：伤害≥当前战力（伤害>0 才构成致命语境）。"""
    o = state.obj(uid)
    d = state.card_registry[o.def_id]
    if CardType.UNIT not in d.card_types:
        return False
    if o.damage <= 0:
        return False
    return o.damage >= effective_might(state, uid)


def cleanup(state: GameState) -> None:
    """执行清理（318..323.14）并迭代至静默（322）。调用方保证：不在链结算中（321）、
    清理中不确认/结算链项（320）。假设 1v1。"""
    state.cleanups_run += 1
    for _ in range(64):  # 迭代上限防死循环；322 理论上应在有限轮内静默
        if win_check(state):
            return  # 1 胜利检查（终局跳过余项，T-0049）
        changed = False
        for bf in state.battlefields:
            changed |= _item2_identities(state, bf)
        changed |= _item3_board_states(state)          # 3a 挂点 + 3b 致命摧毁
        for bf in state.battlefields:
            changed |= _item4_loss_of_control(state, bf)
        changed |= _item5_recall_misplaced(state)
        for bf in state.battlefields:
            changed |= _items6_7_pending(state, bf)
        for bf in state.battlefields:
            changed |= _item7a_cancel_combat(state, bf)
        for bf in state.battlefields:
            changed |= _item8_clear_contest(state, bf)
        changed |= _items9_10_open(state)
        changed |= _item10a_convert(state)
        if not changed or state.ended:
            return
    from .errors import EngineInvariantError

    raise EngineInvariantError("cleanup did not converge (64 iterations)")


def _item2_identities(state: GameState, bf: BattlefieldState) -> bool:
    """323.2：战斗中攻防身份由 combat 模块即时管理；此处无操作（M1 骨架不作改动）。"""
    return False


def _item3_board_states(state: GameState) -> bool:
    """323.3/3a/3b（323.4/323.5）：绝念入链挂点（骨架池无触发——P1 接入），
    致命单位摧毁；贴附卡随顶部卡由 kill→_untrack 卸除。"""
    changed = False
    for uid in list(state.objects.keys()):
        o = state.objects.get(uid)
        if o is None or o.zone not in (Zone.BASE, Zone.BATTLEFIELD):
            continue
        d = state.card_registry[o.def_id]
        if CardType.UNIT in d.card_types and lethal_marked(state, uid):
            # 3a（323.4）：绝念触发入链挂点——骨架池无[绝念]，P1 在此收集入链
            kill(state, uid, rule="R-CR-323.5", via="lethal")
            changed = True
    return changed


def _units_of(state: GameState, seat: int, bf_index: int) -> list[int]:
    out = []
    b = state.battlefields[bf_index]
    for uid in b.occupants:
        o = state.obj(uid)
        d = state.card_registry[o.def_id]
        if CardType.UNIT in d.card_types and o.controller == seat:
            out.append(uid)
    return out


def _item4_loss_of_control(state: GameState, bf: BattlefieldState) -> bool:
    """323.6（项4）：开环、控制者无其单位在场、无对决/战斗→失去控制。"""
    if bf.controller is None:
        return False
    if bf.showdown_pending or bf.combat is not None or bf.combat_pending or bf.showdown_active:
        return False
    from .enums import TurnMode

    if state.showdown_live():  # 323.6 条件中的法术对决在场 → 抑制（对决进行中不清控制）
        if any(b.showdown_active for b in state.battlefields):
            return False
    if state.chain_live():  # 项4条件：当前回合处于开环状态
        return False
    if _units_of(state, bf.controller, bf.index):
        return False
    old = bf.controller
    bf.controller = None
    bf.contested = False
    bf.contested_by = None
    emit(state, EventType.CLEANUP_ITEM, rule_ids=["R-CR-323.6"],
         public={"battlefield": bf.index, "lost_controller": old})
    return True


def _item5_recall_misplaced(state: GameState) -> bool:
    """323.7（项5）：战场上未贴附的非单位装备/符文→所属者基地；
    非其控制者基地中的常驻牌/符文→所属者基地；
    待命牌控制者与所在战场控制者不同→置所属者废牌堆（107.3.d）。"""
    changed = False
    # 5a 战场上的非单位装备/符文（未贴附）
    for bf in state.battlefields:
        for uid in list(bf.occupants):
            o = state.obj(uid)
            d = state.card_registry[o.def_id]
            if o.attached_to is not None:
                continue
            if d.card_types & {CardType.GEAR, CardType.RUNE} and CardType.UNIT not in d.card_types:
                recycle_to_base(state, uid, rule="R-CR-323.7")
                changed = True
    # 5b 基地中非其控制者的常驻牌/符文
    for seat in (0, 1):
        for uid in list(state.base_occupants[seat]):
            o = state.obj(uid)
            d = state.card_registry[o.def_id]
            if CardType.LEGEND in d.card_types or CardType.BATTLEFIELD in d.card_types:
                continue
            if o.controller != seat and o.attached_to is None:
                recycle_to_base(state, uid, rule="R-CR-323.7")
                changed = True
    # 5c 待命牌失控→废牌堆（107.3.d / 323.7）
    for bf in state.battlefields:
        for uid in list(bf.hidden_slot):
            o = state.obj(uid)
            if bf.controller != o.controller:
                bf.hidden_slot.remove(uid)
                o.snapshot_last_known(0)
                state.players[o.owner].trash.append(uid)
                o.zone, o.zone_owner, o.battlefield = Zone.TRASH, o.owner, None
                o.face_down = False
                emit(state, EventType.CLEANUP_ITEM, rule_ids=["R-CR-323.7", "R-CR-107.3.d"],
                     card_ids=[f"uid:{uid}"], public={"uid": uid, "battlefield": bf.index, "to": "trash"})
                changed = True
    return changed


def recycle_to_base(state: GameState, uid: int, *, rule: str) -> None:
    """召回语义（454..458，非移动 456.1）：至所属者基地。"""
    from .resources import _untrack

    o = state.obj(uid)
    _untrack(state, uid)
    o.zone, o.zone_owner, o.battlefield = Zone.BASE, o.owner, None
    o.face_down = False
    state.base_occupants[o.owner].append(uid)
    emit(state, EventType.RECALL, rule_ids=[rule, "R-CR-456.1"], card_ids=[f"uid:{uid}"],
         public={"uid": uid, "owner": o.owner})


def _items6_7_pending(state: GameState, bf: BattlefieldState) -> bool:
    """323.8/323.9：争夺→对决待发生；争夺场上有敌单位→战斗待发生。"""
    changed = False
    if not bf.contested or bf.contested_by is None:
        return False
    if bf.showdown_active or bf.combat is not None:
        return False
    enemy_uid = bf.contested_by
    other = 1 - enemy_uid
    enemy_units = _units_of(state, other, bf.index)
    if not bf.showdown_pending:
        bf.showdown_pending = True
        emit(state, EventType.CLEANUP_ITEM, rule_ids=["R-CR-323.8"],
             public={"battlefield": bf.index, "showdown_pending": True})
        changed = True
    if enemy_units and not bf.combat_pending:
        bf.combat_pending = True
        emit(state, EventType.CLEANUP_ITEM, rule_ids=["R-CR-323.9"],
             public={"battlefield": bf.index, "combat_pending": True})
        changed = True
    return changed


def _item7a_cancel_combat(state: GameState, bf: BattlefieldState) -> bool:
    """323.10（项7a）：待发生战斗的战场不再有两名敌对玩家单位→取消。"""
    if not bf.combat_pending or bf.combat is not None:
        return False
    sides = {o.controller for o in (state.obj(u) for u in bf.occupants)
             if CardType.UNIT in state.card_registry[o.def_id].card_types}
    if len(sides) < 2:
        bf.combat_pending = False
        emit(state, EventType.CLEANUP_ITEM, rule_ids=["R-CR-323.10"],
             public={"battlefield": bf.index, "combat_pending": False})
        return True
    return False


def _item8_clear_contest(state: GameState, bf: BattlefieldState) -> bool:
    """323.11（项8）：无争夺发起者单位且无对决/战斗→移除争夺。"""
    if not bf.contested or bf.contested_by is None:
        return False
    if bf.showdown_active or bf.combat is not None or bf.combat_pending:
        return False
    if _units_of(state, bf.contested_by, bf.index):
        return False
    bf.contested = False
    by = bf.contested_by
    bf.contested_by = None
    emit(state, EventType.CLEANUP_ITEM, rule_ids=["R-CR-323.11"],
         public={"battlefield": bf.index, "contest_removed": True, "was_by": by})
    return True


def _items9_10_open(state: GameState) -> bool:
    """323.12/13（项9/10）：普通开环时开始待发生对决/战斗。
    单一场次自动开始；多场次由回合玩家选择（323.12/13「由回合玩家选择其中一处」）。"""
    from .actions import DecisionRequest
    from .enums import DecisionKind

    if state.chain_live():
        return False
    if state.showdown_live():
        return False
    pending_sd = [b for b in state.battlefields if b.showdown_pending]
    pending_cb = [b for b in state.battlefields if b.combat_pending]
    if pending_sd and not pending_cb:
        if len(pending_sd) == 1:
            bf = pending_sd[0]
            bf.showdown_pending = False
            from . import showdown

            showdown.start_showdown(state, bf)
            return True
        state.current_request = DecisionRequest(
            DecisionKind.CHOOSE_BATTLEFIELD_NEXT, state.turn_player,
            options={"kind": "showdown", "choices": [b.index for b in pending_sd]},
        ).to_dict()
        return True  # 请求挂起：engine 回答后由 _open_pending_at 打开
    if pending_cb:
        if len(pending_cb) == 1:
            bf = pending_cb[0]
            bf.combat_pending = False
            bf.showdown_pending = False
            from . import showdown

            showdown.start_combat(state, bf)
            return True
        state.current_request = DecisionRequest(
            DecisionKind.CHOOSE_BATTLEFIELD_NEXT, state.turn_player,
            options={"kind": "combat", "choices": [b.index for b in pending_cb]},
        ).to_dict()
        return True
    return False


def _item10a_convert(state: GameState) -> bool:
    """323.14（项10a）：非战斗对决中该场战斗待发生→转为战斗法术对决。"""
    bf_idx = state.showdown_bf
    if bf_idx is None:
        return False
    bf = state.battlefields[bf_idx]
    if bf.combat_pending and bf.showdown_active and bf.combat is None:
        bf.showdown_pending = False
        bf.combat_pending = False
        emit(state, EventType.CLEANUP_ITEM, rule_ids=["R-CR-323.14"],
             public={"battlefield": bf.index, "convert_to": "combat_showdown"})
        from . import combat

        attacker = bf.contested_by if bf.contested_by is not None else state.turn_player
        bf.combat = CombatContext(battlefield=bf.index, attacker=attacker, defender=1 - attacker, step=1)
        # 焦点保持/争夺发起者为攻方（464）；攻防触发挂点（骨架无）
        state.sd_pass = []
        emit(state, EventType.COMBAT_START, rule_ids=["R-CR-464.1"],
             public={"battlefield": bf.index, "attacker": attacker, "defender": 1 - attacker})
        return True
    return False
