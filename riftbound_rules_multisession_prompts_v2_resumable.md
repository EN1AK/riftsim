# Riftbound / LoL TCG 规则知识库：多会话、可恢复、批处理 Prompt（V2）

> 适用场景：Nex-N2.5-Pro、Qwen、GPT 系列或其他上下文有限，但具备文件系统 / Shell / SQLite / Sub-Agent 能力的 Agent。
>
> 核心目标：把 `loltcg_pdfs/`、`riftbound_en_rules/` 和 `cards_bilingual.db` 中的规则、勘误、FAQ、官方解释等资料，整理为一套统一、可追溯、可验证、可恢复、可继续维护的最终规则知识库。
>
> 本版本的第一优先级不是“单次会话尽可能多做”，而是：
>
> **任何一次 Agent 中断、context overflow、进程退出或会话切换，都不能让已经完成的正式成果丢失。**

---

# 0. 总体执行哲学

整个项目必须被视为：

```text
一个持久化任务队列
+
一组可恢复的小任务
+
一个数据库事实来源
```

而不是：

```text
一个超长 Prompt
+
一个超长 Agent 会话
```

必须遵守：

1. 聊天上下文不是长期记忆。
2. `workspace/rules_work.db` 是正式结构化成果的主要事实来源。
3. `workspace/progress.json` 记录机器可读进度。
4. `workspace/README_STATE.md` 记录给下一会话看的最小恢复信息。
5. 所有正式成果必须持续落盘。
6. 每个长阶段必须拆成 batch。
7. 每个 batch 必须能独立完成和 checkpoint。
8. 单条 item 能独立提交时，优先 item-level commit。
9. 当前 batch 完成后必须停止，不得自动继续无限扩展。
10. 如果上下文明显增长，优先保存并停止，而不是继续直到 context overflow。

---

# 1. 使用方式

不要把下面所有阶段一次性丢进同一个会话。

推荐：

```text
Session 01 → Stage 0
Session 02 → Stage 1

Session 03+ → Stage 2A，按 batch 多次执行
Session 04+ → Stage 2B，按 batch 多次执行
Session 05+ → Stage 2C，按 batch 多次执行
Session 06+ → Stage 2D，按 batch 多次执行

之后：
Stage 3 → 多 batch
Stage 4 → 多 batch
Stage 5 → 多 batch
Stage 6 → 最终构建，可按产物拆分
```

每个新会话开始时优先只读：

```text
workspace/README_STATE.md
workspace/progress.json
workspace/rules_work.db 的 schema / 当前阶段相关行
```

不要把过去所有聊天重新塞回 context。

---

# 2. 全局不可违反规则

## 2.1 Context 原则

禁止：

- 一次加载所有 PDF。
- 一次读取整张 Evidence 表。
- 一次把整本 PDF 文本塞入上下文。
- 一次把所有 FAQ / Errata / Rules 放进 context。
- 让 Sub-Agent 返回大段自然语言报告。
- 重复读取已经确认完成且当前阶段不需要的数据。
- 为了“顺便多做一点”无限扩大当前任务。
- 在正式成果只存在于内存时继续长时间工作。

必须：

- 当前会话只处理当前阶段的一个明确工作单元。
- 所有正式中间结果落盘。
- 大型结果保存到文件 / DB，只返回索引、ID、计数和 warning。
- 当 context 明显膨胀时优先 checkpoint。

---

## 2.2 数据优先于总结

禁止：

```text
原文
→ Agent A 总结
→ Agent B 根据总结再总结
→ Agent C 根据二手总结做规则
```

优先：

```text
原文
→ Evidence Store
   ↑   ↑   ↑
 Agent A/B/C
```

任何重要结论应能回查到原始 Evidence。

---

## 2.3 来源效力

默认优先级：

```text
1. 官方 Errata / Correction
2. 官方 FAQ / Ruling / Official Explanation
3. 正式 Rules / Rulebook
```

但不能做简单文本覆盖。

必须判断关系：

```text
same
replacement
partial_replacement
supplement
clarification
scope_restriction
exception
example
conflict
unresolved
```

特别注意：

- FAQ 默认用于解释、补充、限定、例外和案例。
- FAQ 不默认覆盖 Rulebook。
- Errata 只修改其明确涉及的部分。
- 不得扩大 Errata 的修改范围。

---

## 2.4 版本 / 时间 / 语言

判断顺序：

```text
明确版本继承关系
↓
发布时间 / 更新时间
↓
语言
```

对于同版本或明确对应版本：

```text
英文官方文本 > 中文官方文本
```

但：

- 不能拿明显更旧的英文资料机械覆盖更新的中文资料。
- 版本关系不清晰时进入 `manual_review`。
- 日期根据文件名推断时不得标记 `confirmed`。

---

