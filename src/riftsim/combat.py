# 战斗（459..466；MECH-COMBAT/STEP1/STEP2/STEP3）
from __future__ import annotations

from . import cleanup_sys
from .actions import Action, DecisionRequest
from .enums import ActionKind, CardType, DecisionKind, EventType, Keyword
from .errors import IllegalActionError
from .events import emit
from .resources import deal_damage, effective_might
from .state import BattlefieldState, CombatContext, GameState


def start_combat(state: GameState, bf: BattlefieldState) -> None:
    """清理项 10：开始战斗（460..463）。攻方=争夺发起者（464），焦点=攻方。"""
    attacker = bf.contested_by if bf.contested_by is not None else state.turn_player
    defender = 1 - attacker
    bf.combat = CombatContext(battlefield=bf.index, attacker=attacker, defender=defender, step=1)
    bf.showdown_active = True
    state.showdown_bf = bf.index
    state.focus = attacker
    state.sd_pass = []
    emit(state, EventType.COMBAT_START, rule_ids=["R-CR-460.1", "R-CR-463.1", "R-CR-464.1"],
         public={"battlefield": bf.index, "attacker": attacker, "defender": defender})
    # 383.3：「当我进攻或防守」式触发——攻方宿主先入链、守方后入链（464 顺序近似；
    # 链结算后进焦点窗：advance 的 showdown 焦点重建接管）
    from . import triggers

    triggers.fire(state, "atk_defend", player=attacker, battlefield_index=bf.index)
    triggers.fire(state, "atk_defend", player=defender, battlefield_index=bf.index)
    if not state.chain_live():
        state.current_request = DecisionRequest(DecisionKind.SHOWDOWN_FOCUS, attacker).to_dict()
    else:
        state.current_request = None


def showdown_closed(state: GameState, bf: BattlefieldState) -> None:
    """战斗法术对决关闭→步骤 2 伤害（465）。"""
    c = bf.combat
    assert c is not None
    c.step = 2
    atk_units = _units(state, bf, c.attacker)
    def_units = _units(state, bf, c.defender)
    if not atk_units or not def_units:
        _resolve_combat(state, bf)  # 无单位侧不分配，直接进入结算
        return
    c.assign_side = c.attacker
    c.pool = _side_pool(state, atk_units, role="attacker")  # 强攻仅进攻身份生效（807.1.d.1）
    c.assigned = {}
    emit(state, EventType.COMBAT_DAMAGE_ASSIGNED, rule_ids=["R-CR-465.2"],
         public={"battlefield": bf.index, "side": c.attacker, "pool": c.pool})
    state.current_request = DecisionRequest(
        DecisionKind.ASSIGN_DAMAGE, c.attacker,
        options={"battlefield": bf.index, "side": c.attacker, "pool": c.pool},
    ).to_dict()


def _units(state: GameState, bf: BattlefieldState, seat: int) -> list[int]:
    return [
        uid for uid in bf.occupants
        if state.obj(uid).controller == seat
        and CardType.UNIT in state.card_registry[state.obj(uid).def_id].card_types
        and state.obj(uid).attached_to is None
    ]


def _has_ability(state: GameState, uid: int, kind: str) -> bool:
    d = state.card_registry[state.obj(uid).def_id]
    return any(ab.kind == kind for ab in d.abilities)


def _side_pool(state: GameState, units: list[int], *, role: str) -> int:
    """战斗伤害池（465.2.c 战力总和）：身份期关键词计入（807.1.d.1/814.1.d.1）；
    「无法造成战斗伤害」的单位不贡献（卡面文本，R-CR-465.2 分配前提）。"""
    return sum(
        effective_might(state, u, role=role)
        for u in units
        if not _has_ability(state, u, "no_combat_damage")
    )


