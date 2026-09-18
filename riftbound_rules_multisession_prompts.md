# Riftbound / LoL TCG 规则知识库：多会话分阶段 Prompt

适用场景：Nex-N2.5-Pro 或其他上下文有限、但具备文件系统 / Shell / SQLite / Sub-Agent 能力的 Agent。

目标：把 `loltcg_pdfs/`、`riftbound_en_rules/` 和 `cards_bilingual.db` 中的规则、勘误、FAQ、官方解释等资料，整理为一套统一、可追溯、可验证、可恢复、可继续维护的最终规则知识库。

---

# 使用方式

不要把下面所有阶段一次性丢进同一个会话。

推荐：

1. 新建会话，执行 Stage 0。
2. Stage 0 完成后结束会话。
3. 新建会话，执行 Stage 1。
4. 每个 Stage / Sub-stage 尽量使用新的独立会话。
5. 每个会话开始时只读取 `workspace/README_STATE.md`、数据库 schema 和当前阶段真正需要的数据。
6. 每个会话结束前必须把正式结果写回 `workspace/`，并更新 checkpoint。
7. 不依赖聊天历史作为长期记忆。

整个任务的长期状态必须存在于：

```text
workspace/
```

而不是存在于某个 Agent 会话的 context 中。

---

# 全局不可违反的规则

这些规则适用于所有阶段。

## Context 原则

- 不要一次加载所有 PDF。
- 不要一次读取整张 Evidence 表。
- 不要把整本 PDF 的文本直接塞入上下文。
- 不要让 Sub-Agent 返回大量自然语言报告。
- 不要重复读取已经确认完成、且当前阶段不需要的资料。
- 当前会话只处理当前阶段或当前局部 Rule / Topic。
- 所有正式中间结果必须落盘。
- 如果上下文明显变长，优先 checkpoint，而不是继续强行工作。

## 数据优先于总结

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

任何重要结论应能够回查到原始 Evidence。

## 来源效力

默认：

1. 官方 Errata / Correction
2. 官方 FAQ / Ruling / Official Explanation
3. 正式 Rules / Rulebook

但这不是简单文本覆盖。

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

FAQ 默认用于解释、补充、限定、例外和案例，不默认覆盖 Rulebook。

Errata 只修改其明确涉及的部分。

## 版本 / 时间 / 语言

判断顺序：

```text
明确的版本继承关系
↓
发布日期 / 更新时间
↓
语言
```

对于同版本或明确对应版本：

```text
英文官方文本 > 中文官方文本
```

但不能拿明显更旧的英文资料机械覆盖更新的中文资料。

无法确定时进入 `manual_review`。

## 官方内容与模型推导必须区分

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

模型归纳不能伪装成官方规则。

---

# 推荐 Workspace

Agent 可以自行调整，但必须保留等价功能。

```text
workspace/
    README_STATE.md
    progress.json
    source_manifest.json
    rules_work.db

    extracted/
    reports/
    final/
```

推荐数据库逻辑表：

```text
sources
processing_tasks
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

# Stage 0 — 项目启动 / 状态恢复

> 建议：单独新会话执行。

将下面整段作为新会话 Prompt：

---

## PROMPT — STAGE 0

你正在处理一个跨多个会话执行的 Riftbound / LoL TCG 规则知识库项目。

资料位于：

- `loltcg_pdfs/`
- `riftbound_en_rules/`
- `cards_bilingual.db`

首先不要开始大规模读取 PDF，也不要开始整理最终规则。

你的任务是建立或恢复一个可跨会话继续执行的 workspace。

### 1. 检查是否已有 workspace

优先检查：

```text
workspace/README_STATE.md
workspace/progress.json
workspace/rules_work.db
workspace/source_manifest.json
```

如果已经存在：

- 读取 `README_STATE.md`
- 检查数据库 schema
- 检查当前 progress
- 判断项目处于哪个阶段
- 不要重新执行已经完成的阶段

如果不存在，则初始化 workspace。

### 2. 初始化长期状态

创建：

```text
workspace/
    README_STATE.md
    progress.json
    source_manifest.json
    rules_work.db
    extracted/
    reports/
    final/
```

根据需要自行设计 SQLite schema。

至少支持：

```text
sources
processing_tasks
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

