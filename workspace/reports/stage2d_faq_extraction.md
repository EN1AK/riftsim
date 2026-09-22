# Stage 2D — FAQ / Ruling / Official Explanation Extraction Report

Date: 2026-09-20 · Stage: 2D · Executor script: `stage2d_extract_faq.py`

## 范围

仅处理 FAQ / Ruling / Official Explanation 来源（6 zh FAQ + 4 en Patch Notes）。
未重新抽取 Core Rules / Errata；未做任何规则裁决（Reconciliation 职责），
未修改 `rules` / 任何最终规则表。`rule_change_candidate` 仅为 Extraction 标记。
`cards_bilingual.db` 仅用于卡名→`card_key` 对齐（related_cards / card_ids 列），
未当作规则来源；未做过度泛化（possible_generalization 等留待 Stage 4）。

## 统计

```text
FAQ/OE documents:   10 (zh: 6 / en: 4)
Evidence rows:      604 (594 FAQ/OE items + 10 front_matter)
  zh:               332 (EV-CN-FAQ-0001..0332; 326 items + 6 front_matter)
  en:               272 (EV-EN-OE-0001..0272; 268 items + 4 front_matter)
needs_review:       0 items (4 resolved by human review on 2026-09-20)
manual_review:      15 entries (MR-2D-0001..0015)
```

### 按文档

| source_id | 文档 | 语言 | items | 页覆盖 | 编号段 |
|---|---|---|---|---|---|
| source_001 | 裁判FAQ (251023) | zh | 50 (+1 fm) | 10/10 | 0001..0051 |
| source_005 | 铸魂淬炼 官方FAQ (260114) | zh | 47 (+1 fm) | 21/21 | 0052..0099 |
| source_006 | 铸魂淬炼 裁判FAQ | zh | 93 (+1 fm) | 25/25 | 0100..0193 |
| source_007 | 破限 官方FAQ | zh | 23 (+1 fm) | 24/24 | 0194..0217 |
| source_008 | 破限 裁判FAQ (260511) | zh | 79 (+1 fm) | 24/24 | 0218..0297 |
| source_011 | 化神争锋 官方FAQ | zh | 34 (+1 fm) | 22/22 | 0298..0332 |
| source_012 | Core Rules Patch Notes | en | 86 (+1 fm) | 7/7 | 0001..0087 |
| source_014 | Spiritforged Patch Notes | en | 45 (+1 fm) | 5/5 | 0088..0133 |
| source_016 | Unleashed Patch Notes | en | 75 (+1 fm) | 7/7 | 0134..0209 |
| source_019 | Vendetta Patch Notes | en | 62 (+1 fm) | 8/8 | 0210..0272 |

（编号段 zh 指 EV-CN-FAQ、en 指 EV-EN-OE；fm=front_matter。007 p24 / 011 p22 /
016 p7 等尾页内容已确认归属前页条目或纯站点噪音，末行覆盖已逐源核对。）

### faq_classification 分布（6 类启发式）

| classification | 数量 | 口径说明 |
|---|---|---|
| example_only | 193 | 纯卡牌场景结算示例（含【卡名】且无规则引用） |
| rule_interpretation | 270 | 规则适用边界澄清；含规则引用的卡牌问答；EN CLARIFIED；007/016 prose 解释段 |
| additional_condition | 0 | 启发式未独立命中（新增前提类内容多以 prose/解释形态归入 interpretation） |
| exception | 5 | 明示“例外/特例/特殊情况”的条目 |
| rule_change_candidate | 127 | 声称规则已改：zh 含（旧）/（新）对照或“规则 X（修订后）”；EN NEW RULE/NEW SYSTEM/EDIT/REMOVAL（不改规则，仅标记） |
| uncertain | 0 | — |

EN marker 分布：source_012 CLARIFIED 58 / NEW RULE 22 / NEW SYSTEM 2 / REMOVAL 1 / EDIT 1；
source_014 NEW RULE 24 / CLARIFIED 5 / NEW SYSTEM 4；source_016 NEW RULE 29 /
CLARIFIED 21 / NEW SYSTEM 6；source_019 NEW RULE 35 / CLARIFIED RULE 11。

### 结构形态说明

- zh FAQ：问答条目 `faq_question`/`faq_answer` 完整；`related_rule_refs`（notes JSON）
  从正文及 011「相关规则：」行提取，`rule_id_candidate` 列取首个引用。
- zh 修订块（「卡名/规则（修订后）」「[新文本]」）单列条目，notes 标
  `mentions_errata`（与 Stage 2C 勘误交叉，不重复建勘误条目）。
- zh prose 条目（007 散文小节、008 分析段）`faq_question`=小节标题/节名，
  notes 标 `prose_section` / `prose_passage`，分类为启发式（MR-2D-0015）。
- en official_explanation：标记条目（NEW/CLARIFIED/EDIT/REMOVAL）多为单行声明，
  `faq_question`=标记行全文、`faq_answer`=NULL（原文完整保留于 original_text）；
  小节解释散文段单列 `prose_passage` 条目（q=NULL）。此为官方说明文形态，
  非解析缺损。
- 每源一条 `front_matter` evidence：文档头、前言、缩写指南、效力/生效日声明原文。
- 卡牌对齐：related_cards=文内【】卡名去重；card_ids=经 `cards` 表
  name_cn(+sub_title_cn)/name_en 匹配的 card_key 列表（同名多版本卡并存，未裁决）。

## needs_review items — 已全部复核修复（2026-09-20）