## 2.5 官方内容与模型推导必须区分

最终必须区分：

```text
canonical_rule
official_interpretation
derived_interpretation
exception
example
editorial_note
unresolved
```

模型归纳不得伪装成官方规则。

---

# 3. 推荐 Workspace

```text
workspace/
    README_STATE.md
    progress.json
    source_manifest.json
    rules_work.db

    extracted/
    reports/
    checkpoints/
    final/
```

推荐数据库逻辑表：

```text
sources
processing_tasks
processing_items
evidence
rules
rule_evidence
alignments
reconciliations
changes
conflicts
manual_review
verification
```

如果已有 schema 不完全一致，可以复用原结构，不必为了形式重建全部数据库。

---

# 4. 通用任务状态

至少使用：

```text
pending
running
completed
failed
needs_review
```

推荐所有长任务记录：

```text
task_id
stage
substage
source_id
batch_id
item_id
status
started_at
completed_at
attempt_count
failure_reason
checkpoint_ref
notes
```

---

# 5. 通用批处理协议

所有可能很长的 Stage 默认使用以下协议。

## 5.1 启动

1. 读取 `README_STATE.md`
2. 读取 `progress.json`
3. 查询当前 Stage 的任务状态
4. 找出：
   - running
   - failed
   - pending
   - needs_review
5. 不重做 completed

---

## 5.2 Batch 选择优先级

```text
1. 可安全恢复的 running batch
2. 已具备重试条件的 failed batch
3. pending batch
4. needs_review 仅在明确的 review 会话中处理
```

---

## 5.3 单次会话只处理一个 batch

默认：

```text
one invocation = one batch
```

完成一个 batch 后：

```text
checkpoint
↓
STOP
```

不得自动开始下一个 batch。

---

## 5.4 原子提交原则

如果 item 可独立落库：

```text
处理 item
↓
validate
↓
写 DB
↓
更新 item status
↓
COMMIT
```

不要：

```text
results = []

处理几百条
全部存在内存
最后统一保存
```

---

## 5.5 上下文安全阈值

出现以下情况立即进入 checkpoint：

- Tool Output 变大
- 当前 batch 比预计复杂
- 需要不断加载旧 Evidence
- 开始重复历史分析
- 当前 session 已经承担多个不相关子任务
- 剩余 context 可能不足以完成可靠保存

原则：

> 安全 checkpoint > 多处理几条。

---

# 6. Stage 0 — 项目启动 / 状态恢复

## PROMPT — STAGE 0

你正在处理一个跨多个会话执行的 Riftbound / LoL TCG 规则知识库项目。

资料位于：

```text
loltcg_pdfs/
riftbound_en_rules/
cards_bilingual.db
```

本阶段只负责建立或恢复可持久化 workspace。

不要开始大规模读取 PDF，不要开始正式规则抽取。

### 6.1 检查已有状态

优先检查：

```text
workspace/README_STATE.md
workspace/progress.json
workspace/rules_work.db
workspace/source_manifest.json
```

如果已有：

- 读取状态
- 检查 DB schema
- 检查当前 Stage
- 检查是否存在未正常关闭的 running task
- 不重新执行 completed 阶段

如果不存在，则初始化。

---

### 6.2 初始化

创建：

```text
workspace/
    README_STATE.md
    progress.json
    source_manifest.json
    rules_work.db
    extracted/
    reports/
    checkpoints/
    final/
```

数据库至少支持：

```text
sources
processing_tasks
processing_items
evidence
rules
rule_evidence
alignments
reconciliations
changes
conflicts
manual_review
verification
```

---

### 6.3 恢复能力要求

必须确保：

- Stage 有状态。
- Task 有状态。
- 长任务能继续拆成 item / batch。
- 已完成 item 可以被程序化识别。
- Agent 新会话不需要读取旧聊天即可恢复。

---

### 6.4 README_STATE.md

保持简短。

至少包含：

```text
Project:
Current stage:
Current batch:

Completed stages:
Pending stages:

Completed sources:
Pending sources:

Database:
Important tables:

Statistics:
- sources
- evidence
- rules
- conflicts
- manual_review

Running tasks:
Failed tasks:
Needs review:

Known warnings:

Next recommended action:
```

---

### 6.5 完成条件

只有以下成立才能标记 Stage 0 completed：

- workspace 建立或恢复成功
- SQLite 可用
- progress 可持久化
- README_STATE 可作为新会话入口
- task/item 状态可恢复
- 下一阶段明确为 Stage 1

最后：

```text
更新 rules_work.db
更新 progress.json
更新 README_STATE.md
Stage 0 = completed
STOP
```

不得自动进入 Stage 1。

---

# 7. Stage 1 — Source Inventory + PDF Preprocessing

## PROMPT — STAGE 1

继续现有规则知识库项目。

首先读取：

