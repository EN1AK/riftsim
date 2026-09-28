# 阶段 0 交付 1：来源清单与效力认定（Source Inventory）

> 生成：2026-09-28，阶段 0 输入审计。数据均实查自 `workspace/rules_work.db`（事实来源）、
> `workspace/final/rules.db`、`cards_bilingual.db`、`workspace/source_manifest.json`、
> `workspace/README_STATE.md`、`workspace/final/coverage_report.md`。审计脚本为 `.tmp/` 下临时探针。

## 1. 结论摘要

- 规则知识库管线 **COMPLETE（2026-09-22）**：20/20 来源处理完毕，evidence 5527/5527 已映射，
  规则 2984/2984 reconciled，冲突 1/1 已裁决，manual_review 186/186 正式关闭，
  覆盖检查 13/13 PASS，终态一致性 24/24 PASS（可随时用 `scripts/stage6/stage6f_final_consistency.py` 复核）。
- **已统一去重**：5527 条 evidence 聚类为 2984 条规则（R-CR 2382 / R-CARD 514 / R-TOPIC 81 / R-MISC 5 / 前言 2）。
- **全部带来源锚点**：`rule_sources` 6353 行，可回查 evidence_id → source_document → 页码/章节/规则号。
- **无未解决冲突**：唯一冲突 CON-4B-T2-0001（R-CR-811.1.b 中文漏译持续时段从句）已按"同版本英文优先"
  裁决并补入 canonical（CHG-5-0001）。全库 `derived_interpretation = 0`（无任何模型推导结论）。
- 规则版本已确认唯一：**2026-07 核心规则**（中 2026-07-17 / 英 2026-07-16，编号序列 2381 条完全一致，
  为同一版本），叠加 2026-07-24 生效的 Vendetta 官方改动（source_019，已应用 37 条 + 1 条 incorporated 记录）。

## 2. 权威规则材料清单（20 份原始 PDF）

规则效力拓扑（2026-09-20 Group C 裁定，MR-2D-0009/0013）：
**现行核心规则 > 过渡性官方 FAQ/Patch Notes（至下一版核心规则发布）> 后发布 FAQ 取代先发布 > 裁判 FAQ（社区层级）**；
同级同版本冲突时英文官方文本优先于中文译文（实例：R-CR-811.1.b）；Errata 只修改其明确覆盖的范围。

| source_id | 文件（路径） | 类型 | 语言 | 版本/日期 | 生效层级 | 状态 |
|---|---|---|---|---|---|---|
| source_009 | `loltcg_pdfs/09_2026-07-23_6f47b6...pdf` | 核心规则 | zh | 文档自称更新于 2026-07-17（confirmed） | **canonical 基准**（中文官方文本为规范） | 已处理，2382 evidence，125/125 页 |
| source_018 | `riftbound_en_rules/07_2026-07-16_Core_Rules.pdf` | 核心规则 | en | 文档自称 Last Updated 2026-07-16（confirmed） | 同版本官方参照；冲突时优先 | 已处理，2382 evidence，120/120 页 |
| source_019 | `riftbound_en_rules/08_2026-07-17_Vendetta_Patch_Notes.pdf` | 官方解释/规则改动 | en | 2026-07-17，生效 2026-07-24（declared） | **core 之后的官方改动，已应用**（37 条 CHG-4B-T3 + 1 incorporated） | 已处理，62 items |
| source_020 | `riftbound_en_rules/09_2026-07-23_Vendetta_Errata.pdf` | 勘误 | en | 2026-07-23（inferred） | 卡牌勘误（EN 记录） | 已处理，8 rows |
| source_010 | `loltcg_pdfs/10_2026-07-24_9fe1f1...pdf` | 勘误 | zh | 2026-07-24（inferred） | 卡牌勘误（zh，canonical 依据） | 已处理，13 rows |
| source_002 | `loltcg_pdfs/02_2025-12-03_符文战场_勘误汇总_1028.pdf` | 勘误 | zh | 2025-12-03 | 卡牌勘误 | 已处理，31 rows |
| source_003 | `loltcg_pdfs/03_2026-04-15_破限系列_勘误汇总_260403.pdf` | 勘误 | zh | 2026-04-15 | 卡牌勘误（19 条为纯翻译修正 zh_only） | 已处理，31 rows |
| source_004 | `loltcg_pdfs/04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` | 勘误 | zh | 2026-04-15 | 卡牌勘误 | 已处理，18 rows |
| source_013 | `riftbound_en_rules/02_2025-10-28_Origins_Errata.pdf` | 勘误 | en | doc 内日期 2025-10-21（declared） | 卡牌勘误（EN 记录） | 已处理，31 rows + 前言 |
| source_015 | `riftbound_en_rules/04_2026-01-14_Spiritforged_Errata.pdf` | 勘误 | en | 2026-01-14 | 卡牌勘误 | 已处理，16 rows |
| source_017 | `riftbound_en_rules/06_2026-04-03_Unleashed_Errata.pdf` | 勘误 | en | 2026-04-03 | 卡牌勘误 | 已处理，8 rows + 前言 |
| source_005 | `loltcg_pdfs/05_2026-04-15_铸魂淬炼系列_官方FAQ_260114.pdf` | 官方 FAQ | zh | 2026-04-15 | 官方解释；两条目（0089/0090）已被 source_008 0307 **取代**（保留链接不作现行） | 已处理，47 items |
| source_007 | `loltcg_pdfs/07_2026-04-30_破限系列_官方FAQ.pdf` | 官方 FAQ | zh | 2026-04-30 | 官方解释（6 条 RCC 已并入 2026-07 核心规则，CHG-4B-T1F） | 已处理，23 items |
| source_011 | `loltcg_pdfs/11_2026-08-13_612b1c...pdf` | 官方 FAQ | zh | 2026-08-13 | 官方解释（最新中文 FAQ） | 已处理，34 items |
| source_012 | `riftbound_en_rules/01_2025-10-24_Core_Rules_Patch_Notes.pdf` | 官方解释（Patch） | en | 2025-10-24 | **过渡性，已被 2026-07 核心取代，未应用**（仅记录） | 已处理，86 items |
| source_014 | `riftbound_en_rules/03_2025-12-05_Spiritforged_Patch_Notes.pdf` | 官方解释（Patch） | en | 生效 2025-12-12（declared） | 同上，过渡性未应用 | 已处理，45 items |
| source_016 | `riftbound_en_rules/05_2026-03-30_Unleashed_Patch_Notes.pdf` | 官方解释（Patch） | en | 生效 2026-03-31（declared） | 同上，过渡性未应用 | 已处理，75 items |
| source_001 | `loltcg_pdfs/01_2025-12-03_裁判FAQ_251023.pdf` | 裁判 FAQ | zh | doc 内 2025-10-23（declared） | **裁判社区层级**（低于官方 FAQ），挂载已标注 | 已处理，50 items |
| source_006 | `loltcg_pdfs/06_2026-04-15_铸魂淬炼系列_裁判FAQ.pdf` | 裁判 FAQ | zh | 2026-04-15 | 裁判社区层级 | 已处理，93 items |
| source_008 | `loltcg_pdfs/08_2026-05-13_破限系列_裁判FAQ_260511.pdf` | 裁判 FAQ | zh | doc 内 2026-05-11（declared） | 裁判社区层级；sec.4 为 4 张观察卡**现行口径** | 已处理，79 items |

