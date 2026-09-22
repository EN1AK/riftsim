# Stage 4A — Rule Clustering 报告（2026-09-21）

任务：把全部 Evidence 映射到稳定 Rule ID（不做 canonical rule 裁决，留给 Stage 4B）。

## 聚类方案

| 簇类型 | rule_id 形式 | 依据 |
|---|---|---|
| 核心规则 | `R-CR-<rule_number>` | AL-CR 对齐对（zh+en 同版本合并，不因双语拆两个 Rule） |
| 核心规则前言 | `R-CR-FRONT` | EV-CN-CR-0000 / EV-EN-CR-0000 |
| 卡牌簇 | `R-CARD-<card_key>` | errata target + FAQ 卡牌实体（Stage 3 entity resolution） |
| Errata 前言 | `R-ER-FRONT` | 3 条 errata 文档头 |
| FAQ 前言 | `R-FAQ-FRONT` | 10 条 faq/oe 文档头 |
| 主题簇 | `R-TOPIC-CN-XX` / `R-TOPIC-EN-XX` | 仅按 topic 可聚的 FAQ/OE（无卡、无显式规则引用） |
| 兜底簇 | `R-MISC-<source_id>` | 无 topic/卡/引用的 FAQ/OE 行（4B 需人工归题） |

FAQ/OE 挂载优先级：显式规则编号引用 > 卡牌实体 > topic 簇 > misc 兜底。

## 结果统计

- rules（簇）: **2984**
  - R-CR: 2381（规则号簇；另有 R-CR-FRONT）
  - R-CARD: 514（errata 130 + 仅见于 FAQ 的 384）
  - R-TOPIC-CN: 17 / R-TOPIC-EN: 64
  - R-FRONT: 2（R-ER-FRONT, R-FAQ-FRONT；R-CR-FRONT 计入 R-CR 桶）
  - R-MISC: 5
- rule_evidence 链接: **6352**
  - same（核心规则 zh/en 双挂）: 4764
  - replacement（errata -> 卡簇）: 222
  - faq:* : 1353（rule_interpretation 680 / example_only 512 / rule_change_candidate 134 / exception 27）
  - front_matter: 13
- Evidence 覆盖: 5527 / 5527，unmapped = 0
- 预创建后无成员的空主题簇 25 个已清除；重复链接 0；无 evidence 的 rule 0

## rule_evidence.relationship 约定（供 4B 使用）

- `same`：核心规则 zh 与 en 文本（同版本确认；161 对 translation_difference 在 notes 标记见 MR-3-CR）
- `replacement`：errata 指向卡簇（modification_type 为启发式，写入 notes；范围裁决在 4B）
- `faq:<classification>`：保留 Stage 2D 分类原值，4B 再判 supplement/clarification/exception/change
- `front_matter`：文档头

## 新增 manual_review（MR-4A-0001..0006）

6 条 FAQ 显式引用了当前 2026-07 核心规则中不存在的规则编号
（376.3 / 335.3 / 460.2 / 322.2 / 322.3 / 322.8 / 735.1），疑似旧版编号。
已知先例：FAQ 735.1.c 已并入现行规则 809.1.c（MR-2D-0007）。→ Stage 4B 映射到后继规则或记为历史引用。

### 2026-09-21 裁决（保持 OPEN，4B 终核）

- MR-4A-0001: 376.3.b.1 → 383.3.d / 383.3.d.1（多触发按回合顺序放置；战斗防守方细则见 383.4.f + 466.x）
- MR-4A-0002: 322.2/322.3 → 318 清理步骤序列（特殊清理见 324 + 466.1.a）
- MR-4A-0003: 322.2/322.3/322.8 → 318 + 324 + 466；旧 440.1.x → 466.1.a（现行 440.x 已重用为燃烧规则）
- MR-4A-0004: 735.1.c → 809.1.c（文本逐字对应，完全确认）
- MR-4A-0005: 460.2.c.3 → 465.2.c.4(+465.2.c.4.a)；323.5 现行存在且内容一致，无需重映射（已修正）
- MR-4A-0006: 335.3 → 334 HOT FEPR 主规则（+335–336）

## 附审：explicit-ref 链接风险标记

45 条 FAQ→R-CR 显式编号链接中，23 条来自重编号前的 judge 来源
（source_001 x5 / source_007 x18）已在 rule_evidence.notes 打 'VERIFICATION FLAG 4B'：
编号命中不代表目标规则正确（现行编号可能已重用为不同规则）。
source_011 的 22 条引用经抽查与现行编号一致，未标记。

## 交接给 Stage 4B 的标记

- 161 对 translation_difference 核心规则（MR-3-CR-0001..0161，rule_evidence.notes 已标）
- 134 条 rule_change_candidate FAQ（仅提取标记，是否改规则由 4B 裁决）
- EV-CN-ER-0093（VEN-079 corrected mistranslation）: 4B 使用修正后中文文本
- R-TOPIC / R-MISC 簇为 4A 分组桶：4B 需将其中 FAQ 内容归并到具体 R-CR / R-CARD 规则
- source_012 Patch Notes 效力交接（MR-2D-0010）在 4B 处理

## 执行脚本

- `stage4a_cluster.py`（主聚类，按簇原子提交）
- `stage4a_fix.py`（清空簇清除 + MR-4A 录入 + 终验）
- tasks: task_4a_01..04 completed