### 3. 建立任务状态规范

任务状态至少使用：

```text
pending
running
completed
failed
needs_review
```

必须能够区分：

- 已完成 source
- 未完成 source
- 已完成 stage
- 未完成 stage
- failed tasks
- unresolved conflicts

### 4. 创建 README_STATE.md

保持简短，不要变成大篇总结。

至少包含：

```text
Project:
Current stage:

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

Known warnings:

Next recommended action:
```

目标是让未来的新会话只读这个文件和数据库，就能继续工作。

### 5. 不做的事情

本阶段不要：

- 全量读取 PDF
- 提取全部规则
- 做中英文对齐
- 做最终规则裁决

本阶段只建立可靠的跨会话执行基础。

### 6. 完成条件

只有在以下条件成立后，本阶段才能标记 completed：

- workspace 已建立或成功恢复
- SQLite 可用
- progress 可持久化
- README_STATE.md 可作为下一会话入口
- 下一阶段明确为 Source Inventory

完成后：

1. 更新 `README_STATE.md`
2. 更新 `progress.json`
3. 将 Stage 0 标记为 completed
4. 停止继续扩展任务

不要自动继续 Stage 1。

---

# Stage 1 — Source Inventory + PDF Preprocessing

> 建议：新会话执行。

---

## PROMPT — STAGE 1

继续 Riftbound / LoL TCG 规则知识库项目。

首先读取：

```text
workspace/README_STATE.md
workspace/progress.json
```

并检查：

```text
workspace/rules_work.db
```

不要重新执行已完成阶段。

本会话只执行：

> Source Inventory + 必要的 PDF 预处理准备

不要进入 Evidence Extraction。

### 1. 扫描全部输入

扫描：

```text
loltcg_pdfs/
riftbound_en_rules/
cards_bilingual.db
```

建立完整 Source Manifest。

至少记录：

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

### 2. 日期 / 版本可信度

使用：

```text
confirmed
inferred
unknown
```

如果日期只是根据文件名推断：

```text
date_confidence = inferred
```

不得写成 confirmed。

### 3. 中英文 counterpart

尝试识别可能对应的：

```text
英文 Rulebook
↕
中文 Rulebook
```

但不要强行认定。

如果不确定：

```text
possible_counterpart = candidate
confidence = low/uncertain
```

### 4. PDF 预处理

如果后续读取 PDF 需要文本提取，可以建立 page → text 的可追溯表示。

要求：

- 保留原始页码
- 尽可能保留 heading / section
- 不丢掉 source_id
- 不要把整个 PDF 文本输出到聊天中

可以把结果写入：

```text
workspace/extracted/
```

具体格式自行决定。

### 5. 建立 Extraction Task Queue

根据：

- 文档
- section
- 页数
- 文本规模

拆出后续 Extraction Task。

不要为了减少 task 数量把 chunk 做得过大。

推荐单个任务涉及的原始文本规模约：

```text
10k–30k tokens
```

允许根据文档结构调整。

为每个 task 建立：

```text
task_id
source_id
page_start
page_end
section
status
assigned_role
notes
```

写入 `processing_tasks`。

### 6. 不做的事情

本阶段不要：

- 正式抽取大量 Evidence
- 合并规则
- 生成 Rule ID
- 中英文语义对齐
- 处理最终冲突

### 7. 完成条件

必须满足：

- 所有输入文件已被发现
- 所有 source 有稳定 `source_id`
- 每份 PDF 有 page_count 或合理的规模记录
- source_type / language 基本识别
- extraction tasks 已建立
- 未知日期 / 版本正确标记为 unknown 或 inferred
- Source Manifest 已持久化

最后更新：

```text
workspace/source_manifest.json
workspace/rules_work.db
workspace/progress.json
workspace/README_STATE.md
```

将 Stage 1 标记 completed。

不要自动开始 Stage 2。

---

# Stage 2A — 中文 Rules Evidence Extraction

> 建议：新会话。资料很多时，可以拆成多个 2A 会话。

---

## PROMPT — STAGE 2A

继续现有规则知识库项目。

首先读取：

```text
workspace/README_STATE.md
workspace/progress.json
```

检查 `rules_work.db` 中 Stage 2A 尚未完成的任务。

