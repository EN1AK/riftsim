# 测试辅助：快速状态构造与注入（fixture DSL 的最小实现，tests/fixture.py 前身）
from __future__ import annotations

from riftsim import engine
from riftsim.actions import Action
from riftsim.cards import AbilityDef, CardDefinition, make_skeleton_deck
from riftsim.config import GameConfig
from riftsim.enums import ActionKind, CardType, Domain, Keyword, Phase, Zone
from riftsim.objects import GameObject


RUNE_ABILITIES = (
    AbilityDef(ability_id="rune_exhaust_gain", kind="gain_resource", timing="reaction",
               cost_exhaust_self=True, grant_energy=1, rules_ref=("R-CR-164.2",)),
    AbilityDef(ability_id="rune_recycle_gain", kind="gain_resource", timing="reaction",
               cost_recycle_self=True, grant_power_self_domain=True, rules_ref=("R-CR-164.2",)),
)


def rune_def(idx, domain=Domain.R):
    return {"def_id": f"t:rune:{idx}", "name": f"p 符文{idx}", "card_types": {CardType.RUNE},
            "domains": {domain}, "abilities": RUNE_ABILITIES}


def cfg() -> GameConfig:
    return GameConfig(decks=(make_skeleton_deck("A", "hero-a"), make_skeleton_deck("B", "hero-b")))


def fresh(seed: int = 42):
    """reset 后双方 0 张调度，回到先手玩家主阶段行动窗。"""
    st = engine.reset(seed, cfg())
    first = st.meta.config["first_player"]
    engine.step(st, Action(ActionKind.RESOLVE_CHOICE, first, params={"set_aside": []}))
    engine.step(st, Action(ActionKind.RESOLVE_CHOICE, 1 - first, params={"set_aside": []}))
    return st, first


def spawn_card(state, def_dict: dict, owner: int, zone: Zone, **obj_kwargs) -> int:
    """注入一张自定义卡（测试基建）；def_dict 覆盖骨架 def 的关键字段。"""
    d = CardDefinition(
        def_id=def_dict["def_id"], name=def_dict.get("name", def_dict["def_id"]),
        card_types=frozenset(def_dict["card_types"]),
        domains=frozenset(def_dict.get("domains", {Domain.R})),
        cost_energy=def_dict.get("cost_energy", 0),
        cost_power=tuple(def_dict.get("cost_power", ())),
        might=def_dict.get("might"),
        might_bonus=def_dict.get("might_bonus"),
        tags=frozenset(def_dict.get("tags", ())),
        hero_tag=def_dict.get("hero_tag"),
        keywords=frozenset(def_dict.get("keywords", ())),
        abilities=tuple(def_dict.get("abilities", ())),
    )
    state.card_registry[d.def_id] = d
    uid = state.new_uid()
    o = GameObject(uid=uid, def_id=d.def_id, owner=owner, controller=owner,
                   zone=zone, zone_owner=owner if zone not in (Zone.BATTLEFIELD,) else None,
                   **obj_kwargs)
    state.objects[uid] = o
    return uid


def give_hand(state, player: int, def_dict: dict, **kw) -> int:
    uid = spawn_card(state, def_dict, player, Zone.HAND, **kw)
    state.players[player].hand.append(uid)
    return uid


def place_base(state, player: int, def_dict: dict, *, exhausted: bool = False, **kw) -> int:
    uid = spawn_card(state, def_dict, player, Zone.BASE, exhausted=exhausted, **kw)
    state.base_occupants[player].append(uid)
    return uid


def place_battlefield_unit(state, player: int, bf_index: int, might: int = 2, *, exhausted: bool = False,
                           keywords: tuple = (), damage: int = 0, name: str = "测试单位") -> int:
    uid = spawn_card(
        state,
        {"def_id": f"test:unit:{state.next_uid}", "name": name,
         "card_types": {CardType.UNIT}, "domains": {Domain.R},
         "cost_energy": might, "cost_power": (Domain.R,), "might": might,
         "keywords": keywords},
        player, Zone.BATTLEFIELD, battlefield=bf_index, exhausted=exhausted, damage=damage,
    )
    state.battlefields[bf_index].occupants.append(uid)
    return uid


def first_main_actions(state, first: int):
    """便捷：当前 MAIN_ACTION 请求下先手玩家的合法动作。"""
    return engine.legal_actions(state, first)


def end_main(state, player: int):
    return engine.step(state, Action(ActionKind.END_MAIN, player))
