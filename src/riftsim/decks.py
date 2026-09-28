# 组卡校验（MECH-DECK-CONSTRUCTION，R-CR-101..103；测试 T-0001..T-0006）
from __future__ import annotations

from collections import Counter

from .cards import DeckList
from .enums import CardType
from .errors import DeckValidationError


def validate_deck(deck: DeckList, *, mode: str = "duel_1v1") -> list[str]:
    """返回违规列表；空列表=合法。调用方视非空为 DeckValidationError。

    覆盖：103.1（符文特性）、103.2（主牌堆≥40、选定英雄、同名≤3、专属≤3）、
    103.3.a（符文堆恰 12、特性）、103.4.c（同名战场≤1）、825 唯我（骨架池暂不具备，
    允许 keywords 含 UNIQUE 的卡时生效）。
    """
    v: list[str] = []

    legend = deck.legend
    if CardType.LEGEND not in legend.card_types:
        v.append("R-CR-103.1: 传奇必须是传奇类型")
    legend_domains = set(legend.domains)
    if not legend_domains:
        v.append("R-CR-103.1.b.1: 传奇必须至少有一种特性来决定符文特性")

    # ---- 103.2 主牌堆 ----
    if len(deck.main_deck) < 40:
        v.append(f"R-CR-103.2: 主牌堆不足 40（现有 {len(deck.main_deck)}）")
    hero = deck.chosen_hero
    if not hero.is_hero or CardType.UNIT not in hero.card_types:
        v.append("R-CR-103.2.a: 选定英雄必须是英雄单位")
    if hero.hero_tag != legend.hero_tag:
        v.append("R-CR-103.2.a.2: 选定英雄的英雄标签必须与传奇一致")
    if sum(1 for c in deck.main_deck if c.def_id == hero.def_id) != 1:
        v.append("R-CR-103.2.a.1: 主牌堆必须含恰好 1 张选定英雄")

    # 特性同一性（103.1.b.3/4）：单特性卡须同，多特性卡须全部同
    for c in deck.main_deck:
        cdom = set(c.domains)
        if not cdom:
            continue  # 无色卡（无特性）不限制（103.3 无色符文/卡备注在规则卡说明）
        if len(cdom) == 1:
            if not cdom.issubset(legend_domains):
                v.append(f"R-CR-103.1.b.3: {c.name} 特性 {dom_str(cdom)} 不属于卡组特性")
        else:
            if not cdom.issubset(legend_domains):
                v.append(f"R-CR-103.1.b.4: 多特性卡 {c.name} 的特性须全部属于卡组特性")

    # 同名 ≤3（103.2.b），按名称计数（选定英雄计入；[唯我] 字面值 "unique"=825）
    names = Counter(c.name for c in deck.main_deck)
    for name, n in names.items():
        defs = [c for c in deck.main_deck if c.name == name]
        limit = 1 if any("unique" in {k.value for k in c.keywords} for c in defs) else 3
        if n > limit:
            v.append(f"R-CR-103.2.b: 同名卡「{name}」{n} 张超过上限 {limit}")
    # 专属卡合计 ≤3（103.2.d）
    if legend.hero_tag:
        exclusive = [
            c for c in deck.main_deck
            if c.hero_tag == legend.hero_tag and not c.is_hero and "signature" in c.tags
        ]
        if len(exclusive) > 3:
            v.append(f"R-CR-103.2.d: 专属卡 {len(exclusive)} 张超过上限 3")

    # ---- 103.3.a 符文牌堆恰 12 ----
    if len(deck.rune_deck) != 12:
        v.append(f"R-CR-103.3.a: 符文牌堆须为 12（现有 {len(deck.rune_deck)}）")
    for r in deck.rune_deck:
        if CardType.RUNE not in r.card_types:
            v.append(f"R-CR-103.3: 符文牌堆成员 {r.name} 不是符文")
        elif r.domains and not set(r.domains).issubset(legend_domains):
            v.append(f"R-CR-103.3.a.1: 符文 {r.name} 特性不符合符文特性")

    # ---- 103.4.c 同名战场 ≤1 ----
    bf_names = Counter(b.name for b in deck.battlefields)
    for name, n in bf_names.items():
        if n > 1:
            v.append(f"R-CR-103.4.c: 同名战场「{name}」超过 1 个")
    return v


def dom_str(domains: set) -> str:
    return "[" + "][".join(sorted(d.value if hasattr(d, "value") else d for d in domains)) + "]"


def assert_deck(deck: DeckList, *, mode: str = "duel_1v1") -> None:
    violations = validate_deck(deck, mode=mode)
    if violations:
        raise DeckValidationError(violations)