原 4 条 needs_review 经人工对照原文逐条复核并修复，现 needs_review=0：

| 结果 | 处理 |
|---|---|
| EV-CN-FAQ-0169（源 006 p19） | 场景+Q1..Q4 枚举合并正确，仅答案缺 `A1：` 前缀 → 已补前缀 |
| 原 0248（源 008 p8「3）…<瞬息>？」） | 原文为 1 个场景 Q+1)..4) 子问+1 个统一 A → 已并入相邻条目合并；碎片条目删除 |
| 原 0263（源 008 p13，菲兹/闪现/蔑视） | 裸问答跨行合并，逐字复核正确 → 仅清标记 |
| 原 0264/0265（源 008 p14，卡莎/顺劈回收） | 0264 答案尾行「我方基地中有【中娅沙漏】。」误入 → 已剥移为 0265 场景前缀 |

修复后原编号 0248 及其后续编号已整体前移重排（manual_fix 条目 notes 中引用的
aided 编号为重排前历史编号，有括注说明）。MR-2D-0014 已记修复结论。

另：source_006 「Q：可以。」排版错误（应为 A：）已按 typo_fixed 自动归并
（notes 标记），见 MR-2D-0002。

## manual_review（15 项，MR-2D-0001..0015）

- 0001/0002/0003/0011：日期与生效日冲突（001/006/008 zh；014/016/019 en）。
- 0002 同条：006 typo 自动归并待复核；0003：008 增量合订版本结构。
- 0004：007 金克丝中英条件分句位置差异（跨语言）。
- 0005：008 第 4 节四卡（沙丘亚龙/金克丝/均衡门徒/艾翁）中英分歧+未来更新声明。
- 0006：011 明示废弃 005 斯弗尔尚歌/厄斐琉斯答复（FAQ 间取代）。
- 0007：005『规则 735.1.c（修订后）』FAQ 直接修订核心规则条文（rule_change_candidate）。
- 0008：FAQ 内嵌勘误（005 修订块/008 永恩/011 星界灵鹭）与 2C 勘误交叉核对。
- 0009：007/011/005 效力优先声明与失效条件（临时高于核心规则，新版发布后失效）。
- 0010：012 声明与先前 FAQ 少量明确矛盾。
- 0012：019 声明 Unleashed FAQ 多条阐明已并入核心规则（reconciliation 元数据）。
- 0013：裁判FAQ（001/006/008）「不代表官方FAQ」效力层级。
- 0014：008 第 5 节无标记问答与断行解析置信度（4 条 needs_review）。
- 0015：007 prose_section 条目形态与启发式分类口径。

## Warnings / 解析决策记录

1. 解析器为逐源格式族（6 族）：001 问题N.M+Q/A 混合型；005 问/修订后块型；
   006/008 Q/A+Qn/An+场景引导+裸问答型（含 frac 跨行/跨页断句合并、场景引导段
   附加、008 第 4 节中英对照分析 prose 化）；007 散文+规则引用块+（旧）/（新）对照型；
   011 问句标题+相关规则行型；EN Patch Notes 标记条目型（含大小写混合标记、
   cookie/RELATED ARTICLES 噪音过滤、小写行非小节标题规则）。
2. 问句跨行/跨页断裂（006 索拉卡 Q1/Q2 跨 p9→p10、008 多处）按 frac 缓冲合并，
   合并结果已人工抽查确认；保守侧：断句问全部附加 needs_review。
3. confidence 分档：official 标记/修订块/rule_change_candidate=high（0.85），
   常规问答/解释=medium（0.70-0.75），unmarked 结构=low（0.55）。
4. 解析中途发现并修复：`task` 状态更新 SQL LIKE 误配（source_001% → task_001%）；
   规则号正则支持纯字母子段（187.4.c 等）；is_title/is_en_section 误吞边界。
5. evidence 编号因迭代重跑曾留空洞，交付前已重排，2026-09-20 人工复核修复后
   再次重排为 EV-CN-FAQ-0001..0332 / EV-EN-OE-0001..0272 连续序列
   （重编号脚本 stage2d_renumber.py，幂等）。
6. additional_condition=0 / uncertain=0：本批文档未出现需独立标注的条目；
   「新前提/条件」内容多以解释形态存在，未强行细分。

## 数据落点

- `workspace/rules_work.db` `evidence`：+604 行（EV-CN-FAQ-0001..0332 /
  EV-EN-OE-0001..0272），新增列 `card_ids`（faq_* 列沿用 2D schema）。
- `manual_review`：+15 行（MR-2D-0001..0015），全表 19 行。
- `processing_tasks`：10 个 2D 任务全部 completed（页范围全覆盖，notes 已记）。
- `sources.notes`：10 源补记 Stage2D 提取计数与编号段。
- 机器可读统计：`workspace/reports/stage2d_stats.json`。
- `progress.json`：stage_2d=completed；current_stage 指向 Stage 3（待指令）。

## 处理脚本

`stage2d_extract_faq.py`（仓库根目录）：tokenizer（PAGE 跟踪+EN 噪音过滤）→
6 族解析器 → 启发式六分类 → 卡牌对齐 → 逐条 INSERT（原子单位=item，逐源 COMMIT，
重跑安全按源 DELETE）→ task/sources 更新。辅助：`stage2d_manual_review.py`、
`stage2d_finalize.py`、`stage2d_renumber.py`。

STOP：Stage 2D 完成。未自动开始 Stage 3。
