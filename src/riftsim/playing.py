# 打出六步（349..359）与技能打出五步（401..406；MECH-PLAY-*）
from __future__ import annotations

from .actions import Action
from .enums import ActionKind, CardType, Domain, EventType, Keyword, Zone
from .errors import IllegalActionError
from .events import emit
from .resources import add_energy, add_power, can_pay, pay_cost
from .state import ChainItem, GameState


# ---------------------------------------------------------------- 时机权限门
def can_use_timing(state: GameState, player: int, timing: str, *, in_reaction: bool) -> bool:
    """时机权限（806/813/381；R-CR-155/377）：
    - 默认/迅捷类「action」：己方回合 + 开环（非对决亦可；单位/装备主阶段限制另见调用点）
    - 「reaction」：闭环可（任意回合，813.1.c）；己方回合开环亦可
    - 支付窗获得资源技能：恒可（357.1.a；in_payment 由调用点放宽）
    """
    link_closed = state.chain_live()
    own_turn = state.turn_player == player
    if timing == "reaction":
        if link_closed:
            return True
        return own_turn and not state.showdown_live()
    # action 默认
    return own_turn and not link_closed and not state.showdown_live()


def keywords_of(state: GameState, uid: int) -> set[Keyword]:
    o = state.obj(uid)
    d = state.card_registry[o.def_id]
    return set(d.keywords) | set(o.keywords_extra.keys())


# ---------------------------------------------------------------- 合法动作枚举
def legal_play_actions(state: GameState, player: int) -> list[Action]:
    """MAIN_ACTION 窗口的打出（己方回合主阶段开环，155.1/419.1.a）。"""
    if state.turn_player != player or state.chain_live() or state.showdown_live():
        return []
    out: list[Action] = []
    for uid in list(state.players[player].hand) + list(state.players[player].hero_zone):
        out.extend(_play_options(state, player, uid, in_reaction=False))
    return out


def legal_reactions(state: GameState, player: int) -> list[Action]:
    """闭环/对决中的反应类动作：
    法术/技能带[反应]→闭环可；带[迅捷]→法术对决期间可（806.1.c）；支付窗资源技能另恒可。
    """
    out: list[Action] = []
    link_closed = state.chain_live()
    showdown = state.showdown_live()
    for uid in list(state.players[player].hand) + list(state.players[player].hero_zone):
        d = state.card_registry[state.obj(uid).def_id]
        kws = keywords_of(state, uid)
        allowed = False
        if CardType.SPELL in d.card_types:
            if Keyword.REACTION in kws and link_closed:
                allowed = True
            if Keyword.ACTION in kws and showdown:
                allowed = True
        else:
            # 常驻牌在闭环/对决中打出需要相应时机关键词（806/813 语义通用化）
            if Keyword.REACTION in kws and link_closed:
                allowed = True
            if Keyword.ACTION in kws and showdown:
                allowed = True
        if allowed:
            out.extend(_play_options(state, player, uid, in_reaction=True))
    for uid in state.player_objects(player, board_only=True):
        out.extend(_activate_options(state, player, uid, in_reaction=True))
    return out


def legal_activate_actions(state: GameState, player: int) -> list[Action]:
    """主阶段开环的主动技能（381/145.2/151.2）。"""
    if state.turn_player != player or state.chain_live() or state.showdown_live():
        return []
    out: list[Action] = []
    for uid in state.player_objects(player, board_only=True):
        out.extend(_activate_options(state, player, uid, in_reaction=False))
    return out


def _play_options(state: GameState, player: int, uid: int, *, in_reaction: bool) -> list[Action]:
    d = state.card_registry[state.obj(uid).def_id]
    if not _affordable_with_runes(state, player, d.cost_energy, _power_dict(d.cost_power)):
        return []
    if CardType.UNIT in d.card_types:
        locs = [("base", player)]
        for bf in state.battlefields:
            if bf.controller == player:
                locs.append(("battlefield", bf.index))
        return [
            Action(ActionKind.PLAY_CARD, player, uid, {"location": loc, "in_reaction": in_reaction})
            for loc in locs
        ]
    if CardType.GEAR in d.card_types:
        return [Action(ActionKind.PLAY_CARD, player, uid, {"location": ("base", player), "in_reaction": in_reaction})]
    return [Action(ActionKind.PLAY_CARD, player, uid, {"in_reaction": in_reaction})]


