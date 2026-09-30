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
    [伏击]：有己方单位的战场存在即有打出可能性（813.4.a），打出到该类位置获[反应]（822.1.b）。
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
            if Keyword.QUICKDRAW in kws and link_closed:
                allowed = True  # 819.1.b：灵便装备自带[反应]
            if Keyword.ACTION in kws and showdown:
                allowed = True
            if Keyword.AMBUSH in kws and (link_closed or showdown) and _ambush_battlefields(state, player):
                allowed = True  # 813.4.a 条件可能性即可在合适时机打出
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
    # 步骤 2 可选费用变体（355 选择）：805 急速 / 批次 2-e 可选附加费
    variants: list[dict] = [{}]
    kws = keywords_of(state, uid)
    if CardType.UNIT in d.card_types and Keyword.ACCELERATE in kws and len(d.domains) <= 1:
        accel_power = dict(_power_dict(d.cost_power))
        accel_key = next(iter(d.domains)).value if d.domains else "A"  # 805.1.a.1 / 805.1.a.2
        accel_power[accel_key] = accel_power.get(accel_key, 0) + 1
        if _affordable_with_runes(state, player, d.cost_energy + 1, accel_power):
            variants.append({"accelerate": True})
        # 多特性单位急速变体 MVP 暂缓（805.1.a.1 特性需选项——worklog 已知间隙）
    x_ab = next((ab for ab in d.abilities if ab.kind == "extra_cost" and ab.timing == "passive"), None)
    if CardType.UNIT in d.card_types and x_ab is not None:
        x_energy, x_power = _apply_symbols(d.cost_energy, _power_dict(d.cost_power), x_ab.cost_symbols)
        if _affordable_with_runes(state, player, x_energy, x_power):
            variants.append({"pay_extra": True})
    if CardType.UNIT in d.card_types:
        locs = [("base", player)]
        for bf in state.battlefields:
            if bf.controller == player:
                locs.append(("battlefield", bf.index))
        ambush_locs = [("battlefield", i) for i in _ambush_battlefields(state, player)] \
            if Keyword.AMBUSH in kws else []
        open_locs = [("battlefield", bf.index) for bf in state.battlefields
                     if bf.controller is None and not bf.occupants] \
            if any(ab.kind == "location_open_battlefield" for ab in d.abilities) else []
        if in_reaction and Keyword.REACTION not in kws and Keyword.ACTION not in kws:
            locs = ambush_locs  # 813.4：仅伏击授权位置令此牌获[反应]
        else:
            locs += ambush_locs + open_locs
        locs = list(dict.fromkeys(locs))
        return [
            Action(ActionKind.PLAY_CARD, player, uid,
                   {"location": loc, "in_reaction": in_reaction, **v})
            for loc in locs for v in variants
        ]
    if CardType.GEAR in d.card_types:
        out_g: list[Action] = []
        for v in variants:
            base_params = {"location": ("base", player), "in_reaction": in_reaction}
            out_g.append(Action(ActionKind.PLAY_CARD, player, uid, dict(base_params, **v)))
            if Keyword.QUICKDRAW in kws:
                # 819.1.d：打出时触发「将其贴附于你控制的一名单位上」——目标随打出宣言选定
                for tgt in _friendly_units(state, player):
                    out_g.append(Action(ActionKind.PLAY_CARD, player, uid,
                                        dict(base_params, **v, target=tgt)))
        return out_g
    # 法术：带目标的单体原语随动作一并选定（355.6；spell_damage / spell_pump 同一路径）
    tgt_ab = next((ab for ab in d.abilities if ab.kind in ("spell_damage", "spell_pump")), None)
    if tgt_ab is not None:
        return [
            Action(ActionKind.PLAY_CARD, player, uid,
                   {"in_reaction": in_reaction, "target": tgt})
            for tgt in deal_targets_of(state, tgt_ab.target_scope)
        ]
    return [Action(ActionKind.PLAY_CARD, player, uid, {"in_reaction": in_reaction})]


def _ambush_battlefields(state: GameState, player: int) -> list[int]:
    """有己方单位的战场索引（822.1.b 位置授权；无视控制归属）。"""
    return [
        bf.index for bf in state.battlefields
        if any(state.obj(u).controller == player for u in bf.occupants)
    ]


def _apply_symbols(energy: int, power: dict[str, int], symbols: tuple[str, ...]) -> tuple[int, dict[str, int]]:
    """费用符号叠加（356 定总费）：数字→法力，特性字母/"A"→符能。"""
    power = dict(power)
    for sym in symbols:
        if sym.isdigit():
            energy += int(sym)
        else:
            power[sym] = power.get(sym, 0) + 1
    return energy, power


