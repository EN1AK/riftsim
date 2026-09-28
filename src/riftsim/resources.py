# 资源与游戏行动原子（MECH-RUNE-POOLS / MECH-ACT-*；413/416/417/418/422/428/429/430/431/444）
from __future__ import annotations

from .enums import CardType, Domain, EventType, Termination, Zone
from .events import emit
from .rng import STREAM_BURNOUT_SHUFFLE, STREAM_RECYCLE_ORDER
from .state import GameState


def effective_might(state: GameState, uid: int) -> int:
    """单位当前战力（R-CR-143/147/703/+临时修正）。M1 线性：印刷+增益+临时；
    P1 由 MECH-LAYERS 全量接管。"""
    o = state.obj(uid)
    d = state.card_registry[o.def_id]
    base = d.might or 0
    temp = o.might_temp
    buff = o.buffs  # 703：每个增益 +1[M]
    for m in state.effects.continuous:
        if m.target_uid == uid:
            temp += m.might_add
    return base + buff + temp


def add_energy(state: GameState, seat: int, n: int) -> None:
    """获得法力（429；入符文池 165）。"""
    state.players[seat].rune_energy += n
    emit(state, EventType.EXECUTE, rule_ids=["R-CR-429.1"], public={"player": seat, "gain_energy": n})


def add_power(state: GameState, seat: int, domain: Domain, n: int = 1) -> None:
    p = state.players[seat]
    p.rune_power[domain.value] = p.rune_power.get(domain.value, 0) + n
    emit(state, EventType.EXECUTE, rule_ids=["R-CR-429.1"], public={"player": seat, "gain_power": domain.value, "n": n})


def clear_pool(state: GameState, seat: int, *, rule: str) -> None:
    """清空符文池（167）。事件可观测。"""
    p = state.players[seat]
    if p.rune_energy or p.rune_power:
        p.rune_energy = 0
        p.rune_power = {}
        emit(state, EventType.POOL_CLEAR, rule_ids=[rule], public={"player": seat})


def clear_all_pools(state: GameState, *, rule: str) -> None:
    for s in (0, 1):
        clear_pool(state, s, rule=rule)


def can_pay(state: GameState, seat: int, energy: int, power: dict[str, int]) -> bool:
    """支付能力判定（357）：法力任意、符能须特性匹配（134）。"""
    p = state.players[seat]
    if p.rune_energy < energy:
        return False
    for d, n in power.items():
        if p.rune_power.get(d, 0) < n:
            return False
    return True


def pay_cost(state: GameState, seat: int, energy: int, power: dict[str, int], *, rule: str = "R-CR-357.1") -> None:
    """执行支付（357）。调用方须先 can_pay；非资源费用（[E]/回收/弃置）在调用处执行。"""
    p = state.players[seat]
    p.rune_energy -= energy
    for d, n in power.items():
        p.rune_power[d] -= n
        if p.rune_power[d] <= 0:
            del p.rune_power[d]
    emit(state, EventType.PAID, rule_ids=[rule, "R-CR-444.1"], public={"player": seat, "energy": energy, "power": dict(power)})


def check_burnout_win(state: GameState, candidate: int) -> bool:
    """燃尽分数即时胜利（431.3.c.1：无需等待清理）。"""
    if state.ended:
        return True
    ws = state.meta.win_score
    c, o = state.players[candidate], state.players[1 - candidate]
    if c.score >= ws and c.score > o.score:
        _end_game(state, candidate, Termination.BURNOUT, rule="R-CR-431.3.c.1")
        return True
    return False


def burnout(state: GameState, seat: int) -> None:
    """燃尽（431/431.4 限定行动）：废牌堆洗入主牌堆→选对手得 1 分→原动作继续。
    废牌堆空则循环得分（431.3.c 例），直到对手立即获胜（431.3.c.1）。"""
    while True:
        p = state.players[seat]
        if p.trash:
            p.main_deck = list(p.trash) + list(p.main_deck)
            p.trash = []
            state.rng.shuffle(STREAM_BURNOUT_SHUFFLE, p.main_deck)
        for uid in p.main_deck:
            state.obj(uid).zone = Zone.MAIN_DECK
            state.obj(uid).zone_owner = seat
        opp = 1 - seat  # 1v1：燃尽玩家选择对手得分（194.1.d；仅一名）
        state.players[opp].score += 1
        emit(
            state, EventType.BURNOUT, rule_ids=["R-CR-431.2", "R-CR-194.1.d"],
            public={"player": seat, "score_to": opp, "score": state.players[opp].score},
        )
        if check_burnout_win(state, opp):
            return
        if state.players[seat].main_deck:
            return
        # 主牌堆仍空（废牌堆空）→再次燃尽（431.3 循环，直至对手胜利必然终止）
        if state.ended:
            return