def _activate_options(state: GameState, player: int, uid: int, *, in_reaction: bool) -> list[Action]:
    o = state.obj(uid)
    d = state.card_registry[o.def_id]
    out: list[Action] = []
    for ab in d.abilities:
        if ab.cost_exhaust_self and o.exhausted:
            continue
        # 激活费用支付能力：资源技能自身费用为 [E] 或回收，无需池资源
        if in_reaction:
            if ab.timing == "reaction" or ab.kind == "gain_resource":
                ok = state.chain_live() or state.showdown_live() or ab.kind == "gain_resource"
            else:
                ok = False
        else:
            ok = can_use_timing(state, player, ab.timing, in_reaction=False)
            # 单位/装备主动技能另限主阶段（145.2/151.2），本函数仅在主阶段调用
        if ok:
            out.append(Action(ActionKind.ACTIVATE_ABILITY, player, uid,
                              {"ability_id": ab.ability_id, "in_reaction": in_reaction}))
    return out


def _power_dict(cost_power: tuple) -> dict[str, int]:
    out: dict[str, int] = {}
    for d in cost_power:
        out[d.value] = out.get(d.value, 0) + 1
    return out


def _rune_breakdown(state: GameState, player: int) -> tuple[dict[str, int], int, int]:
    """符文产能明细：各特性可回收数（含休眠）、活跃可 [E] 数、休眠数。"""
    per_domain: dict[str, int] = {}
    active = 0
    sleeping = 0
    for uid in state.player_objects(player, board_only=True):
        o = state.obj(uid)
        d = state.card_registry[o.def_id]
        if CardType.RUNE not in d.card_types or o.attached_to is not None:
            continue
        dom = next(iter(d.domains)).value if d.domains else None
        if dom:
            per_domain[dom] = per_domain.get(dom, 0) + 1
        if o.exhausted:
            sleeping += 1
        else:
            active += 1
    return per_domain, active, sleeping


def _affordable_with_runes(state: GameState, player: int, energy: int, power: dict[str, int]) -> bool:
    """可支付性（357 + 357.1.a 支付窗资源技能），保守精确：
    各特性符能缺口须由该特性符文回收补足（[C]=自身特性，164.2）；
    回收优先消耗休眠符文以保留活跃 [E] 产能，法力缺口须 ≤ 剩余活跃数。"""
    p = state.players[player]
    per_domain, active, sleeping = _rune_breakdown(state, player)
    recycles_needed = 0
    for d, n in power.items():
        lack = n - p.rune_power.get(d, 0)
        if lack <= 0:
            continue
        if per_domain.get(d, 0) < lack:
            return False
        recycles_needed += lack
    energy_lack = max(0, energy - p.rune_energy)
    active_left = active - max(0, recycles_needed - sleeping)
    return energy_lack <= active_left