本会话只处理：

> 中文正式规则正文（source_type = rule, language = zh）

不要处理英文 Rules、Errata、FAQ，也不要做最终规则裁决。

### Extraction 原则

你的任务只回答：

> 这个来源明确说了什么？

不得回答：

> 最终规则应该是什么？

### Evidence Schema

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

### 强制要求

必须保存：

```text
original_text
source_id
page
```

摘要不能替代原文。

### Context 管理

每次只读取一个有限 task / chunk。

完成后：

1. Evidence 写入数据库
2. task 标记 completed
3. 释放当前 chunk
4. 再处理下一个 task

不要在 Main Context 中累积所有中文规则原文。

如果支持 Sub-Agent：

- 可以并行处理不同 source / chunk
- Sub-Agent 必须直接把正式结果写入 workspace / DB
- Sub-Agent 返回主 Agent 的消息保持极短

推荐返回格式：

```text
task_id:
status:
source_id:
pages:
evidence_count:
warnings:
```

### 禁止

不要：

- 修改旧规则
- 应用 Errata
- 用 FAQ 解释规则
- 做英文对齐
- 生成 canonical_rule
- 从当前规则推测不存在的规则

### 完成检查

检查：

- 所有中文 rule extraction task 是否 completed
- 是否有 failed task
- Evidence 数量是否异常为 0
- 是否有大段页面完全未产出 Evidence，需要人工判断是否合理

如果存在 failed：

- 重新进入 pending 或 needs_review
- 不得静默跳过

结束前更新：

```text
progress.json
README_STATE.md
rules_work.db
```

如果所有中文 Rules 完成，则 Stage 2A = completed。

不要自动继续 Stage 2B。

---

# Stage 2B — 英文 Rules Evidence Extraction

> 建议：新会话。

---

## PROMPT — STAGE 2B

继续现有规则知识库项目。

读取：

```text
workspace/README_STATE.md
workspace/progress.json
```

本会话只处理：

> 英文正式规则正文（source_type = rule, language = en）

不要重新处理中文 Rules。

执行原则与 Stage 2A 相同：

- 按 task / chunk 局部读取
- 抽取 Evidence
- 保留原文、页码、source_id
- 不做最终裁决
- 不做中英文合并
- 不应用 Errata
- 不根据 FAQ 修改规则

Evidence 使用现有统一 schema。

### 特别注意

尽量保留：

- 英文官方术语
- Rule Number
- Section Heading
- Timing / Trigger 等精确措辞

不要因为后续会翻译就提前把英文原文只保留中文摘要。

### 完成检查

确认所有英文 Rule extraction task：

```text
completed / failed / needs_review
```

failed 不得静默遗漏。

更新 checkpoint。

所有英文 Rules 完成后：

```text
Stage 2B = completed
```

不要自动继续其他 Stage。

---

# Stage 2C — Errata / Correction Evidence Extraction

> 建议：新会话。

---

## PROMPT — STAGE 2C

继续现有规则知识库项目。

读取 checkpoint，并只处理：

> 所有 Errata / Correction 来源

不要重新抽取 Core Rules。

### 目标

Errata Extraction 不只是摘录文本，还需要尽可能识别：

```text
target_rule_candidate
target_source
original_fragment
corrected_fragment
modification_type
effective_scope
```

但此阶段仍然**不做最终规则裁决**。

### modification_type

可使用：

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

### Evidence

仍使用统一 Evidence Schema，并额外记录 Errata 特有字段。

如果 Errata 表达：

> 将 X 替换成 Y

必须同时保存：

- X
- Y
- source
- page
- date/version

### 不允许

不要仅因为看到 Errata 就直接修改 `canonical_rule`。

此阶段做的是：

> 记录“官方要求修改什么”

最终应用发生在 Reconciliation。

### 高风险标记

以下情况标记 needs_review：

- 找不到对应原规则
- Errata 指向规则编号不存在
- 中英文 Errata 意义明显不同
- 日期 / 版本不清晰
- 修改范围无法确定

### 完成条件

所有 Errata source / tasks 处理完成。

生成简短统计：

```text
Errata documents:
Errata evidence:
Mapped targets:
Unmapped targets:
Warnings:
```

