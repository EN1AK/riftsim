# Stage 3 — Batch 3-FAQ: FAQ/OE 中英文对齐报告

日期：2026-09-21 | 任务：task_3_04（completed）

## 输入

- zh FAQ 326 items（source_001 裁判FAQ 50、005 铸魂官方FAQ 47、006 铸魂裁判FAQ 93、
  007 破限官方FAQ 23、008 破限裁判FAQ 79、011 化神争锋官方FAQ 34）
- en OE 219 items（source_012 Core Rules Patch Notes 84、014 Spiritforged PN 33、
  016 Unleashed PN 56、019 Vendetta PN 46）
- front_matter 59（zh 6 / en 53）

## 文档级关系判定

| zh 文档 | en 文档 | 时代/系列 | 条目级对应 |
|---|---|---|---|
| source_001 裁判FAQ | source_012 Core Rules Patch Notes | 2025-10 v2025 | 无（裁判解释 vs 规则修订公告） |
| source_005 铸魂官方FAQ | source_014 Spiritforged Patch Notes | SFD | 无（卡牌Q&A+内嵌勘误 vs 系统/规则新增） |
| source_007 破限官方FAQ | source_016 Unleashed Patch Notes | UNL | 无（规则编号零交集） |
| source_011 化神争锋官方FAQ | source_019 Vendetta Patch Notes | VEN | 无（规则编号零交集） |
| source_006/008 裁判FAQ | （无） | — | 语料库中无任何对应 |

结论：zh FAQ 与 en Patch Notes 属不同文档类别，无条目级对应关系。

## 候选对审核（全部拒绝）

信号候选 6 条（卡牌名/规则信号，详见 stage3_faq_candidates.json）逐条审核：

1. EV-CN-FAQ-0005/0006/0007/0008 ↔ EV-EN-OE-0059：共例证卡牌"海兽钓钩/Baited Hook"，
   但 en 以其为例讲 null 值澄清，zh 为卡尔玛/先锋之盔交互时序裁决 → 内容不同，不构成对应。
2. EV-CN-FAQ-0316 ↔ EV-EN-OE-0263：en 为 "you may/they may" 时序澄清 + play 定义；
   zh 为拉文布鲁姆学生/攻城锤/鼓舞场景裁决 → 不同。
3. EV-CN-FAQ-0324 ↔ EV-EN-OE-0265：en 为 finalized 检查新规 + 致命伤害澄清（提到 Elder Dragon）；
   zh 为冲突性打出位置要求裁决（远古巨龙例证） → 不同。

规则编号交叉匹配：zh 007/011 rule refs ∩ en 016/019 文本规则号 = 0。

## 结果

- 新增 alignments：0（FAQ/OE 无跨语言对）
- 全部 604 行显式标记 `stage3_alignment`：
  `unmatched_zh` 320 + 审核拒绝 6（zh）、`unmatched_en` 216 + 审核拒绝 3（en）、
  `not_applicable (front_matter)` 59
- needs_review：0；failed：0

## 遗留说明

- zh FAQ 内嵌勘误修订条目（005 的 18 条"修订后"等）已在 Group-B 阶段与 2C 勘误建立
  cross_ref 指针（同语料内关联），不属于跨语言对齐范围。
- 跨语言规则主题相关性由 Stage 4 通过 rule_id_candidate/rule_number 聚类处理。