# ---------------------------------------------------------------- 打出处理（六步 354..359）
def handle_play_card(state: GameState, action: Action, *, in_reaction: bool = False) -> None:
    player, uid = action.actor, action.source_uid
    o = state.obj(uid)
    d = state.card_registry[o.def_id]
    if not (
        uid in state.players[player].hand
        or uid in state.players[player].hero_zone
        or (o.zone == Zone.HIDDEN_SLOT and o.controller == player)
    ):
        raise IllegalActionError(state.step_id, player, action.digest(), "source not in hand/hero/hidden (R-CR-419.1.a)")
    # 时机权限复核（358 步骤 5 的门在合法集已断言；此处防御）
    if not in_reaction:
        if state.turn_player != player or state.chain_live() or state.showdown_live():
            raise IllegalActionError(state.step_id, player, action.digest(), "timing: need own open main (R-CR-155.1)")
    else:
        kws = keywords_of(state, uid)
        ok = (Keyword.REACTION in kws and state.chain_live()) or (Keyword.ACTION in kws and state.showdown_live())
        if o.zone == Zone.HIDDEN_SLOT and Keyword.HIDDEN in d.keywords | set(o.keywords_extra):
            ok = state.chain_live() or state.showdown_live()  # 待命打出获[反应]（811.6）
        if not ok:
            raise IllegalActionError(state.step_id, player, action.digest(), "reaction timing needs [反应]/[迅捷] (R-CR-806/813)")

    origin_zone = o.zone
    # 步骤 1（354）：入链，回合转闭环
    _untrack_source(state, uid)
    o.zone, o.zone_owner, o.battlefield = Zone.CHAIN, None, None
    emit(state, EventType.PLAY_STEP, rule_ids=["R-CR-354.1"], card_ids=[f"uid:{uid}"],
         public={"step": 1, "uid": uid, "player": player, "origin": origin_zone.value})
    # 步骤 2（355）：选择（骨架：仅位置；目标/模式 P1+）
    choices = dict(action.params)
    emit(state, EventType.PLAY_STEP, rule_ids=["R-CR-355.1"], card_ids=[f"uid:{uid}"],
         public={"step": 2, "uid": uid, "choices_public": _public_choices(choices)})
    # 步骤 3（356）：定总费（骨架=印刷费；额外/增减费 P1）
    if origin_zone == Zone.HIDDEN_SLOT:
        energy, power = 0, {}  # 待命打出无视基础费用（811.6）
    else:
        energy, power = d.cost_energy, _power_dict(d.cost_power)
    emit(state, EventType.PLAY_STEP, rule_ids=["R-CR-356.1"], card_ids=[f"uid:{uid}"],
         public={"step": 3, "uid": uid, "total": {"energy": energy, "power": dict(power)}})
    # 步骤 4（357）：支付（支付窗可激活获得资源技能）
    pay_auto(state, player, energy, power)
    # 步骤 5（358）：复核（骨架：位置最终合法）
    _check_location_legal(state, player, uid, choices)
    emit(state, EventType.PLAY_STEP, rule_ids=["R-CR-358.2"], card_ids=[f"uid:{uid}"], public={"step": 5, "uid": uid})
    # 步骤 6（359）：成为待处理项，等 FEPR-确认
    item = ChainItem(
        item_id=state.new_uid(), kind="card", source_uid=uid, controller=player,
        choices=choices, total_cost={"energy": energy, "power": power}, paid=True,
        origin=origin_zone,
    )
    from . import chain_sys

    chain_sys.push(state, item)
    state.current_request = None


def _public_choices(choices: dict) -> dict:
    out = dict(choices)
    out.pop("in_reaction", None)
    return out


def _untrack_source(state: GameState, uid: int) -> None:
    o = state.obj(uid)
    if o.zone in (Zone.HAND, Zone.HERO_ZONE) and o.zone_owner is not None:
        p = state.players[o.zone_owner]
        for lst in (p.hand, p.hero_zone):
            if uid in lst:
                lst.remove(uid)
                break
    elif o.zone == Zone.HIDDEN_SLOT and o.battlefield is not None:
        bf = state.battlefields[o.battlefield]
        if uid in bf.hidden_slot:
            bf.hidden_slot.remove(uid)


def _check_location_legal(state: GameState, player: int, uid: int, choices: dict) -> None:
    d = state.card_registry[state.obj(uid).def_id]
    loc = choices.get("location")
    if CardType.UNIT in d.card_types:
        if not loc:
            raise IllegalActionError(state.step_id, player, "", "unit play needs location (R-CR-355.6)")
        kind, idx = loc
        if kind == "base" and idx != player:
            raise IllegalActionError(state.step_id, player, "", "base must be own (R-CR-149)")
        if kind == "battlefield" and state.battlefields[idx].controller != player:
            raise IllegalActionError(state.step_id, player, "", "battlefield not controlled (R-CR-359.2/822 伏击之外)")