写入 reports 或 DB，不要把全部条目 dump 到聊天里。

更新 checkpoint。

---

# Stage 2D — FAQ / Ruling / Official Explanation Extraction

> 建议：新会话。

---

## PROMPT — STAGE 2D

继续现有规则知识库项目。

本会话只处理：

- FAQ
- Ruling
- Official Explanation
- 官方案例说明

不要重新读取已经完成的 Core Rules / Errata。

### 每条 FAQ 先分类

使用：

```text
example_only
rule_interpretation
additional_condition
exception
rule_change_candidate
uncertain
```

注意：

`rule_change_candidate` 只是 Extraction 阶段的标记。

不要在这里直接修改最终规则。

### FAQ Evidence 必须保留

- 原始问题
- 原始回答
- source_id
- page / section
- 涉及卡牌
- 涉及规则主题
- rule_id_candidate（如果能判断）
- classification
- confidence

### 禁止过度泛化

例如一个 FAQ 说明某一张卡在某一场景如何结算：

不要自动写成：

> 所有类似卡牌永远如此。

除非原始 FAQ 或正式规则能够支持这一泛化。

### cards_bilingual.db

可以使用数据库做：

- 卡名中英文映射
- card_id 对齐
- 卡牌实体识别

不要把 `cards_bilingual.db` 默认当成高于官方 Rules / FAQ / Errata 的规则来源。

### 完成条件

所有 FAQ / ruling / explanation source 完成。

记录：

```text
FAQ evidence:
example_only:
rule_interpretation:
additional_condition:
exception:
rule_change_candidate:
uncertain:
```

更新 checkpoint。

Stage 2D 完成后停止。

---

# Stage 3 — Entity Resolution + 中英文 Alignment

> 建议：新会话。
> 此阶段不要读全部 Evidence，只按 topic / candidate 分批查询。

---

## PROMPT — STAGE 3

继续规则知识库项目。

首先读取：

```text
workspace/README_STATE.md
```

确认 Stage 2A–2D 的完成状态。

如果 Extraction 尚有 failed source，不要假装数据完整。

本阶段目标：

1. Card / Object Entity Resolution
2. 中文 / 英文规则 Evidence Alignment
3. 对应版本识别

本阶段不进行最终 Canonical Rule 裁决。

### 1. Entity Resolution

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

把 FAQ / Evidence 中涉及的卡牌实体尽量挂到统一 card_id。

### 2. 中英文 Alignment

不要一次读取全部中文 + 英文 Evidence。

按以下任一方式分批：

- topic
- section
- rule number
- rule_id_candidate
- semantic candidate

对疑似对应 Evidence 判断：

```text
equivalent
translation_difference
missing_information
semantic_difference
actual_conflict_candidate
uncertain
```

### 3. 语言不是唯一优先级

不要简单执行：

```text
English > Chinese
```

应结合：

```text
版本关系
日期
语言
```

此阶段主要负责发现差异，不负责最终拍板。

### 4. 建立 Alignment Record

至少包含：

```text
alignment_id
evidence_a
evidence_b
relation
confidence
version_relation
notes
```

### 5. 高风险项

以下进入 manual_review candidate：

- 无法确定是否对应版本
- 中文比英文多出重要规则条件
- 英文明显旧于中文
- 两者无法同时成立
- 翻译差异可能改变触发条件 / timing / scope

### 完成条件

- 主要 Rule / FAQ Evidence 已有语言或实体对齐
- 无法对齐项目明确标记
- 不存在“默默忽略的另一语言来源”
- alignments 已写入 DB
- checkpoint 已更新

不要自动进入 Rule Reconciliation。

---

# Stage 4 — Rule Clustering + Reconciliation

> 建议：至少一个新会话。
> 如果规则很多，可以按 topic 分成多个 Stage 4 会话。

---

## PROMPT — STAGE 4

继续现有项目。

首先读取 checkpoint。

本阶段目标：

> 把 Evidence 聚类成稳定 Rule ID，并逐 Rule 生成 proposed canonical rule。

不要一次加载全部 Evidence。

### 1. Rule Clustering

根据：

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

建立稳定：

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

不要：

- 因中英文不同而创建两个 Rule ID
- 因关键词相似就错误合并不同规则

