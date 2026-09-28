# CardDefinition 与骨架卡池（阶段 3 卡池 skeleton-v1，docs/implementation_scope.md §3）。
# 卡定义非规则权威；效果文本阶段 4 起按 KB canonical 逐卡接入（R-CARD deferred）。
from __future__ import annotations

from dataclasses import dataclass, field

from .enums import CardType, Domain, Keyword
from .version import CARD_POOL_VERSION


@dataclass(frozen=True)
class AbilityDef:
    """技能的结构化描述骨架（MECH-ABILITIES-OVERVIEW）。
    M1 仅支持符文自带两类获得资源技能（R-CR-164.2）与框架位；
    P1/阶段 4 接入效果原语后扩展 op/tags。
    """

    ability_id: str
    kind: str            # "gain_resource" | "play_primitive"(预留)
    timing: str = "action"   # "action"(己方回合开环) | "reaction"(闭环亦可, 813)
    cost_exhaust_self: bool = False   # [E] 费用（377.2.a.1）
    cost_recycle_self: bool = False   # 回收此牌费用
    grant_energy: int = 0             # 获得法力数
    grant_power_self_domain: bool = False  # [C]：获得牌自身特性符能
    immediate: bool = True            # 获得资源技能确认后立即结算（429.2/337.2）
    rules_ref: tuple[str, ...] = ()


@dataclass(frozen=True)
class CardDefinition:
    """卡面属性集合（R-CR-129..137）。费用判定以印刷为准（R-CR-206）。"""

    def_id: str
    name: str
    card_types: frozenset[CardType]
    domains: frozenset[Domain] = frozenset()       # 特性；空=无色（费用符号 [C] 按 805.1.a.2 走）
    cost_energy: int = 0                           # 法力费
    cost_power: tuple[Domain, ...] = ()            # 符能需求（按数量计）
    might: int | None = None                       # 战力（单位）
    might_bonus: int | None = None                 # 战力加成（装备 137）
    tags: frozenset[str] = frozenset()             # 标签：hero / 专属等（133.4）
    hero_tag: str | None = None                    # 英雄标签（103.2.a.2 选定英雄匹配键）
    keywords: frozenset[Keyword] = frozenset()     # 印刷关键词（800）
    abilities: tuple[AbilityDef, ...] = ()         # 规则文本技能（135）
    pool: str = CARD_POOL_VERSION

    @property
    def is_hero(self) -> bool:
        return "hero" in self.tags

    @property
    def is_permanent_card(self) -> bool:
        """常驻牌口径：单位/装备（打出后进场上区域；法术非常驻，157）。"""
        return bool(self.card_types & {CardType.UNIT, CardType.GEAR})


# ---------------------------------------------------------------- 骨架卡池 defs
_D = Domain

_BASIC_RUNE_ABILITIES = (
    AbilityDef(
        ability_id="rune_exhaust_gain",
        kind="gain_resource",
        timing="reaction",          # [反应]（164.2）
        cost_exhaust_self=True,
        grant_energy=1,
        rules_ref=("R-CR-164.2",),
    ),
    AbilityDef(
        ability_id="rune_recycle_gain",
        kind="gain_resource",
        timing="reaction",
        cost_recycle_self=True,
        grant_power_self_domain=True,   # [C]
        rules_ref=("R-CR-164.2",),
    ),
)


def basic_rune(card_index: int, domain: Domain) -> CardDefinition:
    return CardDefinition(
        def_id=f"sk:rune:{domain.value}:{card_index}",
        name=f"基本符文-{domain.value}#{card_index}",
        card_types=frozenset({CardType.RUNE}),
        domains=frozenset({domain}),
        abilities=_BASIC_RUNE_ABILITIES,
    )