def pay_auto(state: GameState, player: int, energy: int, power: dict[str, int]) -> None:
    """步骤 4 支付辅助：自动激活基本符文技能补缺口（357.1.a）。
    顺序：休眠优先回收补符能（[C] 特性匹配），再 [E] 活跃符文补法力。
    M1 自动化决策占位——P1 若需玩家显式选择激活序，改为 PAYMENT_CHOICE 请求点。"""
    p = state.players[player]
    for d, n in power.items():
        while p.rune_power.get(d.value if isinstance(d, Domain) else d, 0) < n:
            key = d.value if isinstance(d, Domain) else d
            rune = _find_rune(state, player, want_domain=Domain(key), sleeping_first=True)
            if rune is None:
                raise IllegalActionError(state.step_id, player, "", f"no recyclable rune for [{key}] (R-CR-357.1)")
            _recycle_rune_for_gain(state, rune)
    while p.rune_energy < energy:
        rune = _find_rune(state, player, want_domain=None, require_active=True)
        if rune is None:
            raise IllegalActionError(state.step_id, player, "", "insufficient runes for energy (R-CR-357.1)")
        _exhaust_rune_for_gain(state, rune)
    if not can_pay(state, player, energy, power):
        raise IllegalActionError(state.step_id, player, "", "cannot pay total cost (R-CR-357.1)")
    pay_cost(state, player, energy, power)


def _find_rune(state: GameState, player: int, want_domain: Domain | None,
               require_active: bool = False, sleeping_first: bool = False) -> int | None:
    cands: list[int] = []
    for uid in state.player_objects(player, board_only=True):
        o = state.obj(uid)
        d = state.card_registry[o.def_id]
        if CardType.RUNE not in d.card_types or o.attached_to is not None:
            continue
        if want_domain is not None and want_domain not in d.domains:
            continue
        if require_active and o.exhausted:
            continue
        cands.append(uid)
    if sleeping_first:
        cands.sort(key=lambda u: (not state.obj(u).exhausted, u))
    return cands[0] if cands else None


def _recycle_rune_for_gain(state: GameState, uid: int) -> Domain:
    """回收符文技能：得 [C]（164.2）。返回获得特性。"""
    from .resources import recycle

    o = state.obj(uid)
    d = state.card_registry[o.def_id]
    dom = next(iter(d.domains)) if d.domains else Domain.R  # 无色符文 [C]→? 骨架无此卡；805.1.a.2 [A] 语境不适用
    recycle(state, uid, rule="R-CR-164.2")
    add_power(state, o.controller, dom, 1)
    return dom


def _exhaust_rune_for_gain(state: GameState, uid: int) -> None:
    """[E] 符文技能：得 1 法力（164.2）。"""
    o = state.obj(uid)
    if o.exhausted:
        raise IllegalActionError(state.step_id, o.controller, "", "rune already exhausted")
    o.exhausted = True
    add_energy(state, o.controller, 1)


# ---------------------------------------------------------------- 确认/结算
def enter_permanent(state: GameState, item: ChainItem) -> None:
    """常驻牌确认入场（359.2/337.2）：单位休眠进指定位置；装备活跃进基地。"""
    uid = item.source_uid
    o = state.obj(uid)
    d = state.card_registry[o.def_id]
    player = item.controller
    o.face_down = False
    o.entered_turn = state.turn_number
    if CardType.UNIT in d.card_types:
        o.exhausted = True  # 359.2 单位休眠进场（805 急速挂点）
        kind, idx = item.choices["location"]
        if kind == "base":
            o.zone, o.zone_owner, o.battlefield = Zone.BASE, player, None
            state.base_occupants[player].append(uid)
        else:
            bf = state.battlefields[idx]
            o.zone, o.zone_owner, o.battlefield = Zone.BATTLEFIELD, None, idx
            bf.occupants.append(uid)
        emit(state, EventType.RESOLVE, rule_ids=["R-CR-359.2"], card_ids=[f"uid:{uid}"],
             public={"uid": uid, "entered": f"{kind}:{idx}", "exhausted": True})
    else:  # GEAR（及其他非单位常驻）→基地活跃（359）
        o.exhausted = False
        o.zone, o.zone_owner, o.battlefield = Zone.BASE, player, None
        state.base_occupants[player].append(uid)
        emit(state, EventType.RESOLVE, rule_ids=["R-CR-359.3"], card_ids=[f"uid:{uid}"],
             public={"uid": uid, "entered": "base", "exhausted": False})


