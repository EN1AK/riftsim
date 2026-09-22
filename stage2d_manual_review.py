# -*- coding: utf-8 -*-
"""Stage 2D manual_review entries (disciplinary flags, no auto-resolution)."""
import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

con = sqlite3.connect(r"workspace/rules_work.db")
print("existing MR ids:", [r[0] for r in con.execute(
    "SELECT item_id FROM manual_review ORDER BY item_id DESC LIMIT 4")])

ITEMS = [
    ("MR-2D-0001", None,
     "source_001 日期冲突：文件名标注 2025-12-03，文档内文声明『最后更新时间：2025-10-23』。",
     "source_001", None,
     "sources.date=2025-12-03 vs doc internal date=2025-10-23 （均为 inferred）",
     "文件名为发布/归档日期，内文为内容最后更新日期，两者可能都真实",
     "来源日期效力判定需人工决定 effective_date 与 version 采用哪个日期"),
    ("MR-2D-0002", None,
     "source_006 日期冲突：文件名 2026-04-15，文档内文『更新日期：2026/01/14』；且 006 第 37 行存在 "
     "『Q：可以。』排版错误（应为 A：可以。），已由解析器按 typo_fixed 自动归并，需人工确认归并正确。",
     "source_006", None,
     "sources.date=2026-04-15 vs internal=2026-01-14；typo Q/A 标记误用",
     "文件名与内文日期差近 3 个月；typo 修复已附带 notes 标记 typo_fixed",
     "日期取值与 typo 自动修复的正确性需人工复核"),
    ("MR-2D-0003", None,
     "source_008 文档组成声明：前 3 节为 2026-04-16 裁判FAQ 保留部分，后 2 节（4.卡牌文本更新相关 / "
     "5.260511新增卡牌Q&A）为 2026-05-11 新增；文件名日期 2026-05-13、后缀 260511，三者不完全一致。",
     "source_008", None,
     "sources.date=2026-05-13 vs 内容部分日期 2026-04-16/2026-05-11",
     "文档为增量合订本,不同节的有效日期不同",
     "batch 级版本判定需要人工确认各节时间效力"),
    ("MR-2D-0004", None,
     "source_007 金克丝案例：英文卡牌文本中条件分句位置与中文译文不同，FAQ 裁定两种句式在中文下都按"
     "同一含义理解，但提示英文原版存在句式差异。",
     "source_007", "卡牌文本中英对照",
     "英文条件分句可前置/后置；中文译文句式不区分，FAQ 按统一含义执行",
     "中文执行口径由官方 FAQ 统一，英文原文句式差异不影响中文结算",
     "中英卡牌文本差异属跨语言一致性问题，需 Stage 3 reconciliation 处理"),
    ("MR-2D-0005", None,
     "source_008 第 4 节：沙丘亚龙(OGN·131)/金克丝-暴走萝莉(OGN·251)/均衡门徒(UNL·97)/艾翁-万物之友"
     "(UNL·177) 四张卡的中英文本存在语义分歧，文档给出结算链流程分析并声明『中文文本或将在未来作出"
     "更新调整』；沙丘亚龙另有前序勘误注记。",
     "source_008", "source_002/source_003 (2C 勘误)",
     "中文文本当前结算口径 vs 英文文本含义；中文文本未来可能更新",
     "FAQ 先给出现行中文文本的结算方式，未来可能以勘误形式修订中文文本",
     "与未来勘误的衔接和现行口径固化需人工在 Stage 3 裁决"),
    ("MR-2D-0006", None,
     "source_011 明示废弃 source_005 答复：阿克尚偷眼镜条目声明『铸魂淬炼常见问题解答中的相关答复"
     "已不再适用』（涉及斯弗尔尚歌+厄斐琉斯相关答复）。",
     "source_011", "source_005",
     "005 斯弗尔尚歌/厄斐琉斯答复 vs 011 阿克尚新答复",
     "官方 FAQ 后续版本取代先前答复，011 为准",
     "FAQ 间取代关系需人工确认并将 005 被废弃条目在 Stage 3 标记失效"),
    ("MR-2D-0007", "735.1.c",
     "source_005『规则 735.1.c（修订后）』：FAQ 以（修订后）形式直接给出核心规则 735.1.c 的新文本，"
     "已按 rule_change_candidate 提取；同时与 Stage 2C 勘误范围可能交叉。",
     "source_005", "核心规则 735.1.c / Stage 2C evidence",
     "FAQ 直接修订核心规则条文（非卡牌文本），且声明立即生效",
     "FAQ 作为官方规则说明可临时修订核心规则；2C 勘误未含规则条文只含卡牌",
     "规则条文级修订需与 Stage 1 规则文本比对后由 Stage 3 落地，禁止本阶段直接改规则"),
    ("MR-2D-0008", None,
     "FAQ 内嵌勘误提及：source_005 多个（修订后）卡牌文本块、source_008 永恩回答内嵌『勘误后文本』、"
     "source_011 星界灵鹭条目『已受到勘误，技能描述更新为』——均与 Stage 2C 勘误 evidence 交叉。",
     "source_005/source_008/source_011", "Stage 2C evidence (EV-CN-ER/EV-EN-ER)",
     "FAQ 文本中复述/引用勘误内容，2C 已正式抽取勘误条目",
     "FAQ 内嵌勘误仅作交叉引用（notes 已标 mentions_errata），不重复建勘误条目",
     "需人工核对 FAQ 复述文本与 2C 勘误文本逐字一致性"),
    ("MR-2D-0009", None,
     "FAQ 效力优先声明：source_007『如果本文档与《核心规则》有任何不一致之处，请以本文档为准。当下一"
     "次核心规则更新发布时，本文档将会失效』；source_011『新版《核心规则》发布后以新版为准』；"
     "source_005『这些阐明与勘误将立即生效』。",
     "source_007/source_011/source_005", "Stage 1 核心规则文本",
     "FAQ 自声明高于核心规则的临时效力及失效条件",
     "FAQ 具有过渡性最高效力，核心规则更新后被吸收或失效",
     "效力层级与失效时点需纳入 Stage 3 规则版本管理，不能自动推导"),
    ("MR-2D-0010", None,
     "source_012 前言声明：『A very small amount of that information is explicitly contradicted "
     "in these notes』——Core Rules Patch Notes 与先前 Origins FAQ 存在少量明确矛盾，以 Patch Notes 为准。",
     "source_012", "Origins FAQ (先前官方说明)",
     "Patch Notes 自述与先前 FAQ 少量矛盾",
     "官方以后发 Patch Notes 取代先前 FAQ 中过时的说明",
     "被取代的先前 FAQ 条目需 Stage 3 逐条识别并标记失效"),
    ("MR-2D-0011", None,
     "生效日期冲突（EN Patch Notes）：source_014 内文声明 effective date 2025-12-12 vs sources.date "
     "2025-12-05；source_019 声明 effective 2026-07-24 vs sources.date 2026-07-17；source_016 byline "
     "日期 3/31/2026 vs 文件名 2026-03-30。",
     "source_014/source_016/source_019", None,
     "发布日期(byline/文件名) vs 声明生效日期(effective date) 不一致",
     "先发博客后生效是官方惯例；sources 表的 effective_date 应以声明生效日为准",
     "日期字段采用规则需人工确认（date=publish, effective_date=声明日）"),
    ("MR-2D-0012", None,
     "source_019 多处声明 Unleashed FAQ 的阐明已并入核心规则文档（Lethal damage/your damage/"
     "Battlefield Ability Control/Counting Targets/accelerate/Trigger Condition 等），『all of the "
     "changes described in the Unleashed FAQ have been reproduced in the Core Rules Document』。",
     "source_019", "source_016 (Unleashed Patch Notes) / 核心规则",
     "019 声明 016 的 FAQ 阐明已被核心规则吸收",
     "官方在新版本发布时将旧 FAQ 内容并入核心规则文档",
     "reconciliation 需识别已并入核心规则的 FAQ 条目避免重复计数"),
    ("MR-2D-0013", None,
     "裁判FAQ 效力声明：source_001/006/008 均声明『可以作为裁判判罚的依据，但不代表官方FAQ』，与官方"
     "FAQ（005/007/011）法律效力层级不同。",
     "source_001/source_006/source_008", "source_005/source_007/source_011",
     "裁判FAQ 自述非官方 FAQ，但可作判罚依据",
     "裁判FAQ 为裁判社区整理，效力低于官方 FAQ",
     "冲突时效力排序（官方FAQ > 裁判FAQ）需 Stage 3 人工确认"),
    ("MR-2D-0014", None,
     "source_008 第 5 节部分 Q&A 无 Q/A 标记（裸问句+裸答），以及 006/008 存在问句跨行/跨页断裂，"
     "解析器按段落启发式（unmarked_qa / fracture 合并）处理，共 4 条标记 needs_review=true。",
     "source_008/source_006", None,
     "无标记问答与断行问句的条目边界由启发式确定",
     "启发式依据问句标点与行尾闭合性，人工抽查结果正确",
     "结构置信度问题需人工复核 4 条 needs_review 条目（EV 编号见 notes）"),
    ("MR-2D-0015", None,
     "source_007 散文小节的分类为启发式：prose_section（规则修订与阐明）默认 rule_interpretation，"
     "含（旧）/（新）对照的标记 rule_change_candidate；散文条目并非问答形式，faq_question 为小节标题。",
     "source_007", None,
     "prose 条目不是 Q&A 结构，六分类映射为近似值",
     "官方 FAQ 前半部分为规则修订说明文，本身即规则阐明",
     "条目形态与分类口径需人工在 Stage 3 复核"),
]

for row in ITEMS:
    con.execute(
        "INSERT OR REPLACE INTO manual_review (item_id, rule_id, issue_description, source_a,"
        " source_b, conflicting_points, possible_explanation, cannot_auto_resolve_reason)"
        " VALUES (?,?,?,?,?,?,?,?)", row)
con.commit()
n = con.execute("SELECT COUNT(*) FROM manual_review WHERE item_id LIKE 'MR-2D-%'").fetchone()[0]
print(f"MR-2D rows: {n}")
con.close()