```text
workspace/README_STATE.md
workspace/progress.json
workspace/rules_work.db
```

本阶段目标：

> 建立 Source Manifest、必要的 PDF 预处理结果，以及后续 Extraction Task Queue。

不要进入正式 Evidence Extraction。

---

## 7.1 Source Inventory

扫描：

```text
loltcg_pdfs/
riftbound_en_rules/
cards_bilingual.db
```

每个来源至少记录：

```text
source_id
source_document
source_type
language
version
date
effective_date
page_count
supersedes
possible_counterpart
date_confidence
version_confidence
notes
```

`source_type` 可使用：

```text
rule
errata
faq
ruling
official_explanation
other
```

---

## 7.2 日期 / 版本可信度

使用：

```text
confirmed
inferred
unknown
```

仅根据文件名推断：

```text
date_confidence = inferred
```

不得写成 confirmed。

---

## 7.3 PDF 预处理

必要时建立：

```text
source_id
page
section
heading
text
```

的可追溯表示。

写入：

```text
workspace/extracted/
```

不要把全文输出进聊天。

---

## 7.4 建立 Extraction Queue

按以下维度拆任务：

- 文档
- section
- 页数
- 文本规模
- FAQ 数量
- 内容复杂度

推荐原始文本规模：

```text
约 10k–30k tokens / extraction task
```

但如果 task 仍可能导致上下文过大，应继续拆分。

每个 task 至少：

```text
task_id
stage
source_id
page_start
page_end
section
status
assigned_role
notes
```

---

## 7.5 Stage 1 也必须可恢复

如果 source 很多，不要求单次会话扫完整个目录。

可以按 source batch：

```text
batch 001 → 若干文档
checkpoint
STOP

batch 002 → 若干文档
checkpoint
STOP
```

每完成一份 source 的 inventory：

```text
写 sources
写 manifest
COMMIT
```

---

## 7.6 完成条件

程序化确认：

```text
未发现的输入 = 0
pending inventory task = 0
running inventory task = 0
failed inventory task = 0
```

允许存在：

```text
needs_review
```

最后更新：

```text
source_manifest.json
rules_work.db
progress.json
README_STATE.md
```

全部完成后：

```text
Stage 1 = completed
STOP
```

不得自动开始 Stage 2。

---

# 8. Stage 2 通用 Evidence Extraction 协议

Stage 2A / 2B / 2C / 2D 都必须遵循。

## 8.1 Extraction 只回答

> 当前来源明确说了什么？

不回答：

> 最终规则应该是什么？

---

## 8.2 通用 Evidence Schema

每条 Evidence 至少记录：

```text
evidence_id
rule_id_candidate
topic

source_id
source_type
source_language
source_document

version
date

page
section
heading
rule_number

original_text
normalized_summary

applicable_object
trigger
precondition
effect
restriction
exception
example

confidence
notes
```

强制保留：

```text
original_text
source_id
page 或等价定位信息
```

摘要不能替代原文。

---

## 8.3 Stage 2 执行方式

每次：

```text
读取 checkpoint
↓
选择一个 extraction batch
↓
逐 item 处理
↓
逐 item 写 DB
↓
COMMIT
↓
batch validation
↓
checkpoint
↓
STOP
```

不得：

```text
一个会话试图完成整个 Stage 2X
```

---

# 9. Stage 2A — 中文 Rules Evidence Extraction

## PROMPT — STAGE 2A

本会话只处理：

```text
source_type = rule
language = zh
```

不要处理：

- 英文 Rules
- Errata
- FAQ
- 最终规则裁决

---

## 9.1 Batch

从 `processing_tasks` 中选择一个最小未完成 batch。

如果原 task 过大，继续拆成：

```text
10k–30k tokens
```

或更小。

---

## 9.2 每个 chunk

1. 读取当前 chunk。
2. 提取 Evidence。
3. 保留规则编号、页码、heading。
4. 写入 DB。
5. 标记 item/task 进度。
6. COMMIT。
7. 释放当前 chunk。

---

## 9.3 禁止

不要：

- 修改旧规则
- 应用 Errata
- 用 FAQ 解释规则
- 做英文对齐
- 生成 canonical_rule
- 根据上下文推测不存在的规则

---

## 9.4 Batch 完成检查

检查：

```text
输入页 / section 范围
Evidence 数
是否存在大段页面异常为 0
是否缺 source_id / page
是否重复写入
failed
needs_review
```

完成当前 batch：

```text
checkpoint
STOP
```

---

## 9.5 Stage 2A 整体完成

只有：

```text
Stage 2A pending = 0
Stage 2A running = 0
Stage 2A failed = 0
```

才：

```text
Stage 2A = completed
```

不得自动进入 Stage 2B。

---

# 10. Stage 2B — 英文 Rules Evidence Extraction

