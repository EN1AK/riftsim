# 卡牌数据库加载器（阶段 4）：cards_bilingual.db → CardDefinition 注册表。
# 卡面文本不是规则权威（AGENTS.md §0）；效果文本仅交 effects.py 白名单严格解析，
# schema 无法精确表示的卡记为 unsupported（不猜）。
# 版本口径（docs/api_contract.md §2/§10）：card_db_version = 卡池内容哈希 + 来源标注。
from __future__ import annotations

import functools
import hashlib
import json
import sqlite3
from dataclasses import dataclass

from .cards import AbilityDef, CardDefinition
from .cardfx import apply_fx as _apply_cardfx
from .enums import CardType, Domain

CARDDB_SOURCE = "cards_bilingual.db"

# 特性映射（官网 domain_en ↔ color_cn 双色命名 1:1 互证，见 .tmp/probe_domains 输出）：
# domain_en 优先；如缺省（token/异画符文等）按 color_cn 单色回填，回填行为记入审计。
_DOMAIN_BY_EN = {
    "Fury": Domain.R,    # 红色
    "Calm": Domain.G,    # 绿色
    "Mind": Domain.B,    # 蓝色
    "Body": Domain.O,    # 橙色
    "Order": Domain.Y,   # 黄色
    "Chaos": Domain.P,   # 紫色
}
_DOMAIN_BY_CN_COLOR = {
    "红色": Domain.R, "绿色": Domain.G, "蓝色": Domain.B,
    "橙色": Domain.O, "黄色": Domain.Y, "紫色": Domain.P,
}

# 类型映射：type_en 优先，缺失时以 type_cn 兜底（ARC 系列无英栏）。
_TYPE_BY_EN = {
    "Unit": CardType.UNIT, "Spell": CardType.SPELL, "Gear": CardType.GEAR,
    "Rune": CardType.RUNE, "Legend": CardType.LEGEND, "Battlefield": CardType.BATTLEFIELD,
}
_TYPE_BY_CN = {
    "单位": CardType.UNIT, "英雄单位": CardType.UNIT, "指示物单位": CardType.UNIT,
    "法术": CardType.SPELL, "专属法术": CardType.SPELL,
    "装备": CardType.GEAR, "专属装备": CardType.GEAR, "指示物装备": CardType.GEAR,
    "符文": CardType.RUNE, "传奇": CardType.LEGEND,
    "战场": CardType.BATTLEFIELD, "指示物战场": CardType.BATTLEFIELD,
    "专属单位": CardType.UNIT,
}

# 基本符文自带技能（R-CR-164.2；与骨架池 basic_rune 同一结构，ability_id 保持一致）
_BASIC_RUNE_ABILITIES = (
    AbilityDef(
        ability_id="rune_exhaust_gain", kind="gain_resource", timing="reaction",
        cost_exhaust_self=True, grant_energy=1, rules_ref=("R-CR-164.2",),
    ),
    AbilityDef(
        ability_id="rune_recycle_gain", kind="gain_resource", timing="reaction",
        cost_recycle_self=True, grant_power_self_domain=True, rules_ref=("R-CR-164.2",),
    ),
)

# 参与内容哈希的列（loader 实际消费的语义列；id/图片/稀有度等不影响对局语义的列不参与）
_HASH_COLUMNS = (
    "card_key", "name_en", "name_cn", "type_en", "type_cn", "super_type",
    "domain_en", "color_cn", "energy", "rune_power", "might", "might_bonus",
    "hero_cn", "tags_en", "text_en", "text_cn",
)


@dataclass(frozen=True)
class UnsupportedCard:
    """无法精确表示的卡（schema 外类型 / 混色符能费用等），附原因；绝不猜。
    作为 _build_definition 的返回值哨兵（而非异常）在 loader 中分流。"""

    card_key: str
    reason: str


@dataclass(frozen=True)
class ParseConflict:
    """CN/EN 白名单解析不一致（记录进覆盖报告；解析以 CN 为权威面）。"""

    card_key: str
    detail: str