def _activate_options(state: GameState, player: int, uid: int, *, in_reaction: bool) -> list[Action]:
    o = state.obj(uid)
    d = state.card_registry[o.def_id]
    out: list[Action] = []
    for ab in d.abilities:
        if ab.kind not in _ACTIVATABLE_KINDS:
            continue  # 静态文本（如 enters_exhausted）不可宣告激活（377.1）
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
        if not ok:
            continue
        if ab.kind == "deal_damage":
            # 目标在激活时随动作一并选定（355 步骤 2 选择；377.3.b.1 遵循 398 流程）
            for tgt in deal_targets_of(state, ab.target_scope):
                out.append(Action(ActionKind.ACTIVATE_ABILITY, player, uid,
                                  {"ability_id": ab.ability_id, "in_reaction": in_reaction,
                                   "target": tgt}))
            continue
        if ab.kind == "equip":
            # 818.1：装配是场上（基地）装备的主动技能；目标=你控制的一名单位（818.1.c.2）
            if o.zone != Zone.BASE or o.zone_owner != player or o.attached_to is not None:
                continue
            energy, power = _apply_symbols(0, {}, ab.cost_symbols)
            if not _affordable_with_runes(state, player, energy, power):
                continue  # 818.1.b 支付费用为前提
            for tgt in _friendly_units(state, player):
                out.append(Action(ActionKind.ACTIVATE_ABILITY, player, uid,
                                  {"ability_id": ab.ability_id, "in_reaction": in_reaction,
                                   "equip": True, "target": tgt}))
            continue
        out.append(Action(ActionKind.ACTIVATE_ABILITY, player, uid,
                          {"ability_id": ab.ability_id, "in_reaction": in_reaction}))
    return out


# 可宣告激活的技能种类（377）；静态文本类（enters_exhausted）不在其中
_ACTIVATABLE_KINDS = frozenset({"gain_resource", "deal_damage", "equip"})


def _friendly_units(state: GameState, player: int) -> list[int]:
    """你控制的在场单位（818.1.c.2 装配目标范围；基地+战场，排除贴附物）。"""
    out = [uid for uid, o in state.objects.items()
           if o.controller == player and o.attached_to is None
           and o.zone in (Zone.BASE, Zone.BATTLEFIELD)
           and CardType.UNIT in state.card_registry[o.def_id].card_types]
    out.sort()
    return out