## PROMPT — STAGE 2B

本会话只处理：

```text
source_type = rule
language = en
```

执行方式与 Stage 2A 相同。

特别保留：

- 英文官方术语
- Rule Number
- Section Heading
- Timing / Trigger 精确措辞
- Restriction / Exception 的原始限定词

不要为了方便后续中文输出而丢掉英文原文。

每个 batch 完成：

```text
写 DB
更新 task
更新 progress
更新 README_STATE
STOP
```

整体完成判断：

```text
pending = 0
running = 0
failed = 0
```

然后：

```text
Stage 2B = completed
STOP
```

---

# 11. Stage 2C — Errata / Correction Evidence Extraction

## PROMPT — STAGE 2C

本会话只处理：

```text
Errata
Correction
```

不要重新抽取 Core Rules。

---

## 11.1 每条 Errata 尽量提取

```text
target_rule_candidate
target_source
original_fragment
corrected_fragment
modification_type
effective_scope
```

`modification_type`：

```text
replacement
partial_replacement
terminology_fix
numeric_change
condition_change
scope_change
effect_change
other
uncertain
```

---

## 11.2 不进行最终应用

本阶段只记录：

> 官方要求修改什么。

不要直接改 canonical_rule。

最终应用发生在 Stage 4。

---

## 11.3 Errata 原子处理

每条 Errata：

```text
读取
↓
定位 target candidate
↓
保存原片段
↓
保存修正片段
↓
保存 scope
↓
写 Evidence
↓
COMMIT
```

如果 target 无法确认：

```text
needs_review
```

不要让单条失败拖垮整个 batch。

---

## 11.4 高风险项

以下进入 needs_review：

- 找不到对应原规则
- 指向规则编号不存在
- 中英文 Errata 意义明显不同
- 日期 / 版本不清晰
- 修改范围无法确定
- 一条 Errata 似乎影响多个不相关规则

---

## 11.5 Batch 结束

输出简短统计：

```text
Batch:
Errata items:
Evidence:
Mapped targets:
Unmapped targets:
Failed:
Needs review:
Warnings:
```

写入 DB / reports。

然后：

```text
checkpoint
STOP
```

整体完成后：

```text
Stage 2C = completed
STOP
```

---

# 12. Stage 2D — FAQ / Ruling / Official Explanation Extraction

## PROMPT — STAGE 2D

本阶段处理：

```text
FAQ
Ruling
Official Explanation
官方案例说明
```

禁止试图在一个会话内完成整个 Stage 2D。

---

## 12.1 默认 Batch 大小

推荐：

```text
10–30 条 FAQ / Ruling
```

默认：

```text
20 条
```

复杂条目：

```text
5–10 条
```

---

## 12.2 每条 FAQ 分类

```text
example_only
rule_interpretation
additional_condition
exception
rule_change_candidate
uncertain
```

`rule_change_candidate` 只是 Extraction 标记。

不得直接修改最终规则。

---

## 12.3 FAQ Evidence 强制保存

```text
original_question
original_answer
source_id
source_document
page / section
involved_cards
card_ids
topic
rule_id_candidate
classification
confidence
```

以及通用 Evidence 字段。

---

## 12.4 cards_bilingual.db

仅用于：

- 卡名中英文映射
- card_id 对齐
- 别名识别
- 卡牌实体识别

不得把卡牌 DB 当成高于 Rules / FAQ / Errata 的规则来源。

---

## 12.5 禁止过度泛化

一个具体 FAQ 案例不得自动变成一般规则。

如果认为存在可泛化解释，只记录：

```text
possible_generalization = true
generalization_basis
generalization_scope
confidence
```

等待 Stage 4 判断。

---

## 12.6 单条 FAQ 即原子恢复单元

推荐：

```text
读取一条 FAQ
↓
实体识别
↓
分类
↓
抽取 Evidence
↓
必要时局部回查规则
↓
validate
↓
写 DB
↓
标记 item
↓
COMMIT
↓
下一条
```

即使第 17/20 条出错，前 16 条仍应已经存在于 DB。

---

## 12.7 错误处理

单条无法完成：

```text
status = failed / needs_review
failure_reason
retry_hint
```

然后继续 batch 内下一条。

不得静默跳过。

---

## 12.8 Batch 完成检查

至少检查：

```text
Processed items
Evidence added
Evidence updated

example_only
rule_interpretation
additional_condition
exception
rule_change_candidate
uncertain

Failed
Needs review
```

然后：

```text
checkpoint
STOP
```

严禁自动开始下一 batch。

---

## 12.9 Stage 2D 整体完成

只有：

```text
pending = 0
running = 0
failed = 0
```

才：

```text
Stage 2D = completed
```

允许仍有 `needs_review`，但必须记录。

不得自动开始 Stage 3。

---