@dataclass
class CardDbAudit:
    """加载审计数据：覆盖报告（reports/card_coverage.md）的事实来源。"""

    total_rows: int = 0
    unsupported: list[UnsupportedCard] = None        # type: ignore[assignment]
    conflicts: list[ParseConflict] = None            # type: ignore[assignment]
    keyword_cards: dict[str, list[str]] = None       # Keyword.value -> 含该关键词的 card_key 序
    hook_cards: dict[str, list[str]] = None          # hook 名 -> 命中的 card_key 序
    unparsed_text_cards: list[str] = None            # 有非空文本但白名单未覆盖（部分支持）
    derived_domain_cards: list[str] = None           # domain_en 缺省按 color_cn 回填的卡

    def __post_init__(self) -> None:
        self.unsupported = [] if self.unsupported is None else self.unsupported
        self.conflicts = [] if self.conflicts is None else self.conflicts
        self.keyword_cards = {} if self.keyword_cards is None else self.keyword_cards
        self.hook_cards = {} if self.hook_cards is None else self.hook_cards
        self.unparsed_text_cards = [] if self.unparsed_text_cards is None else self.unparsed_text_cards
        self.derived_domain_cards = [] if self.derived_domain_cards is None else self.derived_domain_cards


@dataclass(frozen=True)
class CardDb:
    """加载结果：defs=可用注册表；audit=覆盖与冲突审计。"""

    defs: dict[str, CardDefinition]
    audit: CardDbAudit
    version: str


def card_db_version(db_path: str) -> str:
    """卡池内容哈希 + 来源标注（docs/api_contract.md §10：阶段 4 起 card_db_version）。
    只对 loader 消费的语义列（_HASH_COLUMNS）做规范化 row dump 哈希，
    与 DB 文件物理字节无关（异图片/稀有度列变化不漂移版本）。"""
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        cols = ", ".join(_HASH_COLUMNS)
        rows = con.execute(f"SELECT {cols} FROM cards ORDER BY card_key").fetchall()
    finally:
        con.close()
    canon = json.dumps(rows, ensure_ascii=False, separators=(",", ":"), default=str)
    digest = hashlib.sha256(canon.encode("utf-8")).hexdigest()[:12]
    return f"cdb1:{digest}@{CARDDB_SOURCE}"


@functools.lru_cache(maxsize=None)
def load_card_db(db_path: str) -> CardDb:
    """全库加载（lru_cache 以路径为键；1267 行 <<1s）。
    返回 CardDb：defs=可加载卡的 CardDefinition（key=card_key）；不支持的卡只在 audit。"""
    version = card_db_version(db_path)
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(
            "SELECT card_key, name_en, name_cn, type_en, type_cn, super_type,"
            " domain_en, color_cn, energy, rune_power, might, might_bonus,"
            " hero_cn, tags_en, text_en, text_cn FROM cards ORDER BY card_key"
        ).fetchall()
    finally:
        con.close()

    audit = CardDbAudit(total_rows=len(rows))
    defs: dict[str, CardDefinition] = {}
    for r in rows:
        built = _build_definition(r, version, audit)
        if isinstance(built, UnsupportedCard):
            audit.unsupported.append(built)
            continue
        d, derived_domain = built
        defs[d.def_id] = d
        if derived_domain:
            audit.derived_domain_cards.append(d.def_id)
    return CardDb(defs=defs, audit=audit, version=version)


