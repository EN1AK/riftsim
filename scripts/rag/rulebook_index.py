# -*- coding: utf-8 -*-
"""规则书章节索引（静态数据，版本化管理）。

来源：workspace/final/rules.db 中 R-CR-* 的 rule_id 章号分布与 topic。
用途：
- CATEGORIES：大类书目，常驻 planner 系统提示（静态书目）。
- KEYWORD_CHAPTERS：800-829 关键词词条章节明细，供分类器 few-shot 与提示注入。
- ALIASES_CN：已知中文词条别名（随数据管线核对后扩充）。
"""
from __future__ import annotations

# (章号范围, 中文主题说明) —— 常驻 planner 提示的静态书目
CATEGORIES = [
    ("000-056", "黄金/白银规则：卡牌与规则冲突、规则禁行"),
    ("100-206", "卡牌要素、费用、域/传奇、战场与胜负条件"),
    ("303-318", "回合阶段、步骤、优先权与专注"),
    ("319-324", "移动完成时点、单位死亡与状态记录"),
    ("325-348", "结算链与 Showdown：立项→执行→传递→结算四步"),
    ("349-359", "打牌流程、目标选择、效果拆分"),
    ("360-375", "能力体系：被动能力、替代效果"),
    ("376-381", "启动式能力"),
    ("382-388", "触发式能力：触发时机、待处理、加入结算链、同时触发排序（383 正文最多）"),
    ("389-401", "延时能力、牵涉能力、开牌"),
    ("402-406", "出牌五步过程：选法/费用/支付/合法性检查/执行"),
    ("407-458", "游戏动作词典：抽413/横414/重置415/回收416/打出419/移动420/藏匿421/弃422/晕423/展示424/反制425/增益426/放逐427/击杀428/添加429/导能430/燃尽431等"),
    ("459-466", "战斗与战斗伤害判定步骤"),
    ("467-472", "计分与获胜"),
    ("473-480", "持续效果叠加层（哪个先算）"),
    ("481-489", "玩法模式；649-652 认输"),
    ("700-799", "Buff/加成伤害/附着/依赖关键词/XP/计数器/不可选为目标等附加规则"),
    ("800-829", "关键词词条各一章（明细见 KEYWORD_CHAPTERS，如 808 绝念、813 反应、829 流转）"),
]

# 800-829 关键词词条章节明细（英文 topic 自 rules.db，中文别名经卡片文本核对后补充）
KEYWORD_CHAPTERS = {
    "801": "Keywords", "802": "Keyword", "804": "Keyword Glossary",
    "805": "Accelerate", "806": "Action", "807": "Assault",
    "808": "Deathknell", "809": "Deflect", "810": "Ganking",
    "811": "Hidden", "812": "Legion", "813": "Reaction",
    "814": "Shield", "815": "Tank", "816": "Temporary",
    "817": "Vision", "818": "Equip", "819": "Quick-Draw",
    "820": "Repeat", "821": "Weaponmaster", "822": "Ambush",
    "823": "Hunt", "824": "Level", "825": "Unique",
    "826": "Backline", "827": "Empower", "828": "Empowered",
    "829": "Flow",
}

# 已知中文词条别名（仅在语料中实际出现过才登记，避免错译）
ALIASES_CN = {
    "808": "绝念",
    "813": "反应",
    "829": "流转",
}


def render_categories() -> str:
    """静态书目文本（planner 系统提示长驻）"""
    return "\n".join("- %s：%s" % (rng, desc) for rng, desc in CATEGORIES)


def render_keywords() -> str:
    """关键词章节一览（分类器 few-shot 用）"""
    items = []
    for chap, name in sorted(KEYWORD_CHAPTERS.items()):
        alias = ALIASES_CN.get(chap)
        items.append("%s %s%s" % (chap, name, ("（%s）" % alias) if alias else ""))
    return "、".join(items)


def describe_chapters(chapters: list[str]) -> str:
    """把分类器返回的章号渲染成提示行（含中文说明）"""
    desc_map = {rng: desc for rng, desc in CATEGORIES}
    parts = []
    for chap in chapters:
        label = None
        if chap in KEYWORD_CHAPTERS:
            alias = ALIASES_CN.get(chap)
            label = "关键词 %s%s" % (
                KEYWORD_CHAPTERS[chap], ("（%s）" % alias) if alias else "")
        else:
            for rng, desc in CATEGORIES:
                start, _, end = rng.partition("-")
                if start.isdigit() and end.isdigit() and int(start) <= int(chap) <= int(end):
                    label = "%s：%s" % (rng, desc)
                    break
        parts.append("R-CR-%s.x（%s）" % (chap, label or "未标注"))
    return "、".join(parts)


def is_valid_chapter(chap: str) -> bool:
    """章号合法性：三位数字无限定（数据源自规则书编号空间）"""
    return chap.isdigit() and len(chap) == 3