派生中间产物：`extracted/*.txt`（PDF 抽取文本，非权威，仅供回查）；`kb/core_rules_{cn,en}.json`
（早期预处理产物，**非权威**，以 evidence 表为准）。

## 3. 统一规则知识库（引擎的直接规则输入）

| 产物 | 路径 | 内容 | 用途定位 |
|---|---|---|---|
| **rules_work.db** | `workspace/rules_work.db` | 事实来源：sources 20 / evidence 5527 / alignments 2445 / rules 2984 / rule_evidence 6353 / reconciliations 2996 / changes 267 / conflicts 1(resolved) / verification 393 / manual_review 186(closed) | 阶段 1 规则规格的主要提取源 |
| **rules.db** | `workspace/final/rules.db` | 查询版：rules 2984 + rule_sources 6353 + rule_cards 7046（688 张不同卡）+ rule_keywords 885（启发式）+ rule_changes 267 + rule_verification 393 + rules_fts（FTS5） | 引擎规则查询/规则 ID 关联 |
| rules.md | `workspace/final/rules.md`（~3.0 MB） | 2984 条的人类可读版；每条含规范规则/官方解释/案例/例外/来源/状态 | 人工核对 |
| change_log.md | `workspace/final/change_log.md` | 267 条变更（勘误应用 222 / FAQ 内嵌 6 / post-core 官方改动 38 / 验证修复 1） | 版本差异、卡牌现行文本追溯 |
| manual_review.md | `workspace/final/manual_review.md` | 186 条复核，全部关闭，含裁定结论 | 歧义判例库（阶段 1 设计参考） |
| coverage_report.md | `workspace/final/coverage_report.md` | 13/13 强制检查 PASS | 覆盖证明 |

规则条结构（rules 表）：`rule_id, topic, proposed_canonical_rule（规范正文）, exception,
official_interpretation, example, status, verification_status`。rules.md/DB 一致，6F 复核通过。

**已知数据形态（直接影响阶段 1 方法）**：

- 结构化语义五字段（applicable_object/trigger/precondition/effect/restriction）**全量为 NULL（设计如此，
  管线只做结构抽取）** → 阶段 1 的原子规则规格必须从 canonical 自然语言正文提取语义，
  并用 rule_id 保持可追溯；不能依赖现成结构化字段。
- 472 条 R-CARD 为 FAQ 挂载型记录（canonical NULL，by design），其卡面文本不来自规则库。
- `rule_keywords` 为括号记号启发式（含费用符号/碎片化误抽，如"进行X"），**只能作提示**，
  权威关键字以核心规则 800 章词条（805–829 共 25 条）为准。