def _build_definition(
    r: sqlite3.Row, version: str, audit: CardDbAudit
) -> tuple[CardDefinition, bool] | UnsupportedCard:
    card_key = r["card_key"]
    type_en, type_cn, super_type = r["type_en"], r["type_cn"], r["super_type"]

    # ---- 类型（R-CR-133/140..179）；schema 外类型 → unsupported ----
    ctype = _TYPE_BY_EN.get(type_en) or _TYPE_BY_CN.get(type_cn or "")
    if ctype is None:
        return UnsupportedCard(card_key, f"无法识别的类型: type_en={type_en!r} type_cn={type_cn!r}")

    # ---- 标签（133.4）：tags_en 站点标签 + hero/signature/token 标记 ----
    tags = {t.strip() for t in (r["tags_en"] or "").split(",") if t.strip()}
    is_hero_unit = super_type == "Champion" or type_cn == "英雄单位"
    if ctype is CardType.UNIT and is_hero_unit:
        tags.add("hero")                       # 103.2.a 选定英雄匹配
    if super_type == "Signature" or (type_cn or "").startswith("专属"):
        tags.add("signature")                  # 103.2.d 专属卡
    if super_type == "Token" or (type_cn or "").startswith("指示物"):
        tags.add("token")                      # R-CR-179/185
    hero_tag = r["hero_cn"] or None

    # ---- 特性（R-CR-134）；混色按列拆分 ----
    domains, derived = _parse_domains(r["domain_en"], r["color_cn"])

    # ---- 费用（206 印刷为准）。混色符能费用无特性列可精确表示 → unsupported ----
    energy = r["energy"]
    cost_energy = int(energy) if energy is not None else 0
    rune_power = r["rune_power"]
    cost_power: tuple[Domain, ...] = ()
    if rune_power:
        if len(domains) != 1:
            return UnsupportedCard(
                card_key,
                f"混色/无色卡的符能费用数 {rune_power} 无特性列可精确归属 (domain_en={r['domain_en']!r})",
            )
        cost_power = tuple([next(iter(domains))] * int(rune_power))

    # ---- 战力 / 战力加成 ----
    might = r["might"]
    might_bonus = _parse_might_bonus(r["might_bonus"])

    # ---- 效果面：cardfx per-card 脚本为唯一事实源（阶段 4 三轮架构转向） ----
    # 运行时不再解析卡面文本；CN/EN 原文作为脚本 review 的依据文档留在 cardfx 注释。
    abilities: tuple = ()
    if ctype is CardType.RUNE:
        abilities = tuple(_BASIC_RUNE_ABILITIES)  # 164.2（基本符文无印刷文本，引擎统一供给）
    keywords: frozenset = frozenset()
    keyword_values: dict = {}

    name = r["name_cn"] or r["name_en"] or card_key
    if ctype is CardType.RUNE and super_type == "Basic" and not domains:
        # 基本符文必须带特性（103.3.a.1）；理论上已由 _parse_domains 回填全部单色
        return UnsupportedCard(card_key, "基本符文缺特性（domain_en/color_cn 均空）")
    d = CardDefinition(
        def_id=card_key, name=name,
        card_types=frozenset({ctype}),
        domains=frozenset(domains),
        cost_energy=cost_energy, cost_power=cost_power,
        might=int(might) if might is not None else None,
        might_bonus=might_bonus,
        tags=frozenset(tags), hero_tag=hero_tag,
        keywords=keywords, keyword_values=keyword_values,
        abilities=abilities, pool=version,
    )
    if ctype is not CardType.RUNE:
        d = _apply_cardfx(d)
        for ab in d.abilities:
            audit.hook_cards.setdefault(ab.kind, []).append(card_key)
        for kw in d.keywords:
            audit.keyword_cards.setdefault(kw.value, []).append(card_key)
    return d, derived


def _parse_domains(domain_en: str | None, color_cn: str | None) -> tuple[set[Domain], bool]:
    """domain_en 优先（逗号拆分）；缺省时 color_cn 单色/混色回填。返回 (domains, 是否回填)。"""
    if domain_en:
        return {_DOMAIN_BY_EN[x.strip()] for x in domain_en.split(",") if x.strip() in _DOMAIN_BY_EN}, False
    if color_cn and color_cn != "无":
        return {
            _DOMAIN_BY_CN_COLOR[x.strip()]
            for x in color_cn.split(",")
            if x.strip() in _DOMAIN_BY_CN_COLOR
        }, True
    return set(), False


def _parse_might_bonus(raw: str | None) -> int | None:
    """'+1'/'+2' → int；None → None。"""
    if raw is None:
        return None
    s = str(raw).strip().lstrip("+")
    return int(s) if s else 0


# NOTE（架构转向）：运行时 CN/EN 文本解析与交叉校验已随 effects.py 退役；
# 效果事实源为 cardfx per-card 脚本。ParseConflict 结构保留供覆盖报告兼容输出（恒空）。
