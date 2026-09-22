# Stage 3 — 总结报告（Entity Resolution + 中英文 Alignment）

日期：2026-09-21 | 状态：completed（task_3_01..05 全部 completed）

## 批次与成果

| 批次 | 任务 | 成果 |
|---|---|---|
| 3-ENT | task_3_01 | 卡牌实体解析：evidence 挂载 card_id（481 行 entity 注记） |
| 3-CR | task_3_02 | 核心规则对齐 2382 对（AL-CR）：equivalent 2221 / translation_difference 161 → MR-3-CR-0001..0161（转 Stage 4/5 处理） |
| 3-ER | task_3_03 | 勘误对齐 63 对（AL-ER，全部 equivalent/high）；30 条 zh-only 显式标记；3 EN front_matter N/A；报告 stage3_er_alignment.md |
| 3-FAQ | task_3_04 | FAQ/OE 对齐：0 对（6 信号候选审核全拒）；604 行全部显式标记 unmatched/NA；文档级关系存档；报告 stage3_faq_alignment.md |
| 收尾 | task_3_05 | MR-2D-0004/0005/0010 结案；全量验证通过 |

## 关键发现（移交 Stage 4）

1. **核心规则**：EN/CN 同版本已确认（rule_number 序列一致）；161 对 translation_diff
   （多为排版/括号标记差异）已逐对记入 manual_review，Stage 4B 可批量按模板差处理。
2. **勘误**：zh 勘误含 30 条 zh-only（28 翻译修正 + 2 文案润色）；
   EV-CN-ER-0093（VEN-079）修正了 mistranslated 目标限制——**改变 zh 实际卡面效果**，
   Stage 4 须采用修正后文本；EN 侧无需勘误。
3. **FAQ/OE**：zh FAQ 与 en Patch Notes 无条目级对应；跨语言规则主题相关性由
   rule_id_candidate/rule_number 在 Stage 4 聚类承载。
4. **模板差异（MR-2D-0004）**：中文译文不区分英文触发式技能条件分句的前置/后置模板，
   官方 FAQ 裁定同义执行；此类差异不计语义差异。
5. **观察项（MR-2D-0005）**：沙丘亚龙/金克丝-暴走萝莉/均衡门徒/艾翁四卡
   pending_zh_text_update，现行口径以 source_008 第 4 节为准，待后续中文勘误。
6. **效力拓扑（MR-2D-0010）**：EN Core Rules Patch Notes(2025-10-24) > 先前 Origins
   官方 FAQ（外部文档，不在语料库）；012 的 CLARIFIED/NEW RULE 为权威侧，交 Stage 4B。

## 验证结果

- rule_evidence_unpaired = 0（4764 核心规则行全部入对）
- errata_unresolved = 0（159 行：126 入对 / 33 显式标记）
- faq_oe_untagged = 0（604 行全部标记）
- alignments 重复对 = 0；任务 pending/running/failed = 0

## Stage 3 总量

- alignments：2445（AL-CR 2382 + AL-ER 63）
- manual_review 高位：MR-3-CR 161 条（translation_difference 复核项，交 Stage 4/5）
- Stage 2 遗留 3 MR 全部结案