def deal_targets_of(state: GameState, scope: str) -> list[int]:
    """伤害技能目标枚举（355.6 目标选取；范围白名单见 effects.py 目标短语表）。"""
    out: list[int] = []
    if scope == "unit_at_battlefield":
        cands = [u for bf in state.battlefields for u in bf.occupants]
    elif scope == "unit":
        cands = list(state.player_objects(0, board_only=True)) + list(state.player_objects(1, board_only=True))
    else:
        return []
    seen: set[int] = set()
    for u in cands:
        o = state.obj(u)
        dd = state.card_registry[o.def_id]
        if CardType.UNIT in dd.card_types and o.attached_to is None and u not in seen:
            seen.add(u)
            out.append(u)
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
    回收优先消耗休眠符文以保留活跃 [E] 产能，法力缺口须 ≤ 剩余活跃数。
    伪域 "A"（805.1.a.2/809.1.c.1）：缺口可由任意特性符文回收补足。"""
    p = state.players[player]
    per_domain, active, sleeping = _rune_breakdown(state, player)
    recycles_needed = 0
    specific_total = 0
    for d, n in power.items():
        if d == "A":
            continue
        specific_total += n
        lack = n - p.rune_power.get(d, 0)
        if lack <= 0:
            continue
        if per_domain.get(d, 0) < lack:
            return False
        recycles_needed += lack
    # [A] 伪域缺口：余额中对特性需求扣减后的剩余（下限 0）能覆盖多少 [A]；
    # 修复：余额不足扣减 specific_total 时差额为负，不得反向增大缺口（旧式在资源紧时
    # 虚增 recycles_needed 致合法动作丢失——SFD-087 E2[B]×3 暴露）。
    any_lack = max(0, power.get("A", 0) - max(0, sum(p.rune_power.values()) - specific_total))
    if any_lack > 0:
        if sum(per_domain.values()) - recycles_needed < any_lack:
            return False
        recycles_needed += any_lack
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
    # 目标合法性预检（355.6）：带目标法术须选范围内目标——在任何状态变更前拒绝
    tgt_ab = next((ab for ab in d.abilities if ab.kind in ("spell_damage", "spell_pump")), None)
    if tgt_ab is not None:
        tgt = action.params.get("target")
        if tgt is None or tgt not in deal_targets_of(state, tgt_ab.target_scope):
            raise IllegalActionError(state.step_id, player, action.digest(),
                                     f"invalid target for {tgt_ab.target_scope} (R-CR-355.6)")

    origin_zone = o.zone
    # 步骤 1（354）：入链，回合转闭环
    _untrack_source(state, uid)
    o.zone, o.zone_owner, o.battlefield = Zone.CHAIN, None, None
    emit(state, EventType.PLAY_STEP, rule_ids=["R-CR-354.1"], card_ids=[f"uid:{uid}"],
         public={"step": 1, "uid": uid, "player": player, "origin": origin_zone.value})
    # 步骤 2（355）：选择（位置/目标/可选费用变体；目标成员资格已在六步前预检）
    choices = dict(action.params)
    emit(state, EventType.PLAY_STEP, rule_ids=["R-CR-355.1"], card_ids=[f"uid:{uid}"],
         public={"step": 2, "uid": uid, "choices_public": _public_choices(choices)})
    # 步骤 3（356）：定总费（印刷费 + 可选附加费 805/批次 2-e + 法盾强制附加 809）
    if origin_zone == Zone.HIDDEN_SLOT:
        energy, power = 0, {}  # 待命打出无视基础费用（811.6）
    else:
        energy, power = d.cost_energy, _power_dict(d.cost_power)
    kws = set(d.keywords) | set(o.keywords_extra)
    if choices.get("accelerate"):
        if Keyword.ACCELERATE not in kws:
            raise IllegalActionError(state.step_id, player, action.digest(),
                                     "accelerate without [急速] (R-CR-805.1)")
        if len(d.domains) > 1:
            raise IllegalActionError(state.step_id, player, action.digest(),
                                     "accelerate multi-domain variant unsupported (R-CR-805.1.a.1; P1)")
        accel_key = next(iter(d.domains)).value if d.domains else "A"  # 805.1.a.1 / 805.1.a.2
        energy, power = _apply_symbols(energy, power, ("1", accel_key))
    if choices.get("pay_extra"):
        x_ab = next((ab for ab in d.abilities if ab.kind == "extra_cost"), None)
        if x_ab is None:
            raise IllegalActionError(state.step_id, player, action.digest(),
                                     "pay_extra without extra-cost text (R-CR-356.2)")
        energy, power = _apply_symbols(energy, power, x_ab.cost_symbols)
    deflect_n = _deflect_charges(state, player, choices.get("target"))
    if deflect_n:
        power["A"] = power.get("A", 0) + deflect_n  # 356.2.a.2 强制附加
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
        if kind == "battlefield":
            bf = state.battlefields[idx]
            if bf.controller == player:
                return
            o = state.obj(uid)
            kws = set(d.keywords) | set(o.keywords_extra)
            # 822.3 步骤 5 复核：伏击授权位置此刻无己方单位 → 位置不再有效
            if Keyword.AMBUSH in kws and any(state.obj(u).controller == player for u in bf.occupants):
                return
            # 开放战场位置选项（170.11.c：未占领且未受控制）
            if any(ab.kind == "location_open_battlefield" for ab in d.abilities) \
                    and bf.controller is None and not bf.occupants:
                return
            raise IllegalActionError(state.step_id, player, "",
                                     "battlefield not controlled (R-CR-359.2/822.3 伏击复核/170.11.c 开放)")


def _deflect_charges(state: GameState, player: int, targets) -> int:
    """法盾强制附加费计数（809.1.c/356.2.a.2）：
    对手控制的单位每被（由你控制的法术/技能）选作一次目标，法盾值累加进其费（809.2）。"""
    if targets is None:
        return 0
    if isinstance(targets, int):
        targets = [targets]
    total = 0
    for t in targets:
        if t not in state.objects:
            continue
        to = state.obj(t)
        if to.controller == player:
            continue  # 809.1.c 仅对「由对手控制且选我为目标」的法术/技能
        td = state.card_registry[to.def_id]
        v = td.keyword_values.get(Keyword.DEFLECT.value)
        if v is None and Keyword.DEFLECT in (set(td.keywords) | set(to.keywords_extra)):
            v = 1  # 无内嵌数值缺省=1（809.1.b.3）
        if v:
            total += v
    return total


def pay_auto(state: GameState, player: int, energy: int, power: dict[str, int]) -> None:
    """步骤 4 支付辅助：自动激活基本符文技能补缺口（357.1.a）。
    顺序：休眠优先回收补符能（[C] 特性匹配），再 [E] 活跃符文补法力。
    M1 自动化决策占位——P1 若需玩家显式选择激活序，改为 PAYMENT_CHOICE 请求点。"""
    p = state.players[player]
    for d, n in power.items():
        key = d.value if isinstance(d, Domain) else d
        if key == "A":
            continue  # [A] 在特性缺口补足后统一处理
        while p.rune_power.get(key, 0) < n:
            rune = _find_rune(state, player, want_domain=Domain(key), sleeping_first=True)
            if rune is None:
                raise IllegalActionError(state.step_id, player, "", f"no recyclable rune for [{key}] (R-CR-357.1)")
            _recycle_rune_for_gain(state, rune)
    specific_total = sum(n for d, n in power.items()
                         if (d.value if isinstance(d, Domain) else d) != "A")
    while sum(p.rune_power.values()) - specific_total < power.get("A", 0):
        # [A] 缺口：回收任意特性符文（805.1.a.2/809.1.c.1；休眠优先保留活跃产能）
        rune = _find_rune(state, player, want_domain=None, sleeping_first=True)
        if rune is None:
            raise IllegalActionError(state.step_id, player, "", "no recyclable rune for [A] (R-CR-357.1)")
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
    """常驻牌确认入场（359.2/337.2）：单位休眠进指定位置；装备活跃进基地。
    覆盖次序：「以活跃状态进场」文本（369.3）与 805 急速已付（805.1.a）→ 活跃；
    「以休眠状态进场」文本（369.3）覆盖默认。
    打出到非控战场令战场进入争夺（190.3.a.1）。
    进场类触发（817 预知 / 打出我时抽牌 383.1）随后入链。"""
    uid = item.source_uid
    o = state.obj(uid)
    d = state.card_registry[o.def_id]
    player = item.controller
    o.face_down = False
    o.entered_turn = state.turn_number
    enters_exhausted = any(ab.kind == "enters_exhausted" for ab in d.abilities)
    enters_ready = any(ab.kind == "enters_ready" for ab in d.abilities)
    accelerated = bool(item.choices.get("accelerate"))
    if CardType.UNIT in d.card_types:
        o.exhausted = enters_exhausted or not (enters_ready or accelerated)  # 默认 359.2.c 休眠
        kind, idx = item.choices["location"]
        if kind == "base":
            o.zone, o.zone_owner, o.battlefield = Zone.BASE, player, None
            state.base_occupants[player].append(uid)
        else:
            bf = state.battlefields[idx]
            o.zone, o.zone_owner, o.battlefield = Zone.BATTLEFIELD, None, idx
            bf.occupants.append(uid)
            if not bf.contested and bf.controller != player:
                bf.contested = True  # 190.3.a.1：被打出到非控战场的单位令战场进入争夺
                bf.contested_by = player
                emit(state, EventType.CONTEST, rule_ids=["R-CR-190.3.a.1"], card_ids=[f"uid:{uid}"],
                     public={"battlefield": idx, "by": player})
        rules = ["R-CR-359.2"]
        if enters_exhausted or enters_ready:
            rules.append("R-CR-369.3")
        if accelerated:
            rules.append("R-CR-805.1.a")
        emit(state, EventType.RESOLVE, rule_ids=rules, card_ids=[f"uid:{uid}"],
             public={"uid": uid, "entered": f"{kind}:{idx}", "exhausted": o.exhausted})
    else:  # GEAR（及其他非单位常驻）→基地默认活跃（359）；文本可改为休眠进场（369.3）
        o.exhausted = enters_exhausted
        o.zone, o.zone_owner, o.battlefield = Zone.BASE, player, None
        state.base_occupants[player].append(uid)
        rules = ["R-CR-359.3"] + (["R-CR-369.3"] if enters_exhausted else [])
        emit(state, EventType.RESOLVE, rule_ids=rules, card_ids=[f"uid:{uid}"],
             public={"uid": uid, "entered": "base", "exhausted": o.exhausted})
    _push_enter_triggers(state, item)


def _push_enter_triggers(state: GameState, item: ChainItem) -> None:
    """常驻进场触发入链（383.1/817.1.c）：预知→洞察（817.1.b）；「打出我时」抽牌。
    多触发排序（383.3.d）暂按 abilities 声明序入链（确定序；玩家自选序挂点）。
    cardfx 孤例：trigger kind 的 AbilityDef 带 resolve_fn 时随链项传递（383.1）。"""
    from . import chain_sys

    uid, player = item.source_uid, item.controller
    o = state.obj(uid)
    d = state.card_registry[o.def_id]
    for ab in d.abilities:
        if ab.kind == "trigger" and ab.resolve_fn:
            chain_sys.push(state, ChainItem(
                item_id=state.new_uid(), kind="trigger", source_uid=uid, controller=player,
                ability={"kind": "trigger", "origin": "trigger",
                         "ability_id": ab.ability_id, "resolve_fn": ab.resolve_fn,
                         "rules_ref": list(ab.rules_ref)},
                origin=o.zone,
            ))
    if Keyword.VISION in keywords_of(state, uid):
        chain_sys.push(state, ChainItem(
            item_id=state.new_uid(), kind="trigger", source_uid=uid, controller=player,
            ability={"kind": "vision_scout", "origin": "trigger",
                     "rules_ref": ["R-CR-817.1.b", "R-CR-817.1.c", "R-CR-436.1"]},
            origin=o.zone,
        ))
    for ab in d.abilities:
        if ab.kind not in ("on_play_draw", "on_play_pump"):
            continue
        payload = ({"kind": "on_play_draw", "draw_count": ab.draw_count or 1}
                   if ab.kind == "on_play_draw"
                   else {"kind": "on_play_pump", "pump_value": ab.pump_value})
        chain_sys.push(state, ChainItem(
            item_id=state.new_uid(), kind="trigger", source_uid=uid, controller=player,
            ability={**payload, "origin": "trigger",
                     "rules_ref": list(ab.rules_ref) or ["R-CR-383.1", "R-CR-413.1"]},
            origin=o.zone,
        ))
    # 819 灵便触发：打出时「将其贴附于你控制的一名单位上」（819.1.d）
    # 目标随打出宣言选定（355/383 选择时点近似——见 worklog TODO-383 目标时点确认）
    if Keyword.QUICKDRAW in keywords_of(state, uid):
        picked = (item.choices or {}).get("target")
        if picked is not None and int(picked) in _friendly_units(state, player):
            chain_sys.push(state, ChainItem(
                item_id=state.new_uid(), kind="trigger", source_uid=uid, controller=player,
                targets=[int(picked)],
                ability={"kind": "on_play_equip", "origin": "trigger",
                         "rules_ref": ["R-CR-819.1.d", "R-CR-716", "R-CR-818.2"]},
                origin=o.zone,
            ))


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
    """卡牌效果文本执行点（157 法术结算；白名单原语逐条独立执行，359.3.e.9 目标失效互不影响）。
    cardfx 孤例适配层：AbilityDef.resolve_fn 非空时优先调命名回调（cardfx.RESOLVERS），
    回调 (state, item, ability=AbilityDef) 自行结算；引擎原语 kind 结算跳过该条。"""
    from .cardfx import resolver_for
    from .resources import deal_damage as _deal
    from .resources import draw as _draw

    uid = item.source_uid
    d = state.card_registry[state.obj(uid).def_id]
    for ab in d.abilities:
        if ab.resolve_fn:
            resolver_for(ab.resolve_fn)(state, item, ab)
            continue
        if ab.kind == "spell_damage":
            tgt = item.choices.get("target")
            valid = set(deal_targets_of(state, ab.target_scope))
            if tgt in valid:
                _deal(state, tgt, ab.damage, source=f"spell:uid{uid}", rule="R-CR-417.1")
            else:
                emit(state, EventType.RESOLVE, rule_ids=["R-CR-359.3.e.9"],
                     card_ids=[f"uid:{tgt}"] if tgt is not None else [],
                     public={"item_id": item.item_id, "fizzle": "target_invalid", "uid": tgt})
        elif ab.kind == "spell_draw":
            _draw(state, item.controller, ab.draw_count or 1, rule="R-CR-413.1")
        elif ab.kind == "spell_pump":
            # 本回合临时修正（474 加减层；R-CR-317.2.c 回合结束失效）；目标结算时复查同 spell_damage
            tgt = item.choices.get("target")
            valid = set(deal_targets_of(state, ab.target_scope))
            if tgt in valid:
                o_t = state.obj(tgt)
                o_t.might_temp += ab.pump_value
                emit(state, EventType.RESOLVE, rule_ids=["R-CR-317.2.c"],
                     card_ids=[f"uid:{tgt}"],
                     public={"item_id": item.item_id, "pump": ab.pump_value, "uid": tgt})
            else:
                emit(state, EventType.RESOLVE, rule_ids=["R-CR-359.3.e.9"],
                     card_ids=[f"uid:{tgt}"] if tgt is not None else [],
                     public={"item_id": item.item_id, "fizzle": "target_invalid", "uid": tgt})


def apply_ability_resolution(state: GameState, item: ChainItem) -> None:
    """技能/触发结算（获得资源 164.2；deal_damage=377.1/417.1；
    on_play_draw=383.1/413.1；vision_scout=817.1.b/436；temporary_destroy=816.1.b）。"""
    from .resources import deal_damage as _deal
    from .resources import draw as _draw

    ab = item.ability or {}
    kind = ab.get("kind")
    player = item.controller
    if ab.get("resolve_fn"):
        from .cardfx import resolver_for

        resolver_for(ab["resolve_fn"])(state, item, ab)
        return
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
        if ab.get("grant_power_domain"):
            add_power(state, player, Domain(ab["grant_power_domain"]), 1)  # [C色]指定域（429.3）
    elif kind == "on_play_draw":
        _draw(state, player, int(ab.get("draw_count") or 1), rule="R-CR-413.1")
    elif kind == "on_play_pump":
        # 「打出我时」自身临时修正：源在场才施加（离场则无从施加；383.1 触发已入链仍需结算点复查）
        o = state.objects.get(item.source_uid)
        if o is not None and o.controller == player and o.zone in (Zone.BASE, Zone.BATTLEFIELD):
            o.might_temp += int(ab.get("pump_value") or 0)
            emit(state, EventType.RESOLVE, rule_ids=["R-CR-317.2.c"],
                 card_ids=[f"uid:{item.source_uid}"],
                 public={"item_id": item.item_id, "pump": ab.get("pump_value"),
                         "uid": item.source_uid})
        else:
            emit(state, EventType.RESOLVE, rule_ids=["R-CR-359.3.e.9"],
                 public={"item_id": item.item_id, "ignore": "source_left_board",
                         "uid": item.source_uid})
    elif kind == "vision_scout":
        _resolve_scout(state, item)
    elif kind == "temporary_destroy":
        o = state.objects.get(item.source_uid)
        if o is not None and o.controller == player and o.zone in (Zone.BASE, Zone.BATTLEFIELD):
            kill_(state, item.source_uid)
        else:
            emit(state, EventType.RESOLVE, rule_ids=["R-CR-816.1.b"],
                 public={"item_id": item.item_id, "ignore": "source_left_board",
                         "uid": item.source_uid})
    elif kind == "deal_damage":
        # 结算时复查目标范围（359.3.e.9 目标指定失效：不再符合范围的指示不执行）
        scope = ab.get("target_scope") or ""
        valid = set(deal_targets_of(state, scope))
        for tgt in item.targets:
            if tgt in valid:
                _deal(state, tgt, int(ab.get("damage") or 0),
                      source=f"ability:uid{item.source_uid}", rule="R-CR-417.1")
            else:
                emit(state, EventType.RESOLVE, rule_ids=["R-CR-359.3.e.9"],
                     card_ids=[f"uid:{tgt}"],
                     public={"item_id": item.item_id, "fizzle": "target_invalid", "uid": tgt})
    elif kind in ("equip", "on_play_equip"):
        # 818 主动技能结算 / 819 灵便触发结算共用（同为「源装备在场→贴附到目标」）
        _resolve_equip(state, item)
    elif kind == "trigger":
        _resolve_trigger_payload(state, item, ab)
    emit(state, EventType.RESOLVE, rule_ids=["R-CR-406"], public={"item_id": item.item_id, "ability": kind})


def _resolve_trigger_payload(state: GameState, item: ChainItem, ab: dict) -> None:
    """383 触发载荷 dispatch（triggers.fire 入链项结算）：
    score=触发控制者加 value 分（卡牌效果分，470 战场分限不适用）；channel=召 value 枚休眠符文（430.2/430.5 休眠进场）。"""
    from .resources import channel as _channel

    payload = ab.get("payload") or ""
    player = item.controller
    rules = list(ab.get("rules_ref") or [])
    if "R-CR-383.3" not in rules:
        rules.append("R-CR-383.3")
    if payload == "score":
        n = int(ab.get("value") or 1)
        state.players[player].score += n
        emit(state, EventType.SCORE, rule_ids=rules,
             public={"player": player, "kind": "trigger_score", "value": n,
                     "score": state.players[player].score, "source": item.source_uid})
    elif payload == "channel":
        n = int(ab.get("value") or 1)
        before = set(state.base_occupants[player])
        got = _channel(state, player, n)  # 430.1 默认活跃入场
        for uid in got:
            if uid not in before:
                state.obj(uid).exhausted = True  # 430.2：效果指明「休眠」→休眠状态入场
        if got:
            emit(state, EventType.RESOLVE, rule_ids=["R-CR-430.2", "R-CR-383.3"],
                 card_ids=[f"uid:{u}" for u in got],
                 public={"item_id": item.item_id, "channel_exhausted": got, "player": player})
    elif payload == "discard_draw":
        # 「弃置X张手牌，然后抽X张」：结算时由触发控制者选弃（383 选择时点近似，TODO-383 登记）；
        # 手牌为空→055 尽可能执行：弃置无视、抽仍执行（不发 CHOOSE）。
        from .resources import draw as _draw_follow

        hand = state.players[player].hand
        n = int(ab.get("value") or 1)
        if not hand:
            if n > 0:
                _draw_follow(state, player, n, rule="R-CR-413.1")
            emit(state, EventType.RESOLVE, rule_ids=rules,
                 public={"item_id": item.item_id, "ignore": "discard_no_hand", "player": player})
        else:
            from .actions import DecisionRequest
            from .enums import DecisionKind

            state.current_request = DecisionRequest(
                DecisionKind.CHOOSE_MODE, player,
                options={"choices": sorted(hand), "reason": "trigger_discard",
                         "then_draw": n, "source_uid": item.source_uid,
                         "item_id": item.item_id},
            ).to_dict()
    elif payload == "pump_turn":
        # 「给我 +N 战力本回合」（VEN-011 类）：me=顶部卡（719.1 文本添加）→宿主 might_temp；
        # 317.2.c/d 回合结束失效（phaser 3d 已有清除）。结算时宿主离场/已卸除→无视（359.3.e.12）。
        go = state.objects.get(item.source_uid)
        host = (state.objects.get(go.attached_to)
                if go is not None and go.attached_to is not None else None)
        if host is not None and host.zone in (Zone.BASE, Zone.BATTLEFIELD):
            n = int(ab.get("value") or 0)
            host.might_temp += n
            emit(state, EventType.RESOLVE, rule_ids=rules + ["R-CR-317.2.c"],
                 card_ids=[f"uid:{host.uid}"],
                 public={"item_id": item.item_id, "pump": n, "uid": host.uid})
        else:
            emit(state, EventType.RESOLVE, rule_ids=rules + ["R-CR-359.3.e.12"],
                 public={"item_id": item.item_id, "fizzle": "host_gone", "uid": item.source_uid})
    elif payload in ("deal_all_enemy_here", "deal_enemy_here"):
        # SFD-190/016 类「此处敌单位」伤害：me=宿主（719.1）；here=宿主所在战场（719.3.a 位置同步）。
        # 结算复查：源仍贴附、宿主在场且位于战场（359.3.e.12 失依→fizzle）。
        from .resources import deal_damage as _deal_here

        go = state.objects.get(item.source_uid)
        host = (state.objects.get(go.attached_to)
                if go is not None and go.attached_to is not None else None)
        if go is None or host is None or host.zone != Zone.BATTLEFIELD or host.battlefield is None:
            emit(state, EventType.RESOLVE, rule_ids=rules + ["R-CR-359.3.e.12"],
                 public={"item_id": item.item_id, "fizzle": "host_gone", "uid": item.source_uid})
        else:
            bf = state.battlefields[host.battlefield]
            foes = sorted(
                u for u in bf.occupants
                if state.obj(u).controller != player
                and CardType.UNIT in state.card_registry[state.obj(u).def_id].card_types
                and state.obj(u).attached_to is None
            )  # uid 确定序
            n = int(ab.get("value") or 0)
            if payload == "deal_all_enemy_here":
                if not foes:
                    emit(state, EventType.RESOLVE, rule_ids=rules + ["R-CR-359.3.e.9"],
                         public={"item_id": item.item_id, "fizzle": "no_targets"})
                for u in foes:
                    _deal_here(state, u, n, source=f"trigger:uid{go.uid}", rule="R-CR-417.1")
            else:  # deal_enemy_here：结算时由触发控制者选目标（383 选择时点近似，TODO-383 登记）
                if not foes:
                    emit(state, EventType.RESOLVE, rule_ids=rules + ["R-CR-359.3.e.9"],
                         public={"item_id": item.item_id, "fizzle": "no_targets",
                                 "uid": item.source_uid})
                else:
                    from .actions import DecisionRequest
                    from .enums import DecisionKind

                    state.current_request = DecisionRequest(
                        DecisionKind.CHOOSE_MODE, player,
                        options={"choices": foes, "reason": "trigger_deal_enemy_here",
                                 "damage": n, "source_uid": go.uid,
                                 "item_id": item.item_id},
                    ).to_dict()
    elif payload == "unattach_self_deal_host":
        # UNL-019 类「将此牌卸除，并对我造成 N 点伤害」：me=顶部卡（719.1 贴附卡文本添加到宿主）→伤害落宿主。
        # 435.1.a.1：结算时已不贴附→整体无效果（宿主死亡经 719.5 已自动卸除；359.3.e.12 信息失依同）。
        from .resources import deal_damage as _deal_host

        go = state.objects.get(item.source_uid)
        host_uid = go.attached_to if go is not None else None
        host = state.objects.get(host_uid) if host_uid is not None else None
        host_on_board = host is not None and host.zone in (Zone.BASE, Zone.BATTLEFIELD)
        if go is None or host_uid is None or not host_on_board:
            emit(state, EventType.RESOLVE, rule_ids=["R-CR-435.1.a.1", "R-CR-383.3"],
                 public={"item_id": item.item_id, "fizzle": "not_attached_or_host_gone",
                         "uid": item.source_uid})
        else:
            # 435.1/b 断开贴附：效果文本即失活（435.1.c/d/e）；装备留宿主当前区域（同 719.5 面登记）
            host_zone, host_owner, host_bf = host.zone, host.zone_owner, host.battlefield
            host.attachments.remove(item.source_uid)
            go.attached_to = None
            go.zone, go.zone_owner, go.battlefield = host_zone, host_owner, host_bf
            if host_zone == Zone.BASE and host_owner is not None:
                state.base_occupants[host_owner].append(go.uid)
            elif host_zone == Zone.BATTLEFIELD and host_bf is not None:
                state.battlefields[host_bf].occupants.append(go.uid)
            emit(state, EventType.DETACH, rule_ids=["R-CR-435.1", "R-CR-435.1.b"],
                 card_ids=[f"uid:{go.uid}", f"uid:{host_uid}"],
                 public={"item_id": item.item_id, "gear": go.uid, "host": host_uid})
            _deal_host(state, host_uid, int(ab.get("value") or 0),
                       source=f"trigger:uid{go.uid}", rule="R-CR-417.1")
    else:
        emit(state, EventType.RESOLVE, rule_ids=rules,
             public={"item_id": item.item_id, "unwired_payload": payload, "uid": item.source_uid})


def _resolve_equip(state: GameState, item: ChainItem) -> None:
    """装配/打出贴附结算（818 主动技能 / 819 灵便触发，共用）：
    目标复查（仍是己方在场单位，359.3.e.9）→ 贴附建立（818.2/717）。
    失效时装备滞留其当前区域（359.3.e.6 指示无视；对照 821.1.c.5 同原则）。"""
    tgt = item.targets[0] if item.targets else None
    host = state.objects.get(tgt) if tgt is not None else None
    src = state.obj(item.source_uid)
    valid = (
        host is not None
        and host.zone in (Zone.BASE, Zone.BATTLEFIELD)
        and host.controller == item.controller
        and CardType.UNIT in state.card_registry[host.def_id].card_types
        and src.zone in (Zone.BASE, Zone.BATTLEFIELD)
        and src.attached_to is None
        and src.controller == item.controller
    )
    if not valid:
        emit(state, EventType.RESOLVE, rule_ids=["R-CR-359.3.e.9"],
             card_ids=[f"uid:{tgt}"] if tgt is not None else [],
             public={"item_id": item.item_id, "fizzle": "target_invalid", "uid": tgt})
        return
    # 装备从当前区域（基地/战场）移除并贴附（719.3 同位置；719.4 状态独立）
    from .resources import _untrack as _untrack_board

    _untrack_board(state, item.source_uid)
    src.zone, src.zone_owner, src.battlefield = host.zone, host.zone_owner, host.battlefield
    src.attached_to = tgt
    host.attachments.append(item.source_uid)
    emit(state, EventType.ATTACH, rule_ids=["R-CR-818.2", "R-CR-717", "R-CR-719.3"],
         card_ids=[f"uid:{item.source_uid}", f"uid:{tgt}"],
         public={"item_id": item.item_id, "gear": item.source_uid, "host": tgt})


def _resolve_scout(state: GameState, item: ChainItem) -> None:
    """洞察 1（817.1.b → 436.1）：看顶牌 → SCOUT_KEEP 决策（可选回收，817.2.a）。
    牌堆不足按实数洞察（436.4）且不燃尽（436.4.a）；uid 仅特权载荷可见。"""
    from .actions import DecisionRequest
    from .enums import DecisionKind

    player = item.controller
    deck = state.players[player].main_deck
    if not deck:
        emit(state, EventType.EXECUTE, rule_ids=["R-CR-436.4", "R-CR-436.4.a"],
             public={"player": player, "scout_empty": True})
        return
    top = deck[-1]
    emit(state, EventType.EXECUTE, rule_ids=["R-CR-436.1", "R-CR-817.2.a"],
         public={"player": player, "scout_look": 1}, privileged={"uids": [top]})
    state.current_request = DecisionRequest(
        DecisionKind.SCOUT_KEEP, player, options={"uids": [top]},
    ).to_dict()


def kill_(state: GameState, uid: int) -> None:
    from .resources import kill

    kill(state, uid, rule="R-CR-816.1.b", via="temporary")


def handle_activate(state: GameState, action: Action, *, in_reaction: bool = False) -> None:
    """激活主动技能（377/401）：入链为 pending 技能项；获得资源类确认立即结算（429.2）。"""
    player, uid = action.actor, action.source_uid
    o = state.obj(uid)
    d = state.card_registry[o.def_id]
    ability_id = action.params.get("ability_id")
    ab = next((a for a in d.abilities if a.ability_id == ability_id), None)
    if ab is None:
        raise IllegalActionError(state.step_id, player, action.digest(), f"no such ability {ability_id}")
    if ab.kind not in _ACTIVATABLE_KINDS:
        raise IllegalActionError(state.step_id, player, action.digest(), f"kind {ab.kind} not activatable (R-CR-377.1)")
    if ab.cost_exhaust_self and o.exhausted:
        raise IllegalActionError(state.step_id, player, action.digest(), "source exhausted for [E] (R-CR-377/414)")
    # 目标范围复核（防御；合法集在 step 已断言成员资格，此处防手工构造）
    targets: list[int] = []
    if ab.kind == "deal_damage":
        tgt = action.params.get("target")
        if tgt is None or tgt not in deal_targets_of(state, ab.target_scope):
            raise IllegalActionError(state.step_id, player, action.digest(),
                                     f"invalid target for {ab.target_scope} (R-CR-355.6)")
        targets = [int(tgt)]
    if ab.kind == "equip":
        # 818.1：装配是场上（基地）装备的主动技能；目标限「你控制的一名单位」（818.1.c.2）
        if o.zone != Zone.BASE or o.zone_owner != player or o.attached_to is not None:
            raise IllegalActionError(state.step_id, player, action.digest(),
                                     "equip source must be your gear on board (base) (R-CR-818.1)")
        tgt = action.params.get("target")
        if tgt is None or int(tgt) not in _friendly_units(state, player):
            raise IllegalActionError(state.step_id, player, action.digest(),
                                     "equip target must be a unit you control (R-CR-818.1.c.2)")
        targets = [int(tgt)]
    # 时机权限（防御复核；legal 已过滤）
    if not in_reaction and not can_use_timing(state, player, ab.timing, in_reaction=False):
        raise IllegalActionError(state.step_id, player, action.digest(), "timing (R-CR-381)")
    # 法盾强制附加费：技能选取对手单位为目标时须先支付 [A]（809.1.c/356.2.a.2）
    deflect_n = _deflect_charges(state, player, targets)
    if deflect_n:
        pay_auto(state, player, 0, {"A": deflect_n})
    # 818.1.b/818.1.c.3：装配费用（可含法力与特性符能）
    if ab.kind == "equip":
        eq_energy, eq_power = _apply_symbols(0, {}, ab.cost_symbols)
        pay_auto(state, player, eq_energy, eq_power)
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
        targets=targets,
        ability={
            # 429.2 立即结算仅限获得资源技能；装配等同其他主动技能走链（377/378）
            "ability_id": ab.ability_id, "kind": ab.kind,
            "immediate": ab.immediate if ab.kind != "equip" else False,
            "grant_energy": ab.grant_energy,
            "grant_power_self_domain": ab.grant_power_self_domain,
            "domain": next(iter(d.domains)).value if (ab.grant_power_self_domain and d.domains) else None,
            "grant_power_domain": ab.grant_power_domain,
            "damage": ab.damage, "target_scope": ab.target_scope,
            "origin": "gain_ability" if ab.kind == "gain_resource" else "player_action",
            "rules_ref": list(ab.rules_ref),
            "resolve_fn": ab.resolve_fn,
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