def draw(state: GameState, seat: int, n: int = 1, *, rule: str = "R-CR-413") -> list[int]:
    """抽牌（413；431.1.a 尽可能抽→燃尽→再抽剩余）。"""
    got: list[int] = []
    for _ in range(n):
        if state.ended:
            break
        if not state.players[seat].main_deck:
            emit(state, EventType.BURNOUT, rule_ids=[rule], public={"player": seat, "trigger": "empty_deck"})
            burnout(state, seat)
            if state.ended or not state.players[seat].main_deck:
                break
        uid = state.players[seat].main_deck.pop()  # 牌堆顶
        state.players[seat].hand.append(uid)
        o = state.obj(uid)
        o.zone, o.zone_owner, o.battlefield = Zone.HAND, seat, None
        got.append(uid)
    emit(state, EventType.DRAW, rule_ids=[rule], public={"player": seat, "count": len(got)},
         privileged={"uids": got})
    return got


def channel(state: GameState, seat: int, n: int) -> list[int]:
    """召出（430/315.3.b）：从符文牌堆顶召 n 张、活跃进场于控制者基地（107.1.c）。
    空堆：OPEN-6 暂定跳过（不燃尽——431.1 仅覆盖主牌堆）。"""
    out: list[int] = []
    for _ in range(n):
        deck = state.players[seat].rune_deck
        if not deck:
            emit(state, EventType.CHANNEL, rule_ids=["R-CR-430.1"], public={"player": seat, "skipped": "empty_rune_deck"})
            break
        uid = deck.pop()
        o = state.obj(uid)
        o.zone, o.zone_owner, o.battlefield = Zone.BASE, seat, None
        o.exhausted = False  # 430.1 默认活跃
        o.entered_turn = state.turn_number
        state.base_occupants[seat].append(uid)
        out.append(uid)
        emit(state, EventType.CHANNEL, rule_ids=["R-CR-430.1"], card_ids=[f"uid:{uid}"],
             public={"player": seat, "uid": uid})
    return out


def recycle(state: GameState, uid: int, *, rule: str = "R-CR-416.1") -> None:
    """回收（416）：置于相应牌堆底。主牌堆卡→所属者主牌堆底；符文→所属者符文牌堆底。"""
    o = state.obj(uid)
    _untrack(state, uid)
    p = state.players[o.owner]
    d = state.card_registry[o.def_id]
    if CardType.RUNE in d.card_types:
        p.rune_deck.insert(0, uid)  # 底部（list[0]=底）
        o.zone, o.zone_owner = Zone.RUNE_DECK, o.owner
        kind = "rune"
    else:
        p.main_deck.insert(0, uid)
        o.zone, o.zone_owner = Zone.MAIN_DECK, o.owner
        kind = "main"
    o.battlefield = None
    o.face_down = False
    emit(state, EventType.RECYCLE, rule_ids=[rule], card_ids=[f"uid:{uid}"],
         public={"owner": o.owner, "kind": kind})


def recycle_many_main(state: GameState, uids: list[int], owner: int, *, rule: str = "R-CR-416.5") -> None:
    """多张同时回主牌堆：随机顺序置底（416.5，随机序走 recycle_order 流）。"""
    order = list(uids)
    state.rng.shuffle(STREAM_RECYCLE_ORDER, order)
    for uid in order:
        recycle(state, uid, rule=rule)


def deal_damage(state: GameState, uid: int, n: int, *, source: str = "", rule: str = "R-CR-417.1") -> None:
    """造成伤害（417）：累积伤害标记；致命由清理 3b（323.5）统一摧毁。"""
    if n <= 0:
        return
    o = state.obj(uid)
    o.damage += n
    emit(state, EventType.DAMAGE, rule_ids=[rule], card_ids=[f"uid:{uid}"],
         public={"uid": uid, "amount": n, "total": o.damage, "source": source})