def _mk_units() -> list[CardDefinition]:
    # 无文本骨架单位：U2=2[R]/2[M]，U3=3[R]/3[M]，U4=4[R]/4[M]（均为 hero_tag=None）
    out = []
    for i in range(1, 14):
        for tag, cost, might in (("u2", 2, 2), ("u3", 3, 3)):
            out.append(
                CardDefinition(
                    def_id=f"sk:unit:{tag}:{i}",
                    name=f"骨架单位{tag.upper()}-{i}",
                    card_types=frozenset({CardType.UNIT}),
                    domains=frozenset({_D.R}),
                    cost_energy=cost,
                    cost_power=(_D.R,),
                    might=might,
                )
            )
    return out


def skeleton_legend(hero_tag: str) -> CardDefinition:
    return CardDefinition(
        def_id=f"sk:legend:{hero_tag}",
        name=f"骨架传奇-{hero_tag}",
        card_types=frozenset({CardType.LEGEND}),
        domains=frozenset({_D.R}),
        hero_tag=hero_tag,
    )


def skeleton_hero(hero_tag: str) -> CardDefinition:
    return CardDefinition(
        def_id=f"sk:hero:{hero_tag}",
        name=f"选定英雄-{hero_tag}",
        card_types=frozenset({CardType.UNIT}),
        domains=frozenset({_D.R}),
        cost_energy=5,
        cost_power=(_D.R,),
        might=5,
        tags=frozenset({"hero"}),
        hero_tag=hero_tag,
    )


def skeleton_battlefield(name: str, idx: int) -> CardDefinition:
    return CardDefinition(
        def_id=f"sk:battlefield:{idx}",
        name=f"骨架战场-{name}",
        card_types=frozenset({CardType.BATTLEFIELD}),
        domains=frozenset(),
    )


def skeleton_gear(idx: int) -> CardDefinition:
    return CardDefinition(
        def_id=f"sk:gear:g1:{idx}",
        name=f"骨架装备-{idx}",
        card_types=frozenset({CardType.GEAR}),
        domains=frozenset({_D.R}),
        cost_energy=1,
        cost_power=(_D.R,),
        might_bonus=1,
    )


def skeleton_spell(idx: int) -> CardDefinition:
    return CardDefinition(
        def_id=f"sk:spell:s1:{idx}",
        name=f"骨架法术-{idx}",
        card_types=frozenset({CardType.SPELL}),
        domains=frozenset({_D.R}),
        cost_energy=1,
        cost_power=(_D.R,),
    )


@dataclass(frozen=True)
class DeckList:
    """卡组配置（组卡校验输入，R-CR-103）。各成员为 CardDefinition。"""

    legend: CardDefinition
    chosen_hero: CardDefinition
    main_deck: tuple[CardDefinition, ...]      # 含选定英雄 1 张，共 ≥40（103.2）
    rune_deck: tuple[CardDefinition, ...]      # 恰 12 张符文（103.3.a）
    battlefields: tuple[CardDefinition, ...]   # 模式数量（1v1=3，Setup 各选 1）
    deck_id: str = ""


def make_skeleton_deck(deck_id: str, hero_tag: str, rng_seed_note: str = "") -> DeckList:
    """F-DECK-A/B（spec/rule_test_matrix.md §0）：传奇+选定英雄+39 混编+12 [R] 符文+3 战场。"""
    legend = skeleton_legend(hero_tag)
    hero = skeleton_hero(hero_tag)
    units = _mk_units()
    main: list[CardDefinition] = [hero]
    # 39 张混编：13×(u2+u3) + 7 gear + 6 spell，同名均 ≤3
    main.extend(units)
    main.extend(skeleton_gear(i) for i in range(1, 8))
    main.extend(skeleton_spell(i) for i in range(1, 7))
    assert len(main) == 40, len(main)
    runes = tuple(basic_rune(i, _D.R) for i in range(1, 13))
    bfs = tuple(skeleton_battlefield(f"{deck_id}-B{i}", i) for i in range(1, 4))
    return DeckList(
        legend=legend,
        chosen_hero=hero,
        main_deck=tuple(main),
        rune_deck=runes,
        battlefields=bfs,
        deck_id=deck_id,
    )