- FTS5 可用但为 unicode61 默认分词，中文整词检索不可靠（英文术语正常）。

## 4. 卡牌数据库（非规则权威）

| 产物 | 路径 | 内容 | 效力定位 |
|---|---|---|---|
| cards_bilingual.db | 仓库根目录 | `cards` 1267 行；系列 OGN 364 / SFD 312 / UNL 300 / VEN 253 / OGS 24 / ARC 6 / FND 5 / SGN 3；类型 Unit 629 / Spell 233 / Legend 127 / Gear 114 / Battlefield 66 / Rune 18 / NULL 80；text_en 1168 / text_cn 1182 / errata_cn 99 | **卡牌实体与基础字段来源**（卡号、名称、类型、领域、费用、战力、文本）；**不作为规则权威**（spec 12.4） |
| cards_en/cards.db | `cards_en/` | 1189 行官网抓取 | 合并源（审计用） |
| cards_cn/cards.db | `cards_cn/` | 1261 行官网抓取 + dicts 25 | 合并源（审计用） |

卡牌文本效力链：**已应用勘误的 canonical（KB，zh 最新勘误 corrected_fragment）> 卡库原始文本**。
已证实卡库字段不足：130 条勘误卡中 31 条在卡库无勘误后文本（4B-B004 实测）；EN 勘误 85 条仅记录未改
zh canonical（实现英文卡面时需从 EN errata 另行叠加，或引擎以 zh canonical 为单一文本源）。
类型 NULL 的 80 行（多为 Token/特殊）需在阶段 1 界定卡定义 schema 时处理。

## 5. 冲突、未决与观察项

- **冲突**：1/1 已裁决（CON-4B-T2-0001 → resolved_stage5 / CHG-5-0001）。无未决冲突。
- **人工复核**：186/186 正式关闭。
- **观察卡 4 张（非阻断）**：OGN-131 / OGN-251 / UNL-097 / UNL-177 —— zh 牌面待官方更新，
  现行口径按 source_008 sec.4；watch 记录在 REC-4B-T3 notes。实现这 4 张卡时必须按该口径并标注。
- **文档级警告（非阻断）**：EV-CN-FAQ-0260 未链接 R-CARD-OGN-251。
- **被取代条目（不作现行）**：EV-CN-FAQ-0089/0090（superseded_by 0307，链接保留仅审计）。
- **过渡性 pre-core 官方改动 90 条**（source_012/014/016）：未应用、仅记录；不得作为现行规则输入。

## 6. 已有代码与运行环境

| 代码 | 路径 | 与模拟器的关系 |
|---|---|---|
| 管线脚本 | `scripts/ingest, cards, stage2-6, rulings, debug` | 仅规则库生产/审计；模拟器不依赖（产物已冻结） |
| RAG 问答服务 | `scripts/rag/`（rag_server, agent_loop, rag_query, card_resolver, rulebook_index + tests） | 规则 QA 工具，非模拟器组件；`card_resolver.py` 的卡名→card_id 解析可在阶段 1/4 的工具链复用 |
| openspec 能力规格 | `openspec/changes/add-riftbound-rules-agent-mode/` | 仅描述 RAG 服务契约，与引擎无关 |
| 模拟器/训练/UI | — | **不存在**，本工程从阶段 2 开始新建 |
| 环境 | Python 3.12.10（系统），`.venv` 已存在（RAG 用：torch/sentence-transformers/openai），`.pylibs` 内置 PyMuPDF 1.28.2，pytest 9.1.1 可用（系统解释器与 `.tmp/wheels` 离线包） | 阶段 3 TDD 可直接用 pytest；引擎本体应保持零重依赖（不建议在热路径引入 RAG 的 torch） |

其他：当前工作区**未初始化 git 仓库**（无 `.git`），规则库 pipeline 以文件 checkpoint 留痕；
建议模拟器代码建立独立版本控制或纳入统一仓库管理（阶段 2 决定）。`.gitignore` 已排除
`.venv/`、`workspace/rag/`、`__pycache__`。

## 7. 缺失项（不阻塞规则引擎设计，单列跟踪）

1. **官方卡组/预组牌表缺失**：仓库只有完整卡池，无任何官方 decklist。MVP 自动对局需按
   101–103 组卡规则自行构建合法卡组（或后续补充官方预组数据）。
2. **结构化语义缺失**（见 §3）：触发/效果等字段须阶段 1 从 canonical 文本规格化提取。
3. **中文卡名分词/FTS 检索弱**：引擎内部一律用 `card_id`/`rule_id` 关联，不依赖中文全文匹配。
4. **N 牌（type NULL 80 行）与衍生 Token 的游戏内属性**需以 core rules 179–187（Tokens）为准生成，
   卡库 token 行仅作参考。
5. rules.md 与 rules.db 内容等价但 rules.db 是查询接口；后续所有程序化消费一律走
   `workspace/final/rules.db`（或 rules_work.db），不解析 rules.md。