def legal_assign_actions(state: GameState, req: DecisionRequest) -> list[Action]:
    """合法分配枚举（465.2.c）：组序 壁垒→普通→后排；逐目标不得超致少（战力-已伤）；
    先致命后摊分：目标达到致少后才允许对下一组/下一目标分配；
    总和=min(pool, 全部致少和)。"""
    bf = state.battlefields[req.options["battlefield"]]
    side = req.options["side"]
    pool = req.options["pool"]
    enemy = 1 - side
    targets = _units(state, bf, enemy)
    groups = _assign_groups(state, targets)
    from .playing import keywords_of

    # 致少口径含身份期关键词：被分配方的当前战力（465.2.c.4；432.1.a 坚守示例）
    c = bf.combat
    role = "attacker" if c is not None and enemy == c.attacker else \
        "defender" if c is not None and enemy == c.defender else None
    caps = {u: max(0, effective_might(state, u, role=role) - state.obj(u).damage) for u in targets}
    total_cap = sum(caps.values())
    total = min(pool, total_cap)
    if total == 0:
        return [Action(ActionKind.ASSIGN_DAMAGE, side, params={"assign": {u: 0 for u in targets}})]
    out: list[Action] = []
    for plan in _enumerate_plans(groups, caps, total):
        out.append(Action(ActionKind.ASSIGN_DAMAGE, side, params={"assign": plan}))
    return out


def _assign_groups(state: GameState, targets: list[int]) -> list[list[int]]:
    """分配优先级组（壁垒 815.1.b → 普通 → 后排 826.3/「最后承担伤害」465.2.c.2/c.6）。
    壁垒与「最后」排斥时任选其一（465.2.c.8）——现有卡池无同体实例，P2 记录。"""
    from .playing import keywords_of

    tank, mid, back = [], [], []
    for u in targets:
        kws = keywords_of(state, u)
        if Keyword.TANK in kws:
            tank.append(u)
        elif Keyword.BACKLINE in kws or _has_ability(state, u, "last_damage"):
            back.append(u)
        else:
            mid.append(u)
    return [g for g in (tank, mid, back) if g]


def _enumerate_plans(groups: list[list[int]], caps: dict[int, int], total: int):
    """枚举合法分配：按组序，前面组全部达致少后才允许后续组>0；组内目标可自由分配。"""
    results: list[dict[int, int]] = []

    def rec(gi: int, remaining: int, acc: dict[int, int]) -> None:
        if gi == len(groups):
            if remaining == 0:
                results.append(dict(acc))
            return
        group = groups[gi]
        later_cap = sum(caps[u] for g in groups[gi + 1 :] for u in g)
        # 本组必须吸收的最低值：若想用后续组，本组须全满
        if later_cap > 0 and remaining > later_cap:
            min_here = remaining - later_cap
        else:
            min_here = 0 if gi == len(groups) - 1 or later_cap == 0 else (remaining - later_cap if remaining > later_cap else 0)
        group_cap = sum(caps[u] for u in group)
        # 本组分配值域
        lo = max(min_here, remaining - later_cap)
        hi = min(group_cap, remaining)
        for gsum in range(lo, hi + 1):
            if later_cap > 0 and gsum < group_cap and remaining - gsum > 0 and gi < len(groups) - 1:
                # 允许后进组仅当本组全满（组序：先致命后摊分）
                continue
            for alloc in _split(group, caps, gsum):
                acc.update(alloc)
                rec(gi + 1, remaining - gsum, acc)
                for u in group:
                    acc.pop(u, None)

    rec(0, total, {})
    return results


def _split(group: list[int], caps: dict[int, int], s: int):
    """组内将 s 点合法拆分给各目标（每目标≤cap）。"""
    if s == 0:
        yield {u: 0 for u in group}
        return
    if len(group) == 1:
        u = group[0]
        if 0 <= s <= caps[u]:
            yield {u: s}
        return
    first, rest = group[0], group[1:]
    for x in range(0, min(caps[first], s) + 1):
        rec_rest = s - x
        max_rest = sum(caps[u] for u in rest)
        if rec_rest > max_rest:
            continue
        for tail in _split(rest, caps, rec_rest):
            yield {first: x, **tail}