# 13. Stage 3 — Entity Resolution + 中英文 Alignment

## PROMPT — STAGE 3

本阶段目标：

1. Card / Object Entity Resolution
2. 中英文 Evidence Alignment
3. 对应版本识别

本阶段不做最终 Canonical Rule 裁决。

---

## 13.1 不得全库载入

不要一次读取全部 Evidence。

按以下之一建立 batch：

```text
topic
section
rule number
rule_id_candidate
card_id
semantic candidate group
```

推荐：

```text
一次 20–100 个 candidate pair
```

复杂 topic 应更小。

---

## 13.2 Entity Resolution

使用：

```text
cards_bilingual.db
```

建立：

```text
card_id
english_name
chinese_name
aliases
```

把 Evidence 中涉及的卡牌实体尽可能挂到统一 `card_id`。

---

## 13.3 Alignment Relation

对疑似对应 Evidence 判断：

```text
equivalent
translation_difference
missing_information
semantic_difference
actual_conflict_candidate
uncertain
```

---

## 13.4 Alignment Record

至少：

```text
alignment_id
evidence_a
evidence_b
relation
confidence
version_relation
notes
```

每个 alignment candidate 处理后即可写 DB。

不要等整个 topic 完成才统一写。

---

## 13.5 高风险项

进入 manual_review candidate：

- 无法确定是否对应版本
- 中文比英文多重要条件
- 英文明显旧于中文
- 两者无法同时成立
- 翻译差异可能改变 timing / trigger / scope
- candidate match 本身不可靠

---

## 13.6 Batch 完成

检查：

```text
candidate pairs
aligned
uncertain
conflict candidate
needs_review
failed
```

然后：

```text
checkpoint
STOP
```

---

## 13.7 Stage 3 完成

只有：

```text
pending alignment task = 0
running = 0
failed = 0
```

且未对齐项均显式记录，才：

```text
Stage 3 = completed
STOP
```

不得自动进入 Stage 4。

---

# 14. Stage 4A — Rule Clustering

推荐把原 Stage 4 拆为：

```text
Stage 4A — Rule Clustering
Stage 4B — Rule Reconciliation
```

避免一次同时承担聚类和最终裁决。

---

## PROMPT — STAGE 4A

目标：

> 把 Evidence 映射到稳定 Rule ID。

不进行完整 canonical rule 裁决。

---

## 14.1 Batch

按：

```text
topic
section
rule number
rule_id_candidate
```

分批。

不要读取整库 Evidence。

---

## 14.2 聚类依据

```text
official rule number
topic
section
applicable_object
trigger
effect
restriction
exception
semantic similarity
```

建立：

```text
rule_id
canonical_topic
```

例如：

```text
R-TIMING-001
R-COMBAT-014
R-REACTION-007
```

---

## 14.3 禁止

不要：

- 因中文 / 英文不同创建两个 Rule ID
- 因关键词相似错误合并不同规则
- 在证据不足时强行合并

无法确定：

```text
needs_review
```

---

## 14.4 原子保存

每确认一个稳定 cluster：

```text
写 rules
写 rule_evidence
COMMIT
```

---

## 14.5 Batch 完成

检查：

```text
Evidence considered
Mapped
Unmapped
New Rule IDs
Merged candidates
Needs review
Failed
```

然后：

```text
checkpoint
STOP
```

---

## 14.6 Stage 4A 完成

所有可聚类 Evidence：

- 已映射 Rule
- 或明确 unmapped / needs_review

且：

```text
pending = 0
running = 0
failed = 0
```

则：

```text
Stage 4A = completed
STOP
```

---

# 15. Stage 4B — Rule Reconciliation

## PROMPT — STAGE 4B

目标：

> 对每个 Rule ID 的 Evidence 做来源效力、版本、语言、Errata、FAQ、例外和冲突裁决，生成 proposed canonical rule。

---

## 15.1 一个 Rule 或极小 Rule batch

默认：

```text
1–5 个 Rule ID / batch
```

复杂 Rule：

```text
1 个 Rule ID
```

只读取：

> 当前 Rule 所需 Evidence。

不得 dump 整库。

---

## 15.2 Evidence 关系

```text
same
replacement
partial_replacement
supplement
clarification
scope_restriction
exception
example
conflict
unresolved
```

---

## 15.3 来源效力

### Errata

- 明确修正规则
- 仅修改其覆盖范围

### FAQ / Ruling

- 默认解释 / 补充 / 限定 / 例外 / example
- 只有明确改变旧规则时才作为 rule change

### Rules

- 基础规范来源

---

## 15.4 版本 / 时间 / 语言

```text
版本继承关系
↓
时间
↓
语言
```

同版本 / 对应版本：

```text
英文官方文本 > 中文官方文本
```

旧英文不得机械覆盖更新中文。

