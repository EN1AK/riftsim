# Stage 3 — Batch 3-ER: 中英文勘误对齐报告

日期：2026-09-21 | 任务：task_3_03（completed）

## 输入

- zh 勘误 93 条（source_002/003/004/010）+ 0 front_matter
- en 勘误 63 条（source_013/015/017/020）+ 3 front_matter（EN 站点导出抬头，无 zh 对应）

## 方法

1. 机械配对：`stage3_er_pair.py`（card_ids 首键）→ 66 候选对、27 zh 未配对、2 en 未配对。
2. 人工/模型裁决：按卡牌族文档映射（zh002↔en013 Origins、zh003↔en017 Unleashed、
   zh004↔en015 Spiritforged、zh010↔en020 Vendetta）+ card_ids 交集重新配对，
   对 66 候选逐一核对 NEW/OLD 文本块（全部过眼部语义等价）。
3. 特殊裁决：
   - EV-CN-ER-0023 ↔ EV-EN-ER-0024（提莫）：zh card_ids 首键 FND-196 导致首漏配；
     FND-196 为 zh 基石系列的同一卡牌印本（card_ids 含 OGN-121）。
   - EV-CN-ER-0028 ↔ EV-EN-ER-0029（疾风剑豪）：FND-259 = OGN-259 同卡不同印本。
   - EV-CN-ER-0048/0051/0055（zh003 terminology_fix）与 0081/0082/0084（zh010）撞车：
     前者为 zh-only 翻译修正（已标记 zh_only_translation），后者才对应 EN source_020 功能勘误。
   - EV-CN-ER-0090/0092（zh010 terminology_fix）：对 UNL-186/OGN-289 的 zh 文案润色，
     功能勘误已由 0034↔EV-EN-ER-0052、0022↔EV-EN-ER-0023 承载，记为 zh-only 未配对。

## 结果

- 对齐 63 对：AL-ER-0001..0063，relation=equivalent，confidence=high
  （version_relation 注明 zh/en 发布日期差，如 zh002 2025-12-03 vs en013 2025-10-21）。
- 未配对 zh 30 条，全部显式标记 `stage3_alignment: unmatched (zh_only_translation)`：
  - 21 条已按 MR-2C-0004 裁定标记（source_003 翻译勘误 19 + source_004 2）。
  - EV-CN-ER-0059..0062 新确认 zh_only_translation（OGN-002/048/146/207，
    中文卡牌勘误仅改写译文，扩展 MR-2C-0004 裁定）。
  - EV-CN-ER-0089/0091 source_010 措辞润色（时间扭曲、忠诚的猎犬）。
  - EV-CN-ER-0090/0092 zh 文案润色（见上）。
  - EV-CN-ER-0093（VEN-079 夺魂钩妲姆）：**纠正 mistranslated 目标限制**
    （旧 zh "战力大于我的单位" → 新 zh "一名单位"，与 EN 原文一致；EN 无需勘误；
    该条改变 zh 实际卡面效果，Stage 4 须采用修正后文本）。
- 未配对 en：0（EV-EN-ER-0024/0029 已配回 zh002）。
- front_matter：3 条 EN 标记 `stage3_alignment: not_applicable`。

## 统计

- candidate pairs reviewed: 66 → accepted 63 / rejected 5（重复发布错配）
- aligned: 63 | zh_only unmatched: 30 | en unmatched: 0 | failed: 0 | needs_review: 0

## 遗留

- mod_type 启发式差异（partial_replacement vs condition_change 等）共 11 对，
  NEW 文本已核对等价，差异仅来自启发式分类器；对齐不受影响（详见 alignments.notes）。