无法确定：

```text
needs_review
```

### 2. 逐 Rule Reconciliation

一次只处理一个 Rule ID 或一个很小的 Rule batch。

只查询：

> 当前 Rule 所需要的 Evidence。

不要把整库 Evidence dump 到 context。

判断 Evidence 关系：

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

### 3. 来源效力

Errata：

- 明确修正规则
- 仅修改其覆盖范围

FAQ / Ruling：

- 默认解释 / 补充 / 限定 / 例外 / example
- 只有明确改变旧规则时才作为 rule change

Rules：

- 基础规范来源

### 4. 版本 / 时间 / 语言

判断：

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

但旧英文不得机械覆盖明显更新中文。

### 5. FAQ 推导

如果从 FAQ 推出一般解释，必须：

```text
derived_from_faq = true
```

并保存：

- FAQ evidence_id
- 推导依据
- 推导范围
- confidence

不要把 derived interpretation 标成 official rule。

### 6. 输出

每个 Rule 写入：

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
```

建立 `rule_evidence` 链接。

### 7. 必须进入 Verification 的 Rule

标记：

```text
needs_verification = true
```

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

### 8. 完成条件

所有可聚类 Evidence：

- 已映射 Rule
- 或明确进入 unmapped/manual_review

所有 Rule：

- 有 proposed canonical rule
- 或 status = unresolved

不要偷偷忽略 Evidence。

最后更新 checkpoint。

---

# Stage 5 — Independent Verification

> 强烈建议：新会话。
> 这是有意利用“新 context”减少前一阶段结论对验证者的污染。

---

## PROMPT — STAGE 5

你正在执行规则知识库的 Independent Verification。

这是一个新的独立验证阶段。

不要默认相信 Stage 4 的结论。

首先读取：

```text
workspace/README_STATE.md
```

然后从数据库获取：

```text
needs_verification = true
```

的 Rule。

### 核心原则

Verification Agent 应重新检查关键原始 Evidence，而不是只阅读 Reconciliation 的解释。

对于每个 Rule：

1. 读取 proposed canonical rule
2. 获取相关 evidence_id
3. 回查关键原文
4. 检查版本 / 日期 / 语言
5. 检查 Errata
6. 检查 FAQ 是否被过度泛化
7. 检查 exception / scope
8. 独立判断结论是否被证据支持

### Verification Status

使用：

```text
verified
verified_with_changes
rejected
needs_review
```

### 特别检查

#### Errata

确认：

- 修改目标正确
- 修改范围没有扩大
- 未删除未被 Errata 修改的原规则部分

#### FAQ

确认：

- example 没有被错误泛化
- interpretation 与原规则兼容
- derived interpretation 范围没有超出来源

#### 中文 / 英文

确认：

- 是否真的是对应版本
- 是否存在时间差
- 英文优先规则是否被机械误用

#### 冲突

确认是否其实是：

- scope 不同
- version 不同
- exception
- clarification

而不是真冲突。

### 如果验证结论不同

不要简单选择 Stage 4 或 Stage 5。

记录：

```text
rule_id
stage4_conclusion
verification_conclusion
relevant_evidence
disagreement_reason
```

并进入：

```text
manual_review
```

除非证据能够明确解决。

### Context 策略

逐 Rule / 小 batch 验证。

验证完成后写 DB，然后释放当前 Evidence。

不要把所有高风险 Rule 同时放进 context。

### 完成条件

所有 needs_verification Rule 都有：

```text
verified / verified_with_changes / rejected / needs_review
```

不存在 pending verification。

更新 checkpoint。

不要直接继续 Final Build。

---

# Stage 6 — Final Build + Coverage Check

> 建议：最终新会话。

---

## PROMPT — STAGE 6

继续规则知识库项目。

这是最终构建阶段。

首先读取：

```text
workspace/README_STATE.md
workspace/progress.json
```

并检查数据库。

不要重新大规模读取 PDF。

本阶段主要从：

- verified rules
- reconciliations
- changes
- manual_review
- source metadata

生成最终产物。

只有必要的局部问题才回查原始 Evidence。

### 1. Coverage Check

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

同时检查：

- 是否有 source 未处理
- 是否有 failed task 未恢复
- 是否有 Errata 未应用
- 是否有 FAQ 未挂载
- 是否有 Evidence 未映射
- 是否有 Rule 无来源
- 是否有 inferred 被误写成 confirmed
- 是否有 FAQ 过度泛化
- 是否有 superseded rule 仍被作为当前规则
- 是否有 verification pending
- 是否有 manual_review 被擅自裁决

如果存在未处理 source：

不得声称任务完整完成。

### 2. 生成最终规范规则

输出：

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

清楚区分：

```text
官方规则
官方解释
模型推导
案例
例外
未解决
```

### 3. 机器可读知识库

生成：

```text
workspace/final/rules.db
```

或把经过清理的最终表导出到该数据库。

应支持根据：

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

### 4. 变更记录

生成：

```text
workspace/final/change_log.md
```

记录：

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

### 5. 待人工确认

生成：

```text
workspace/final/manual_review.md
```

每项至少：

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

不要隐藏不确定性。

### 6. Coverage Report

生成：

```text
workspace/final/coverage_report.md
```

至少包含：

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

### 7. 最终一致性检查

最后确认：

- `rules.md`
- `rules.db`
- `change_log.md`
- `manual_review.md`
- `coverage_report.md`

彼此数量和状态基本一致。

不能出现：

> `rules.md` 说已解决，但 `manual_review.md` 仍列为 unresolved。

### 8. 完成状态

如果所有预定流程完成，则：

```text
Current stage: COMPLETE
```

更新：

```text
README_STATE.md
progress.json
```

如果仍存在 manual_review，可以写：

```text
Pipeline complete with manual review items remaining.
```

这不等于失败。

但如果仍有未处理文档或 failed extraction，则不能标记完整完成。

---

# 通用新会话恢复 Prompt

如果任意阶段因为 context、Agent 中断、程序错误等原因中断，新建会话后可以先发送：

---

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

- 当前 stage
- completed tasks
- pending tasks
- failed tasks
- needs_review tasks
- 当前数据库 schema
- 下一步

不要重新执行已经 completed 的任务。

只恢复当前阶段尚未完成的最小任务集合。

不要一次读取全部历史数据。

所有正式结果继续写入 workspace。

在结束当前会话之前，必须更新：

```text
README_STATE.md
progress.json
```

如果当前会话上下文再次明显膨胀，则先 checkpoint，再停止继续扩展。

---

# Context Emergency Prompt

如果某个会话已经接近上下文上限，可以直接发送：

---

## PROMPT — CONTEXT EMERGENCY CHECKPOINT

当前会话上下文已经过长。

立即停止加载新的 PDF、Evidence 或大规模 Tool Output。

现在只执行 checkpoint：

1. 将当前所有尚未持久化但需要保留的正式结果写入 `workspace/`。
2. 更新 `workspace/rules_work.db`。
3. 更新当前 task 的 status。
4. 更新 `workspace/progress.json`。
5. 更新 `workspace/README_STATE.md`。
6. 在 README_STATE 中明确写出：
   - 当前 stage
   - 已完成内容
   - 尚未完成内容
   - failed / needs_review
   - 下一会话应该执行的具体下一步
7. 不继续新的分析阶段。
8. 不输出大段历史总结。

目标是让一个完全新的会话能够仅凭 workspace 继续任务。

---

# 推荐实际会话划分

如果资料量较大，推荐至少这样分：

```text
Session 01 → Stage 0
Session 02 → Stage 1

Session 03 → Stage 2A 中文 Rules
Session 04 → Stage 2B 英文 Rules
Session 05 → Stage 2C Errata
Session 06 → Stage 2D FAQ / Ruling

Session 07 → Stage 3 Entity + Alignment

Session 08 → Stage 4 Rule Clustering
Session 09 → Stage 4 Reconciliation Part 1
Session 10 → Stage 4 Reconciliation Part 2
...

Session N → Stage 5 Independent Verification

Final Session → Stage 6
```

Stage 2 和 Stage 4 如果仍然过大，可以继续拆更多新会话。

原则不是固定会话数量，而是：

> 一个会话只承担一个明确、可持久化、可恢复的工作单元。

最终系统能够处理的总资料规模不再受单个 Context Window 的直接限制。