def heal(state: GameState, uid: int, n: int, *, rule: str = "R-CR-418.1") -> None:
    o = state.obj(uid)
    removed = min(o.damage, n)
    o.damage -= removed
    emit(state, EventType.HEAL, rule_ids=[rule], card_ids=[f"uid:{uid}"],
         public={"uid": uid, "removed": removed})


def kill(state: GameState, uid: int, *, rule: str = "R-CR-428.1", via: str = "instruct") -> None:
    """摧毁（428）：绝念挂点（808.1.d.2/3 last_known 记录；骨架池无绝念卡——P1 接入链）。"""
    o = state.obj(uid)
    d = state.card_registry[o.def_id]
    if CardType.UNIT in d.card_types or CardType.GEAR in d.card_types:
        o.snapshot_last_known(effective_might(state, uid))
    _untrack(state, uid)
    p = state.players[o.owner]
    p.trash.append(uid)
    o.zone, o.zone_owner, o.battlefield = Zone.TRASH, o.owner, None
    o.face_down = False
    o.buffs = 0  # 705：离开游戏移除增益
    emit(state, EventType.KILL, rule_ids=[rule], card_ids=[f"uid:{uid}"],
         public={"uid": uid, "owner": o.owner, "via": via})


def discard(state: GameState, seat: int, uids: list[int], *, rule: str = "R-CR-422.1") -> None:
    for uid in uids:
        if uid not in state.players[seat].hand:
            continue
        state.players[seat].hand.remove(uid)
        o = state.obj(uid)
        state.players[o.owner].trash.append(uid)
        o.zone, o.zone_owner, o.battlefield = Zone.TRASH, o.owner, None
    emit(state, EventType.DISCARD, rule_ids=[rule], public={"player": seat, "count": len(uids)},
         privileged={"uids": list(uids)})


def _untrack(state: GameState, uid: int) -> None:
    """从当前区域移除 uid（不改变 o.zone——调用方负责）。"""
    o = state.obj(uid)
    if o.zone == Zone.BASE and o.zone_owner is not None:
        if uid in state.base_occupants[o.zone_owner]:
            state.base_occupants[o.zone_owner].remove(uid)
    elif o.zone == Zone.BATTLEFIELD and o.battlefield is not None:
        b = state.battlefields[o.battlefield]
        if uid in b.occupants:
            b.occupants.remove(uid)
    elif o.zone == Zone.HIDDEN_SLOT and o.battlefield is not None:
        b = state.battlefields[o.battlefield]
        if uid in b.hidden_slot:
            b.hidden_slot.remove(uid)
    else:
        p = state.players[o.zone_owner] if o.zone_owner is not None else None
        if p is not None:
            for lst in (p.hand, p.main_deck, p.rune_deck, p.trash, p.banish, p.hero_zone, p.legend_zone, p.aside):
                if uid in lst:
                    lst.remove(uid)
                    break
    # 贴附关系清理（719.5：顶部卡离场→贴附卡卸除留在当前区域）
    for att_uid in list(o.attachments):
        a = state.obj(att_uid)
        a.attached_to = None
        o.attachments.remove(att_uid)
        # 卸除后留在 top 卡原区域
        if o.zone in (Zone.BASE, Zone.BATTLEFIELD):
            a.zone, a.zone_owner, a.battlefield = o.zone, o.zone_owner, o.battlefield
            if o.zone == Zone.BASE and o.zone_owner is not None:
                state.base_occupants[o.zone_owner].append(att_uid)
            elif o.zone == Zone.BATTLEFIELD and o.battlefield is not None:
                state.battlefields[o.battlefield].occupants.append(att_uid)
            emit(state, EventType.DETACH, rule_ids=["R-CR-719.5"], card_ids=[f"uid:{att_uid}"],
                 public={"uid": att_uid, "stayed_zone": o.zone.value, "battlefield": o.battlefield})


def _end_game(state: GameState, winner: int, reason: Termination, *, rule: str) -> None:
    state.ended = True
    state.winner = winner
    state.termination = reason
    state.current_request = None
    emit(state, EventType.WIN, rule_ids=[rule], public={"winner": winner, "reason": reason.value})