---

## 15.5 FAQ 推导

如果从 FAQ 推出一般解释：

```text
derived_from_faq = true
```

并保存：

```text
FAQ evidence_id
推导依据
推导范围
confidence
```

不得标成 official rule。

---

## 15.6 每个 Rule 输出

```text
rule_id
topic
proposed_canonical_rule
applicable_object
trigger
precondition
effect
restriction
exception
official_interpretation
derived_interpretation
example
status
needs_verification
```

并建立：

```text
rule_evidence
reconciliations
changes
conflicts
```

---

## 15.7 必须进入 Verification

如果：

- 被 Errata 修改
- 存在多版本
- 中英文有差异
- FAQ 被泛化
- 有 exception
- 有 scope restriction
- 有 actual conflict
- 有模型推导
- 结论置信度低

则：

```text
needs_verification = true
```

---

## 15.8 Rule 级 Commit

每完成一个 Rule：

```text
写 reconciliation
写 proposed rule
写 links
写 flags
COMMIT
```

不要等整个 batch 最后才统一保存。

---

## 15.9 Batch 结束

统计：

```text
Rules processed
Resolved
Unresolved
Needs verification
Conflicts
Needs review
Failed
```

然后：

```text
checkpoint
STOP
```

---

## 15.10 Stage 4B 完成

所有 Rule：

- 有 proposed canonical rule
- 或 status = unresolved

且：

```text
pending = 0
running = 0
failed = 0
```

才：

```text
Stage 4B = completed
STOP
```

---

# 16. Stage 5 — Independent Verification

## PROMPT — STAGE 5

这是独立验证阶段。

不要默认相信 Stage 4B 的结论。

---

## 16.1 只处理

```text
needs_verification = true
```

的 Rule。

---

## 16.2 Batch 大小

默认：

```text
1–5 个 Rule
```

高风险：

```text
1 Rule / batch
```

---

## 16.3 验证流程

每个 Rule：

1. 读取 proposed canonical rule
2. 获取相关 evidence_id
3. 回查关键原文
4. 检查版本 / 日期 / 语言
5. 检查 Errata
6. 检查 FAQ 是否过度泛化
7. 检查 exception / scope
8. 独立判断结论是否有证据支持

---

## 16.4 Verification Status

```text
verified
verified_with_changes
rejected
needs_review
```

---

## 16.5 特别检查

### Errata

确认：

- 修改目标正确
- 修改范围未扩大
- 未删除未被修改的原规则部分

### FAQ

确认：

- example 未被错误泛化
- interpretation 与原规则兼容
- derived interpretation 范围未超出来源

### 中文 / 英文

确认：

- 是否真是对应版本
- 是否存在时间差
- 英文优先规则是否被机械误用

### 冲突

确认是否其实是：

- scope 不同
- version 不同
- exception
- clarification

而不是真冲突。

---

## 16.6 如果验证结论不同

记录：

```text
rule_id
stage4_conclusion
verification_conclusion
relevant_evidence
disagreement_reason
```

进入：

```text
manual_review
```

除非证据能够明确解决。

---

## 16.7 Rule 级 Commit

每验证一个 Rule：

```text
写 verification
必要时更新 proposed rule
写 disagreement / manual_review
COMMIT
```

---

## 16.8 Batch 结束

```text
Verified
Verified with changes
Rejected
Needs review
Failed
```

然后：

```text
checkpoint
STOP
```

---

## 16.9 Stage 5 完成

所有需要验证的 Rule 都具有终态：

```text
verified
verified_with_changes
rejected
needs_review
```

且：

```text
pending verification = 0
running = 0
failed = 0
```

则：

```text
Stage 5 = completed
STOP
```

不得自动进入 Stage 6。

---

# 17. Stage 6 — Final Build + Coverage Check

## PROMPT — STAGE 6

这是最终构建阶段。

主要从：

- verified rules
- reconciliations
- changes
- manual_review
- source metadata

生成最终产物。

不要重新大规模读取 PDF。

只有局部问题才回查 Evidence。

---

## 17.1 最终构建前硬性检查

程序化检查：

```text
Documents discovered
Documents processed
Documents failed

Evidence extracted
Evidence mapped
Unmapped evidence

Rules generated
Rules verified

Errata processed
FAQ processed
Rulings processed

Conflicts resolved
Unresolved conflicts

Manual review items
```

还要检查：

- source 是否未处理
- failed task 是否未恢复
- Errata 是否未应用
- FAQ 是否未挂载
- Evidence 是否未映射
- Rule 是否无来源
- inferred 是否误写 confirmed
- FAQ 是否过度泛化
- superseded rule 是否仍作为当前规则
- verification 是否 pending
- manual_review 是否被擅自裁决

如果有未处理 source 或 failed extraction：

> 不得声称 pipeline 完整完成。