def handle_assign(state: GameState, req: DecisionRequest, action: Action) -> None:
    bf = state.battlefields[req.options["battlefield"]]
    c = bf.combat
    assert c is not None
    side = req.options["side"]
    assign = {int(k): int(v) for k, v in action.params["assign"].items()}
    legal = legal_assign_actions(state, req)
    plan_tuple = tuple(sorted(assign.items()))
    if not any(tuple(sorted({int(k): int(v) for k, v in a.params["assign"].items()}.items())) == plan_tuple for a in legal):
        raise IllegalActionError(state.step_id, side, action.digest(), "illegal damage assignment (R-CR-465.2.c)")
    state.current_request = None
    emit(state, EventType.COMBAT_DAMAGE_ASSIGNED, rule_ids=["R-CR-465.2.c.4.a"],
         public={"battlefield": bf.index, "side": side, "assign": {str(k): v for k, v in assign.items()}})
    # 造成伤害（分配后同时造成 465.2.d）——记录到 ctx
    for uid, amount in assign.items():
        if amount > 0:
            deal_damage(state, uid, amount, source="combat", rule="R-CR-465.2.d")
    if side == c.attacker:
        defender = c.defender
        atk_units = _units(state, bf, defender)
        if not atk_units:
            _resolve_combat(state, bf)
            return
        c.assign_side = defender
        c.pool = _side_pool(state, _units(state, bf, defender), role="defender")  # 814.1.d.1
        c.assigned = {}
        state.current_request = DecisionRequest(
            DecisionKind.ASSIGN_DAMAGE, defender,
            options={"battlefield": bf.index, "side": defender, "pool": c.pool},
        ).to_dict()
    else:
        _resolve_combat(state, bf)


def _resolve_combat(state: GameState, bf: BattlefieldState) -> None:
    """步骤 3 结算（466）：战斗特殊清理（3a/3b→3c→3d）→判定→确立控制→结束。"""
    c = bf.combat
    assert c is not None
    attacker, defender = c.attacker, c.defender
    # 466.1 战斗特殊清理：3a/3b（致命摧毁，含全场）、3c（全部单位移除伤害）
    cleanup_sys.cleanup(state)
    if state.ended:
        bf.combat = None
        bf.showdown_active = False
        state.showdown_bf = None
        return
    for uid in list(state.objects.keys()):
        o = state.objects.get(uid)
        if o and o.damage > 0:
            from .resources import heal

            heal(state, uid, o.damage, rule="R-CR-466.1.a.1")
    # 3d（466.1.a.2）：防守方仍在场→召回进攻方单位
    recalled = False
    if _units(state, bf, defender):
        for uid in list(_units(state, bf, attacker)):
            from .movement import recall

            recall(state, uid, rule="R-CR-466.1.a.2")
            recalled = True
    # 466.3 判定
    att_alive = bool(_units(state, bf, attacker))
    def_alive = bool(_units(state, bf, defender))
    no_result = recalled or (att_alive and def_alive) or (not att_alive and not def_alive)
    winner_side = None
    if not no_result:
        winner_side = attacker if att_alive else defender
    # 466.3.d.1 无结果且双方仍存活→标记新对决+战斗待发生
    if no_result and att_alive and def_alive:
        bf.showdown_pending = True
        bf.combat_pending = True
        emit(state, EventType.COMBAT_END, rule_ids=["R-CR-466.3.d.1"],
             public={"battlefield": bf.index, "result": "no_result_reflag"})
    # 466.5 确立控制（若无待定）
    if not (bf.showdown_pending or bf.combat_pending) and not state.ended:
        if att_alive and not def_alive:
            from .showdown import _establish_control

            _establish_control(state, bf, attacker, rule="R-CR-466.5")
        elif def_alive and not att_alive:
            from .showdown import _establish_control

            _establish_control(state, bf, defender, rule="R-CR-466.5")
        elif not att_alive and not def_alive:
            bf.controller = None
            bf.contested = False
            bf.contested_by = None
            emit(state, EventType.CLEANUP_ITEM, rule_ids=["R-CR-466.5.b"],
                 public={"battlefield": bf.index, "controller": None})
    # 466.7 战斗结束：移除身份；本次战斗效果失效（骨架无）
    bf.combat = None
    bf.showdown_active = False
    state.showdown_bf = None
    state.focus = None
    state.sd_pass = []
    emit(state, EventType.COMBAT_END, rule_ids=["R-CR-466.7"],
         public={"battlefield": bf.index, "winner_side": winner_side})