def resolve_spell(state: GameState, item: ChainItem) -> None:
    """法术结算（157/158）：执行文本（骨架空）→所属者废牌堆。"""
    uid = item.source_uid
    o = state.obj(uid)
    apply_card_text(state, item)
    o.zone, o.zone_owner, o.battlefield = Zone.TRASH, o.owner, None
    state.players[o.owner].trash.append(uid)
    emit(state, EventType.RESOLVE, rule_ids=["R-CR-157.1", "R-CR-158.1"], card_ids=[f"uid:{uid}"],
         public={"uid": uid, "to": "trash"})


def apply_card_text(state: GameState, item: ChainItem) -> None:
    """卡牌效果文本执行点（骨架池全为空效果；阶段 4 效果原语接入点）。"""
    return


def apply_ability_resolution(state: GameState, item: ChainItem) -> None:
    """技能结算（获得资源 164.2；阶段 4 扩展其他 kind）。"""
    ab = item.ability or {}
    kind = ab.get("kind")
    player = item.controller
    if kind == "gain_resource":
        if ab.get("grant_energy"):
            add_energy(state, player, ab["grant_energy"])
        if ab.get("grant_power_self_domain"):
            d = state.card_registry[state.obj(item.source_uid).def_id]
            dom = ab.get("domain") or (next(iter(d.domains)) if d.domains else None)
            if isinstance(dom, str):
                dom = Domain(dom)
            if dom:
                add_power(state, player, dom, 1)
    emit(state, EventType.RESOLVE, rule_ids=["R-CR-406"], public={"item_id": item.item_id, "ability": kind})


def handle_activate(state: GameState, action: Action, *, in_reaction: bool = False) -> None:
    """激活主动技能（377/401）：入链为 pending 技能项；获得资源类确认立即结算（429.2）。"""
    player, uid = action.actor, action.source_uid
    o = state.obj(uid)
    d = state.card_registry[o.def_id]
    ability_id = action.params.get("ability_id")
    ab = next((a for a in d.abilities if a.ability_id == ability_id), None)
    if ab is None:
        raise IllegalActionError(state.step_id, player, action.digest(), f"no such ability {ability_id}")
    if ab.cost_exhaust_self and o.exhausted:
        raise IllegalActionError(state.step_id, player, action.digest(), "source exhausted for [E] (R-CR-377/414)")
    # 时机权限（防御复核；legal 已过滤）
    if not in_reaction and not can_use_timing(state, player, ab.timing, in_reaction=False):
        raise IllegalActionError(state.step_id, player, action.digest(), "timing (R-CR-381)")
    # 支付技能费用（[E]/回收自身）
    if ab.cost_exhaust_self:
        o.exhausted = True
        emit(state, EventType.EXHAUST, rule_ids=["R-CR-414.1"], card_ids=[f"uid:{uid}"],
             public={"uid": uid, "by": "ability_cost"})
    if ab.cost_recycle_self:
        from .resources import recycle

        # 回收自身：先离链入底，但需先建立链项记录来源
    item = ChainItem(
        item_id=state.new_uid(), kind="ability", source_uid=uid, controller=player,
        ability={
            "ability_id": ab.ability_id, "kind": ab.kind, "immediate": ab.immediate,
            "grant_energy": ab.grant_energy,
            "grant_power_self_domain": ab.grant_power_self_domain,
            "domain": next(iter(d.domains)).value if (ab.grant_power_self_domain and d.domains) else None,
            "origin": "gain_ability" if ab.kind == "gain_resource" else "player_action",
            "rules_ref": list(ab.rules_ref),
        },
        origin=o.zone,
    )
    from . import chain_sys

    if ab.cost_recycle_self:
        # 回收自身作为费用（164.2）：链项保留，来源对象已回符文堆底
        from .resources import recycle as _rec

        _rec(state, uid, rule="R-CR-164.2")
    chain_sys.push(state, item)
    state.current_request = None