---

## 17.2 最终产物

### rules.md

```text
workspace/final/rules.md
```

每条规则至少：

```text
Rule ID
主题
规范规则
适用对象
触发条件
前置条件
效果
限制
例外
官方解释
由 FAQ 推导的解释
案例
来源
状态
```

区分：

```text
官方规则
官方解释
模型推导
案例
例外
未解决
```

---

### rules.db

```text
workspace/final/rules.db
```

应支持按：

```text
rule_id
topic
card_id
keyword
trigger
source
version
```

查询。

---

### change_log.md

```text
workspace/final/change_log.md
```

至少记录：

```text
rule_id
original_content
new_content
source_type
source_language
source_document
version
date
modification_type
reason
final_conclusion
```

---

### manual_review.md

```text
workspace/final/manual_review.md
```

每项：

```text
Issue ID
Rule ID
问题
来源 A
来源 B
冲突点
可能解释
无法自动裁决原因
```

---

### coverage_report.md

```text
workspace/final/coverage_report.md
```

至少：

```text
Documents discovered:
Documents processed:
Documents failed:

Evidence extracted:
Evidence mapped:
Unmapped evidence:

Rules generated:
Rules verified:

Errata applied:
FAQ attached:
Rulings attached:

Conflicts resolved:
Unresolved conflicts:

Manual review items:
```

---

## 17.3 Stage 6 也允许分批

如果最终规则很多，不要强行一次生成全部 Markdown。

可以拆：

```text
6A Coverage Check
6B rules.md 分章节构建
6C rules.db 构建
6D change_log
6E manual_review
6F Final Consistency Check
```

每个产物写完立即保存。

---

## 17.4 最终一致性检查

确认：

```text
rules.md
rules.db
change_log.md
manual_review.md
coverage_report.md
```

彼此数量和状态一致。

不能：

> `rules.md` 说已解决，但 `manual_review.md` 仍列 unresolved。

---

## 17.5 最终状态

如果所有预定流程完成：

```text
Current stage: COMPLETE
```

如果仍有人工确认项：

```text
Pipeline complete with manual review items remaining.
```

这不等于失败。

但如果仍有：

```text
未处理 source
failed extraction
pending verification
```

则不得标记完整完成。

---

# 18. 通用新会话恢复 Prompt

## PROMPT — RESUME

继续现有 Riftbound / LoL TCG 规则知识库项目。

不要从头开始。

首先读取：

```text
workspace/README_STATE.md
workspace/progress.json
```

并检查：

```text
workspace/rules_work.db
```

确认：

```text
当前 stage
当前 substage
当前 batch
completed tasks
running tasks
pending tasks
failed tasks
needs_review tasks
processing_items 状态
当前数据库 schema
下一步
```

不要重新执行已经 completed 的任务。

如果存在上一次中断留下的 `running`：

1. 检查其 item-level 已持久化结果。
2. 已完成 item 不重做。
3. 从第一个未完成 item 恢复。
4. 无法确认时标记 needs_review 或回退 pending。
5. 不得默认整个 batch 从头重跑。

只恢复：

> 当前阶段尚未完成的最小任务集合。

不要一次读取全部历史数据。

正式结果继续写入 workspace / DB。

本会话只完成一个 batch。

完成后：

```text
COMMIT
更新 README_STATE.md
更新 progress.json
STOP
```

---

# 19. Context Emergency Checkpoint Prompt

## PROMPT — CONTEXT EMERGENCY CHECKPOINT

当前会话上下文已经过长，或预计即将无法安全完成当前任务。

立即停止：

- 加载新的 PDF
- 加载新的 Evidence
- 扩大任务范围
- 大规模 Tool Output
- 开始新的 batch
- 开始新的 Rule / FAQ

现在只执行 checkpoint。

### 19.1 优先完成当前最小原子项

如果当前正在处理一条：

```text
FAQ
Errata
Evidence chunk
Alignment pair
Rule reconciliation
Verification rule
```

且能够在安全范围内完成，则：

```text
完成当前 item
写 DB
COMMIT
```

如果无法安全完成：

```text
标记 item = pending / failed / needs_review
记录恢复位置
```

不得为了“完成它”继续大量加载信息。

---

### 19.2 保存

立即：

1. 写入所有尚未持久化的正式结果。
2. 更新 `rules_work.db`。
3. 更新 item status。
4. 更新 task / batch status。
5. COMMIT。
6. 更新 `progress.json`。
7. 更新 `README_STATE.md`。

README_STATE 必须明确：

```text
当前 stage
当前 batch
最后成功完成的 item
已完成内容
尚未完成内容
failed
needs_review
下一会话具体从哪里继续
```

---

### 19.3 停止

不要：

- 输出大段历史总结
- 继续处理新 item
- 开始下一个 batch
- 进入下一个 Stage

