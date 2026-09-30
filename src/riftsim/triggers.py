# 触发式技能注册表（383 首批 2026-10-01）
# 锚点：383.3 条件满足时触发式技能入链（如主动技能）；383.3.d 同时多触发由玩家定序（MVP uid 确定序→见 worklog）。
# 宿主条件（MVP）：装备触发仅当其 attached_to 宿主单位在触发战场且触发者为控制者；条件不满足不注册（383.3 前置）。
from __future__ import annotations

from . import chain_sys
from .chain_sys import ChainItem
from .state import GameState

# 载荷 dispatch 由 playing.apply_ability_resolution 处理
EVENTS = frozenset({"hold", "conquer"})


def _iter_trigger_holders(state: GameState, event: str, player: int | None, battlefield_index: int | None):
    """产出 (gear_uid, ab, go)：宿主在触发战场、装备控制者==player（「我据守/征服」的我），且 ability 声明 trigger==event。
    battlefield_index 为 None 时遍历全场宿主及其贴附装备。"""
    seen: set[int] = set()

    def _emit_for_host(host_uid: int):
        host = state.objects.get(host_uid)
        if host is None:
            return
        for gear_uid in host.attachments:
            if gear_uid in seen:
                continue
            go = state.objects.get(gear_uid)
            if go is None:
                continue
            if player is not None and go.controller != player:
                continue  # 卡面「当我…」：仅触发者自己控制的装备触发
            d = state.card_registry[go.def_id]
            for ab in d.abilities:
                if ab.kind == "trigger" and ab.trigger == event:
                    # 383.3 前置：卡面条件不满足则不注册（UNL-019 类「如果我未在本回合内征服」）
                    if ab.condition == "no_conquer_this_turn" and state.players[go.controller].conquered_this_turn:
                        continue
                    seen.add(gear_uid)
                    yield (gear_uid, ab, go)

    if battlefield_index is not None:
        bf = state.battlefields[battlefield_index]
        for host_uid in list(bf.occupants):
            yield from _emit_for_host(host_uid)
    else:
        for uid, o in list(state.objects.items()):
            if o.attachments:
                yield from _emit_for_host(uid)


def fire(state: GameState, event: str, *, player: int | None = None, battlefield_index: int | None = None) -> None:
    """383.3：条件满足的触发式技能入链。uid 确定序（383.3.d 玩家定序先记近似）。"""
    for gear_uid, ab, go in _iter_trigger_holders(state, event, player, battlefield_index):
        chain_sys.push(state, ChainItem(
            item_id=state.new_uid(), kind="trigger",
            source_uid=gear_uid, controller=go.controller,
            ability={"kind": "trigger", "payload": ab.payload, "value": ab.value,
                     "trigger": ab.trigger, "condition": ab.condition,
                     "rules_ref": list(ab.rules_ref) or ["R-CR-383.3"]},
            origin=go.zone,
        ))