目标：

> 一个完全新的会话可以仅凭 workspace 无损继续。

完成 checkpoint 后立即 STOP。

---

# 20. 通用 Batch Completion Prompt

如果希望 Agent 每次都严格只跑一批，可以在任意 Stage Prompt 后追加：

```text
本次调用只允许完成一个 batch。

完成当前 batch 后必须：
1. 校验当前 batch
2. 保存所有正式成果
3. COMMIT
4. 更新 task / item status
5. 更新 progress.json
6. 更新 README_STATE.md
7. 输出简短统计
8. STOP

即使仍有剩余 token、剩余时间和 pending task，也不得自动开始下一 batch。
```

---

# 21. 通用 Sub-Agent 协议

如果支持 Sub-Agent：

## 允许

- 不同 source / chunk 并行
- 不同 Rule ID 并行
- 独立验证
- 局部实体对齐

## 要求

Sub-Agent 必须：

1. 只处理分配给自己的有限 task。
2. 正式结果直接写入 workspace / DB，或返回严格结构化小结果给主 Agent。
3. 不返回大篇自然语言报告。
4. 提交前校验。
5. 不擅自扩大范围。

推荐返回：

```text
task_id:
batch_id:
status:
items_processed:
records_written:
failed:
needs_review:
warnings:
checkpoint:
```

主 Agent 不应把 Sub-Agent 全部历史输出重新塞入 context。

---

# 22. README_STATE.md 推荐模板

```text
Project: Riftbound / LoL TCG Rules Knowledge Base

Current stage:
Current substage:
Current batch:

Completed stages:
- ...

In-progress stages:
- ...

Pending stages:
- ...

Current batch progress:
- total:
- completed:
- failed:
- needs_review:

Database:
- path:
- schema version:

Statistics:
- sources:
- evidence:
- rules:
- alignments:
- reconciliations:
- verification:
- conflicts:
- manual_review:

Running tasks:
- ...

Failed tasks:
- ...

Needs review:
- ...

Known warnings:
- ...

Last checkpoint:
- ...

Next recommended action:
- ...
```

保持简短。

不要在 README 中复制大量 Evidence 或规则正文。

---

# 23. progress.json 推荐结构

```json
{
  "project": "riftbound_rules_kb",
  "current_stage": "2D",
  "current_substage": "faq_extraction",
  "current_batch": "2D-B018",
  "stages": {
    "0": "completed",
    "1": "completed",
    "2A": "completed",
    "2B": "completed",
    "2C": "completed",
    "2D": "in_progress",
    "3": "pending",
    "4A": "pending",
    "4B": "pending",
    "5": "pending",
    "6": "pending"
  },
  "last_checkpoint": {
    "batch_id": "2D-B017",
    "last_completed_item": "FAQ-0340"
  },
  "statistics": {},
  "warnings": []
}
```

实际字段可根据已有实现调整。

---

# 24. 推荐实际会话划分

资料较大时：

```text
Session 01 → Stage 0
Session 02 → Stage 1 batch 1
Session 03 → Stage 1 batch 2
...

Session N → Stage 2A batch 1
Session N+1 → Stage 2A batch 2
...

Stage 2B 同理
Stage 2C 同理
Stage 2D 同理

Stage 3 → 多个 alignment batch

Stage 4A → 多个 clustering batch
Stage 4B → 每次 1–5 Rule

Stage 5 → 每次 1–5 verification Rule

Stage 6 → 按最终产物拆分
```

原则不是固定 Session 数量，而是：

> 一个会话只承担一个明确、可持久化、可恢复的工作单元。

---

# 25. 整体完成标准

最终系统应满足：

```text
所有 source 有状态
所有 task 有状态
所有 item 有状态
所有 Evidence 可追溯
所有 Rule 有来源
所有 Errata 有目标或 needs_review
所有 FAQ 有分类或 needs_review
所有 Alignment 有状态
所有 Reconciliation 有状态
所有高风险 Rule 已验证或 needs_review
所有 unresolved 明确暴露
所有正式成果已持久化
```

不能通过：

```text
“Agent 似乎已经读过”
“上一轮聊天里提到过”
“模型应该记得”
```

来证明任务完成。

---

# 26. 最重要的执行模式

整个项目始终采用：

```text
读取 checkpoint
↓
选择一个最小 batch
↓
读取当前 batch 必要数据
↓
处理一个 item
↓
写 DB
↓
COMMIT
↓
继续当前 batch
↓
batch validation
↓
checkpoint
↓
STOP
```

而不是：

```text
读取所有资料
↓
长时间推理
↓
不断追加 context
↓
最后统一保存
↓
Context Overflow
↓
成果丢失
```

最终系统能够处理的总资料规模，不应直接受单个 Context Window 大小限制。
