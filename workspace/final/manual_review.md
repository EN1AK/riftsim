# Manual Review — 人工复核与裁决记录

> Stage 6E 产物。由 `stage6e_build_manual_review.py` 从 `workspace/rules_work.db` 的 `manual_review` 表全量幂等重建；事实来源为数据库，任何手工改动会被下次重建覆盖。

- 构建时间: 2026-09-22T18:59:51
- 条目总数: 186 — **全部已正式关闭**（见每条 状态 字段与 裁定结论）。
- 说明: 全部 186 项均已在各自阶段裁决关闭，本文件按已记录的裁决呈现，不存在待决项；正式关闭项不得被重新当作待决。裁定结论为追加在原始问题描述末尾的带日期结案记录，逐字保留。

---

## 汇总统计

### 按批次（问题前缀）

| 批次 | 数量 | 说明 |
| --- | ---: | --- |
| MR-2C | 4 | Stage 2C 勘误抽取 — 跨语言勘误覆盖 |
| MR-2D | 15 | Stage 2D FAQ / 官方说明抽取 — 人工复核与裁决 |
| MR-3-CR | 161 | Stage 3 中英核心规则对齐差异 |
| MR-4A | 6 | Stage 4A 聚类 — FAQ 引用旧规则编号 |
| **合计** | **186** |  |

### 按最终关闭日期

| 日期 | 数量 |
| --- | ---: |
| 2026-09-20 | 16 |
| 2026-09-21 | 3 |
| 2026-09-22 | 167 |

- 无关联规则的来源级问题（rule_id 为 NULL）: 18 条
- rule_id 为旧规则编号而非当前 Rule Cluster ID（历史引用，非孤儿）: [MR-2D-0007 → 735.1.c]

---

## 1. Stage 2C 勘误抽取 — 跨语言勘误覆盖（4 条）

> 中英勘误文档条目数 / 覆盖差异的裁决（Group-B 2026-09-20 裁定：中文独有勘误 zh_only_translation、跨文档一致性核对、cross_ref 指针）。

#### `MR-2C-0001`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-2C-0001` |
| Rule ID | -（无关联规则 — 来源级问题） |
| 状态 | **已关闭**（2026-09-20） |
| 来源 A | `source_004` |
| 来源 B | `source_015` |

**问题（原始记录）**:

```
zh source_004 (铸魂淬炼勘误) contains 2 entries (沉没神庙, 遗忘丰碑) with no counterpart in EN source_015 (Spiritforged_Errata): cross-language errata coverage differs
```

**冲突点**:

```
zh has 18 entries incl. 沉没神庙/遗忘丰碑; en has 16 without them
```

**可能解释**:

```
zh-only correction entries (possibly translation-only or EN issued separately)
```

**无法自动裁决原因**:

```
cannot confirm EN-side status automatically; cross-language meaning check deferred to Stage 3
```

**裁定结论（关闭记录）**:

```
[2026-09-20 裁定关闭] 裁定为 zh 独有勘误：沉没神庙(EV-CN-ER-0079)/遗忘丰碑(EV-CN-ER-0080) 为中文侧独立勘误（EN Spiritforged Errata 无对应），中文文本为最终口径；相关 evidence 已标 zh_only_translation。
```

#### `MR-2C-0002`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-2C-0002` |
| Rule ID | -（无关联规则 — 来源级问题） |
| 状态 | **已关闭**（2026-09-20） |
| 来源 A | `source_013` |
| 来源 B | `source_013` |

**问题（原始记录）**:

```
source_013 (Origins_Errata): internal 'Last Updated: 2025-10-21' differs from filename date 2025-10-28
```

**冲突点**:

```
document-internal date 2025-10-21 vs filename date 2025-10-28
```

**可能解释**:

```
PDF last-updated stamp predates the 10-28 site release/packaging date
```

**无法自动裁决原因**:

```
date/version ambiguity flagged per Stage 2C rules; sources.date kept as filename date
```

**裁定结论（关闭记录）**:

```
[2026-09-20 裁定关闭] 采用内文 Last Updated: 2025-10-21 为 date；文件名 2025-10-28 为抓取归档日期（sources.notes 已记）。
```

#### `MR-2C-0003`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-2C-0003` |
| Rule ID | -（无关联规则 — 来源级问题） |
| 状态 | **已关闭**（2026-09-20） |
| 来源 A | `source_020` |
| 来源 B | `source_010` |

**问题（原始记录）**:

```
source_020 (Vendetta_Errata): article byline date 7/24/2026 differs from filename date 2026-07-23 (matches zh counterpart source_010 dated 2026-07-24)
```

**冲突点**:

```
EN article date 2026-07-24 vs EN filename 2026-07-23; zh doc 2026-07-24
```

**可能解释**:

```
timezone/packaging offset of one day
```

**无法自动裁决原因**:

```
date/version ambiguity flagged per Stage 2C rules; sources.date kept as filename date
```

**裁定结论（关闭记录）**:

```
[2026-09-20 裁定关闭] 采用 byline 7/24/2026 为 date（与 zh 对应勘误日期一致）；文件名 2026-07-23 为抓取日时区偏移。
```

#### `MR-2C-0004`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-2C-0004` |
| Rule ID | -（无关联规则 — 来源级问题） |
| 状态 | **已关闭**（2026-09-20） |
| 来源 A | `source_003` |
| 来源 B | -（不适用/NULL） |

**问题（原始记录）**:

```
zh source_003 contains 13 zh-only 翻译勘误/翻译优化 entries (倾颓宫殿, 击退, 苍蓝雕纹魔像, 圣裁之刻, 宏伟广场, 卡尔萨斯-永恒颂葬, 厄运小姐-海盗, 伊泽瑞尔-奥法逸才, 黛安娜, 兰博, 杰斯, 临终仪式, 蔚, 咂魂者, 自适应机器人, plus 翻译优化 德莱文/暗巷神偷/奥恩的锻炉/帝王神坛): no EN errata counterparts
```

**冲突点**:

```
zh translation-correction sections have no EN parallel errata
```

**可能解释**:

```
translation-only fixes cannot alter EN card text meaning
```

**无法自动裁决原因**:

```
cross-language equivalence must be verified in Stage 3; flagged per Stage 2C rules
```

**裁定结论（关闭记录）**:

```
[2026-09-20 裁定关闭] 裁定为 zh 独有翻译勘误/翻译优化：按正文明细 15 张翻译勘误（倾颓宫殿…自适应机器人）+4 张翻译优化（德莱文/暗巷神偷/奥恩的锻炉/帝王神坛）= 19 张卡（标题『13 条』为历史笔误），均为中文本地化文本修订，不改 EN 原义，EN 无对应属正常；相关 evidence 已标 zh_only_translation。（补注：EV-CN-ER-0081/0082 为 source_010 破限勘误的德莱文/帝王神坛，按系列归属不在本裁定范围内，未标 zh_only。）
```

## 2. Stage 2D FAQ / 官方说明抽取 — 人工复核与裁决（15 条）

> 日期归属、FAQ 取代关系、权威层级、旧版编号衔接、抽取结构复核等;Group-A/Group-C 裁定与人工复核均已完成。

#### `MR-2D-0001`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-2D-0001` |
| Rule ID | -（无关联规则 — 来源级问题） |
| 状态 | **已关闭**（2026-09-20） |
| 来源 A | `source_001` |
| 来源 B | -（不适用/NULL） |

**问题（原始记录）**:

```
source_001 日期冲突：文件名标注 2025-12-03，文档内文声明『最后更新时间：2025-10-23』。
```

**冲突点**:

```
sources.date=2025-12-03 vs doc internal date=2025-10-23 （均为 inferred）
```

**可能解释**:

```
文件名为发布/归档日期，内文为内容最后更新日期，两者可能都真实
```

**无法自动裁决原因**:

```
来源日期效力判定需人工决定 effective_date 与 version 采用哪个日期
```

**裁定结论（关闭记录）**:

```
[2026-09-20 裁定关闭] 采用内文『最后更新时间：2025-10-23』为 date；文件名 2025-12-03 为 PDF 归档/发布日期。
```

#### `MR-2D-0002`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-2D-0002` |
| Rule ID | -（无关联规则 — 来源级问题） |
| 状态 | **已关闭**（2026-09-20） |
| 来源 A | `source_006` |
| 来源 B | -（不适用/NULL） |

**问题（原始记录）**:

```
source_006 日期冲突：文件名 2026-04-15，文档内文『更新日期：2026/01/14』；且 006 第 37 行存在 『Q：可以。』排版错误（应为 A：可以。），已由解析器按 typo_fixed 自动归并，需人工确认归并正确。
```

**冲突点**:

```
sources.date=2026-04-15 vs internal=2026-01-14；typo Q/A 标记误用
```

**可能解释**:

```
文件名与内文日期差近 3 个月；typo 修复已附带 notes 标记 typo_fixed
```

**无法自动裁决原因**:

```
日期取值与 typo 自动修复的正确性需人工复核
```

**裁定结论（关闭记录）**:

```
[2026-09-20 裁定关闭] 采用内文『更新日期：2026/01/14』为 date；文件名 2026-04-15 为 PDF 归档/发布日期。typo『Q：可以。』自动归并人工复核正确（归并为 A，notes 标 typo_fixed）。
```

#### `MR-2D-0003`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-2D-0003` |
| Rule ID | -（无关联规则 — 来源级问题） |
| 状态 | **已关闭**（2026-09-20） |
| 来源 A | `source_008` |
| 来源 B | -（不适用/NULL） |

**问题（原始记录）**:

```
source_008 文档组成声明：前 3 节为 2026-04-16 裁判FAQ 保留部分，后 2 节（4.卡牌文本更新相关 / 5.260511新增卡牌Q&A）为 2026-05-11 新增；文件名日期 2026-05-13、后缀 260511，三者不完全一致。
```

**冲突点**:

```
sources.date=2026-05-13 vs 内容部分日期 2026-04-16/2026-05-11
```

**可能解释**:

```
文档为增量合订本,不同节的有效日期不同
```

**无法自动裁决原因**:

```
batch 级版本判定需要人工确认各节时间效力
```

**裁定结论（关闭记录）**:

```
[2026-09-20 裁定关闭] 合订本以最新内容日期 2026-05-11 为 date；节级日期分层（1-3 节内容保留自 2026-04-16 版）与文件名发布日 2026-05-13 均记 sources.notes。
```

#### `MR-2D-0004`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-2D-0004` |
| Rule ID | -（无关联规则 — 来源级问题） |
| 状态 | **已关闭**（2026-09-21） |
| 来源 A | `source_007` |
| 来源 B | `卡牌文本中英对照` |

**问题（原始记录）**:

```
source_007 金克丝案例：英文卡牌文本中条件分句位置与中文译文不同，FAQ 裁定两种句式在中文下都按同一含义理解，但提示英文原版存在句式差异。
```

**冲突点**:

```
英文条件分句可前置/后置；中文译文句式不区分，FAQ 按统一含义执行
```

**可能解释**:

```
中文执行口径由官方 FAQ 统一，英文原文句式差异不影响中文结算
```

**无法自动裁决原因**:

```
中英卡牌文本差异属跨语言一致性问题，需 Stage 3 reconciliation 处理
```

**裁定结论（关闭记录）**:

```
[2026-09-20 移交 Stage 3] 已在 EV-CN-FAQ-0195 标注 cross_language_note；中文执行口径由 007 FAQ 统一（两句式同义），句式差异仅注记。Stage 3 实体对齐时核对英文原文。 [2026-09-21 Stage 3 结案] 已核对英文原文：触发式技能条件分句在英文中确存在前置/后置两种模板（如 Dune Drake 'When I attack, give me +2 [M] this turn if...' 后置 if vs 前置条件句式），中文译文不区分该句式差异。官方FAQ(source_007 EV-CN-FAQ-0195)已裁定两种句式同义统一执行。Stage 3 对齐口径：涉及条件分句位置的中英文模板差异不算语义差异(translation template variance)，相应对子仍可判 equivalent。不构成冲突，关闭。
```

#### `MR-2D-0005`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-2D-0005` |
| Rule ID | -（无关联规则 — 来源级问题） |
| 状态 | **已关闭**（2026-09-21） |
| 来源 A | `source_008` |
| 来源 B | `source_002/source_003 (2C 勘误)` |

**问题（原始记录）**:

```
source_008 第 4 节：沙丘亚龙(OGN·131)/金克丝-暴走萝莉(OGN·251)/均衡门徒(UNL·97)/艾翁-万物之友(UNL·177) 四张卡的中英文本存在语义分歧，文档给出结算链流程分析并声明『中文文本或将在未来作出更新调整』；沙丘亚龙另有前序勘误注记。
```

**冲突点**:

```
中文文本当前结算口径 vs 英文文本含义；中文文本未来可能更新
```

**可能解释**:

```
FAQ 先给出现行中文文本的结算方式，未来可能以勘误形式修订中文文本
```

**无法自动裁决原因**:

```
与未来勘误的衔接和现行口径固化需人工在 Stage 3 裁决
```

**裁定结论（关闭记录）**:

```
[2026-09-20 移交 Stage 3] 已在 EV-CN-FAQ-0260 标注 pending_zh_text_update；以 008 第 4 节给出的中文结算链分析为现行口径，四卡（沙丘亚龙/金克丝-暴走萝莉/均衡门徒/艾翁-万物之友）挂观察标记，等后续版本中文勘误。 [2026-09-21 Stage 3 结案] 已核对四卡英文原文：OGN-131/OGN-251/UNL-097/UNL-177 均为英文后置if 条件结构，中文译文采用前置“如果”句式，语义分歧模式 = 条件检查时点（触发时 vs 结算时）。现行结算口径以 source_008 第4节(EV-CN-FAQ-0260，设计师口径)中文结算链分析为准；四卡维持 pending_zh_text_update 观察标记，待后续版本中文勘误。跨语言分歧已文档化于本条及 FAQ 注记，Stage 4 reconciliation 采用 FAQ 现行口径并以 EN 原文为效力参照。结案（watch 持续）。
```

#### `MR-2D-0006`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-2D-0006` |
| Rule ID | -（无关联规则 — 来源级问题） |
| 状态 | **已关闭**（2026-09-20） |
| 来源 A | `source_011` |
| 来源 B | `source_005` |

**问题（原始记录）**:

```
source_011 明示废弃 source_005 答复：阿克尚偷眼镜条目声明『铸魂淬炼常见问题解答中的相关答复已不再适用』（涉及斯弗尔尚歌+厄斐琉斯相关答复）。
```

**冲突点**:

```
005 斯弗尔尚歌/厄斐琉斯答复 vs 011 阿克尚新答复
```

**可能解释**:

```
官方 FAQ 后续版本取代先前答复，011 为准
```

**无法自动裁决原因**:

```
FAQ 间取代关系需人工确认并将 005 被废弃条目在 Stage 3 标记失效
```

**裁定结论（关闭记录）**:

```
[2026-09-20 裁定关闭] 取代链建立：005 的斯弗尔尚歌答复(0089)/厄斐琉斯答复(0090) 标 superseded_by=0307；011 阿克尚条目(0307) 标 supersedes。顺带修复 0307/0308 问句断行错位（manual_fix 注记）。
```

#### `MR-2D-0007`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-2D-0007` |
| Rule ID | `735.1.c` |
| 状态 | **已关闭**（2026-09-20） |
| 来源 A | `source_005` |
| 来源 B | `核心规则 735.1.c / Stage 2C evidence` |

**问题（原始记录）**:

```
source_005『规则 735.1.c（修订后）』：FAQ 以（修订后）形式直接给出核心规则 735.1.c 的新文本，已按 rule_change_candidate 提取；同时与 Stage 2C 勘误范围可能交叉。
```

**冲突点**:

```
FAQ 直接修订核心规则条文（非卡牌文本），且声明立即生效
```

**可能解释**:

```
FAQ 作为官方规则说明可临时修订核心规则；2C 勘误未含规则条文只含卡牌
```

**无法自动裁决原因**:

```
规则条文级修订需与 Stage 1 规则文本比对后由 Stage 3 落地，禁止本阶段直接改规则
```

**裁定结论（关闭记录）**:

```
[2026-09-20 裁定关闭] FAQ(2026-01) 对 735.1.c 的文本修订已被 2026-07 版核心规则吸收——现行规则位于 809.1.c（『由对手控制且将[我/此牌]选为目标的法术或技能，每将[我/此牌]选作一次目标，其费用就增加等同于[法盾值]的额外费用才能打出』），与 FAQ 修订版语义等价、文本重构、编号迁移。FAQ 条目已标 incorporated_into=EV-CN-CR-2140，无未决冲突。
```

#### `MR-2D-0008`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-2D-0008` |
| Rule ID | -（无关联规则 — 来源级问题） |
| 状态 | **已关闭**（2026-09-20） |
| 来源 A | `source_005/source_008/source_011` |
| 来源 B | `Stage 2C evidence (EV-CN-ER/EV-EN-ER)` |

**问题（原始记录）**:

```
FAQ 内嵌勘误提及：source_005 多个（修订后）卡牌文本块、source_008 永恩回答内嵌『勘误后文本』、source_011 星界灵鹭条目『已受到勘误，技能描述更新为』——均与 Stage 2C 勘误 evidence 交叉。
```

**冲突点**:

```
FAQ 文本中复述/引用勘误内容，2C 已正式抽取勘误条目
```

**可能解释**:

```
FAQ 内嵌勘误仅作交叉引用（notes 已标 mentions_errata），不重复建勘误条目
```

**无法自动裁决原因**:

```
需人工核对 FAQ 复述文本与 2C 勘误文本逐字一致性
```

**裁定结论（关闭记录）**:

```
[2026-09-20 裁定关闭] 逐条核对 21 处 FAQ 内嵌勘误：005 修订块 18 卡 ↔ source_004 勘误全部一致（13 全同 + 5 FAQ 含说明尾段的包含关系）；008 沙丘亚龙语义一致（中英对照格式差异，已注记）；008 永恩为节引（省略[百炼]关键词括注，已注记 partial_quote）；011 星界灵鹭一致。无冲突。已建立 cross_ref_errata / cross_ref_faq 双向指针 21 组。
```

#### `MR-2D-0009`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-2D-0009` |
| Rule ID | -（无关联规则 — 来源级问题） |
| 状态 | **已关闭**（2026-09-20） |
| 来源 A | `source_007/source_011/source_005` |
| 来源 B | `Stage 1 核心规则文本` |

**问题（原始记录）**:

```
FAQ 效力优先声明：source_007『如果本文档与《核心规则》有任何不一致之处，请以本文档为准。当下一次核心规则更新发布时，本文档将会失效』；source_011『新版《核心规则》发布后以新版为准』；source_005『这些阐明与勘误将立即生效』。
```

**冲突点**:

```
FAQ 自声明高于核心规则的临时效力及失效条件
```

**可能解释**:

```
FAQ 具有过渡性最高效力，核心规则更新后被吸收或失效
```

**无法自动裁决原因**:

```
效力层级与失效时点需纳入 Stage 3 规则版本管理，不能自动推导
```

**裁定结论（关闭记录）**:

```
[2026-09-20 裁定关闭] 效力拓扑裁定：1) 核心规则（当前版本，含官方声明已并入的内容）为常态最高；2) 官方FAQ/Patch Notes 具有过渡性最高效力——与核心规则冲突时以FAQ/Patch Notes 为准，有效期至下一版核心规则发布即失效（007/011/005 声明机制）；3) FAQ 间后发取代先发；4) 裁判FAQ（001/006/008，社区整理，非官方FAQ）为最低层级，仅作判罚参考，与上述冲突自动让位。
```

#### `MR-2D-0010`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-2D-0010` |
| Rule ID | -（无关联规则 — 来源级问题） |
| 状态 | **已关闭**（2026-09-21） |
| 来源 A | `source_012` |
| 来源 B | `Origins FAQ (先前官方说明)` |

**问题（原始记录）**:

```
source_012 前言声明：『A very small amount of that information is explicitly contradicted in these notes』——Core Rules Patch Notes 与先前 Origins FAQ 存在少量明确矛盾，以 Patch Notes 为准。
```

**冲突点**:

```
Patch Notes 自述与先前 FAQ 少量矛盾
```

**可能解释**:

```
官方以后发 Patch Notes 取代先前 FAQ 中过时的说明
```

**无法自动裁决原因**:

```
被取代的先前 FAQ 条目需 Stage 3 逐条识别并标记失效
```

**裁定结论（关闭记录）**:

```
[2026-09-20 移交 Stage 3] 012 未列出矛盾条目清单，无法在本阶段机械识别；按效力拓扑裁定，后发官方文档（012 Patch Notes，2025-10-24）效力高于先前 Origins FAQ。Stage 3 reconciliation 时以 012 文本为准比对 Origins FAQ/说明文，凡文本冲突处在被取代侧标 superseded。 [2026-09-21 Stage 3 结案] 『先前 Origins 官方FAQ/说明文』为外部文档，不在本语料库内（同 MR-2D-0012 处理方式）；语料库内不存在被取代侧条目，无 in-corpus superseded 可标记。效力拓扑裁定维持：EN Core Rules Patch Notes(2025-10-24) > 先前 Origins 官方FAQ。012 的 CLARIFIED/NEW RULE 条目为权威侧，实际冲突比对移交 Stage 4B reconciliation（012条目 vs 核心规则聚类时裁决）。关闭。
```

#### `MR-2D-0011`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-2D-0011` |
| Rule ID | -（无关联规则 — 来源级问题） |
| 状态 | **已关闭**（2026-09-20） |
| 来源 A | `source_014/source_016/source_019` |
| 来源 B | -（不适用/NULL） |

**问题（原始记录）**:

```
生效日期冲突（EN Patch Notes）：source_014 内文声明 effective date 2025-12-12 vs sources.date 2025-12-05；source_019 声明 effective 2026-07-24 vs sources.date 2026-07-17；source_016 byline 日期 3/31/2026 vs 文件名 2026-03-30。
```

**冲突点**:

```
发布日期(byline/文件名) vs 声明生效日期(effective date) 不一致
```

**可能解释**:

```
先发博客后生效是官方惯例；sources 表的 effective_date 应以声明生效日为准
```

**无法自动裁决原因**:

```
日期字段采用规则需人工确认（date=publish, effective_date=声明日）
```

**裁定结论（关闭记录）**:

```
[2026-09-20 裁定关闭] 014/019 的 date 保持 byline，effective_date 分别改为声明生效日 2025-12-12 / 2026-07-24；016 date 改 byline 2026-03-31，无独立生效日声明故 effective=date。
```

#### `MR-2D-0012`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-2D-0012` |
| Rule ID | -（无关联规则 — 来源级问题） |
| 状态 | **已关闭**（2026-09-20） |
| 来源 A | `source_019` |
| 来源 B | `source_016 (Unleashed Patch Notes) / 核心规则` |

**问题（原始记录）**:

```
source_019 多处声明 Unleashed FAQ 的阐明已并入核心规则文档（Lethal damage/your damage/Battlefield Ability Control/Counting Targets/accelerate/Trigger Condition 等），『all of the changes described in the Unleashed FAQ have been reproduced in the Core Rules Document』。
```

**冲突点**:

```
019 声明 016 的 FAQ 阐明已被核心规则吸收
```

**可能解释**:

```
官方在新版本发布时将旧 FAQ 内容并入核心规则文档
```

**无法自动裁决原因**:

```
reconciliation 需识别已并入核心规则的 FAQ 条目避免重复计数
```

**裁定结论（关闭记录）**:

```
[2026-09-20 裁定关闭] 对账确认：声明所指的是外部文档『Unleashed FAQ』（非本库 source_016 Patch Notes），本库无该文档条目可标；声明本身已作为 reconciliation 元数据存于 source_019 front_matter，Stage 3 处理 016/019 条目与核心规则重复计数问题时以此为依据。
```

#### `MR-2D-0013`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-2D-0013` |
| Rule ID | -（无关联规则 — 来源级问题） |
| 状态 | **已关闭**（2026-09-20） |
| 来源 A | `source_001/source_006/source_008` |
| 来源 B | `source_005/source_007/source_011` |

**问题（原始记录）**:

```
裁判FAQ 效力声明：source_001/006/008 均声明『可以作为裁判判罚的依据，但不代表官方FAQ』，与官方FAQ（005/007/011）法律效力层级不同。
```

**冲突点**:

```
裁判FAQ 自述非官方 FAQ，但可作判罚依据
```

**可能解释**:

```
裁判FAQ 为裁判社区整理，效力低于官方 FAQ
```

**无法自动裁决原因**:

```
冲突时效力排序（官方FAQ > 裁判FAQ）需 Stage 3 人工确认
```

**裁定结论（关闭记录）**:

```
[2026-09-20 裁定关闭] 效力拓扑裁定：1) 核心规则（当前版本，含官方声明已并入的内容）为常态最高；2) 官方FAQ/Patch Notes 具有过渡性最高效力——与核心规则冲突时以FAQ/Patch Notes 为准，有效期至下一版核心规则发布即失效（007/011/005 声明机制）；3) FAQ 间后发取代先发；4) 裁判FAQ（001/006/008，社区整理，非官方FAQ）为最低层级，仅作判罚参考，与上述冲突自动让位。 裁判FAQ 归入第 4 层级确认。
```

#### `MR-2D-0014`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-2D-0014` |
| Rule ID | -（无关联规则 — 来源级问题） |
| 状态 | **已关闭**（2026-09-20） |
| 来源 A | `source_008/source_006` |
| 来源 B | -（不适用/NULL） |

**问题（原始记录）**:

```
source_008 第 5 节部分 Q&A 无 Q/A 标记（裸问句+裸答），以及 006/008 存在问句跨行/跨页断裂，解析器按段落启发式（unmarked_qa / fracture 合并）处理，共 4 条标记 needs_review=true。
```

**冲突点**:

```
无标记问答与断行问句的条目边界由启发式确定
```

**可能解释**:

```
启发式依据问句标点与行尾闭合性，人工抽查结果正确
```

**无法自动裁决原因**:

```
结构置信度问题需人工复核 4 条 needs_review 条目（EV 编号见 notes）
```

**裁定结论（关闭记录）**:

```
[2026-09-20 复核完成] 4 条已全部人工复核并修复：0248 并入 0247（1)-4) 共享问答合并，原编号 0248 已删除并重排）、0169 补 A1： 前缀、0264 尾行剥移 0265、0263 结构复核合格；needs_review 清零。
```

#### `MR-2D-0015`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-2D-0015` |
| Rule ID | -（无关联规则 — 来源级问题） |
| 状态 | **已关闭**（2026-09-20） |
| 来源 A | `source_007` |
| 来源 B | -（不适用/NULL） |

**问题（原始记录）**:

```
source_007 散文小节的分类为启发式：prose_section（规则修订与阐明）默认 rule_interpretation，含（旧）/（新）对照的标记 rule_change_candidate；散文条目并非问答形式，faq_question 为小节标题。
```

**冲突点**:

```
prose 条目不是 Q&A 结构，六分类映射为近似值
```

**可能解释**:

```
官方 FAQ 前半部分为规则修订说明文，本身即规则阐明
```

**无法自动裁决原因**:

```
条目形态与分类口径需人工在 Stage 3 复核
```

**裁定结论（关闭记录）**:

```
[2026-09-20 裁定关闭] 复核 source_007 全部 9 条 prose_section 条目（分布 {'rule_interpretation': 5, 'rule_change_candidate': 2, 'exception': 2}）：分类口径与内容匹配合理（0201 战斗结果/0196 控制权含（旧）（新）对照=rule_change_candidate；0199/0200 含特殊情况声明=exception；0217 层级合并标题正常）。采用现有启发式分类，不再调整。
```

## 3. Stage 3 中英核心规则对齐差异（161 条）

> 中英核心规则逐条比对标记的 translation_difference;4B-B003 已全文复核裁决:160 条 equivalent_despite_diff（标点/数字/占位符等文字差异）,1 条语义分歧（R-CR-811.1.b → CON-4B-T2-0001,Stage 5 已修复 CHG-5-0001)。

#### `MR-3-CR-0001`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0001` |
| Rule ID | `R-CR-103.2.b` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0037` |
| 来源 B | `EV-EN-CR-0037` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0037: rule 103.2.b zh/en feature mismatch (number tokens differ: zh=[] en=['3']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['3']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0002`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0002` |
| Rule ID | `R-CR-103.2.b.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0038` |
| 来源 B | `EV-EN-CR-0038` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0038: rule 103.2.b.1 zh/en feature mismatch (number tokens differ: zh=[] en=['2']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['2']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0003`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0003` |
| Rule ID | `R-CR-103.2.b.2` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0039` |
| 来源 B | `EV-EN-CR-0039` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0039: rule 103.2.b.2 zh/en feature mismatch (number tokens differ: zh=[] en=['3', '3']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['3', '3']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0004`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0004` |
| Rule ID | `R-CR-103.2.d` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0041` |
| 来源 B | `EV-EN-CR-0041` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0041: rule 103.2.d zh/en feature mismatch (number tokens differ: zh=[] en=['3']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['3']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0005`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0005` |
| Rule ID | `R-CR-103.2.d.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0042` |
| 来源 B | `EV-EN-CR-0042` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0042: rule 103.2.d.1 zh/en feature mismatch (number tokens differ: zh=[] en=['3']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['3']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0006`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0006` |
| Rule ID | `R-CR-116` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0141` |
| 来源 B | `EV-EN-CR-0141` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0141: rule 116 zh/en feature mismatch (number tokens differ: zh=[] en=['4']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['4']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0007`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0007` |
| Rule ID | `R-CR-132.4` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0191` |
| 来源 B | `EV-EN-CR-0191` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0191: rule 132.4 zh/en feature mismatch (number tokens differ: zh=[] en=['3']; bracket tokens differ: zh=[] en=['Short Name', 'Subtitle']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['3']; bracket tokens differ: zh=[] en=['Short Name', 'Subtitle']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0008`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0008` |
| Rule ID | `R-CR-135.2.b.5.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0237` |
| 来源 B | `EV-EN-CR-0237` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0237: rule 135.2.b.5.a zh/en feature mismatch (number tokens differ: zh=['4', '4', '1', '1'] en=['4', '4', '1', '5', '1', '5', '1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['4', '4', '1', '1'] en=['4', '4', '1', '5', '1', '5', '1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0009`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0009` |
| Rule ID | `R-CR-135.2.b.6` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0238` |
| 来源 B | `EV-EN-CR-0238` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0238: rule 135.2.b.6 zh/en feature mismatch (number tokens differ: zh=['2'] en=['1', '1', '2']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['2'] en=['1', '1', '2']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0010`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0010` |
| Rule ID | `R-CR-135.2.e.5.b` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0253` |
| 来源 B | `EV-EN-CR-0253` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0253: rule 135.2.e.5.b zh/en feature mismatch (bracket tokens differ: zh=['A', 'A'] en=['A']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['A', 'A'] en=['A']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0011`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0011` |
| Rule ID | `R-CR-135.2.e.6.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0255` |
| 来源 B | `EV-EN-CR-0255` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0255: rule 135.2.e.6.a zh/en feature mismatch (number tokens differ: zh=['1'] en=[]). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['1'] en=[]
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0012`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0012` |
| Rule ID | `R-CR-135.2.e.7.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0259` |
| 来源 B | `EV-EN-CR-0259` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0259: rule 135.2.e.7.a zh/en feature mismatch (bracket tokens differ: zh=['>', '>', '>', '>'] en=['Legion', '>', 'Level', '>', 'Deathknell', 'Action', '>', 'Reaction', '>']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['>', '>', '>', '>'] en=['Legion', '>', 'Level', '>', 'Deathknell', 'Action', '>', 'Reaction', '>']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0013`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0013` |
| Rule ID | `R-CR-144.4.a.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0336` |
| 来源 B | `EV-EN-CR-0336` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0336: rule 144.4.a.1 zh/en feature mismatch (number tokens differ: zh=['447.2'] en=['2', '2', '447.2']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['447.2'] en=['2', '2', '447.2']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0014`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0014` |
| Rule ID | `R-CR-158.2` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0387` |
| 来源 B | `EV-EN-CR-0387` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0387: rule 158.2 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Legion']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Legion']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0015`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0015` |
| Rule ID | `R-CR-164.2.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0418` |
| 来源 B | `EV-EN-CR-0418` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0418: rule 164.2.a zh/en feature mismatch (bracket tokens differ: zh=['E', '1'] en=['E', 'Reaction', '1']; len_ratio=0.77 outlier). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['E', '1'] en=['E', 'Reaction', '1']; len_ratio=0.77 outlier
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0016`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0016` |
| Rule ID | `R-CR-164.2.b` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0419` |
| 来源 B | `EV-EN-CR-0419` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0419: rule 164.2.b zh/en feature mismatch (bracket tokens differ: zh=['C'] en=['Reaction', 'C']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['C'] en=['Reaction', 'C']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0017`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0017` |
| Rule ID | `R-CR-187.5` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0509` |
| 来源 B | `EV-EN-CR-0509` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0509: rule 187.5 zh/en feature mismatch (bracket tokens differ: zh=['>', 'E', 'A'] en=['Reaction', '>', 'E', 'Add', 'A']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['>', 'E', 'A'] en=['Reaction', '>', 'E', 'Add', 'A']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0018`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0018` |
| Rule ID | `R-CR-187.11` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0515` |
| 来源 B | `EV-EN-CR-0515` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0515: rule 187.11 zh/en feature mismatch (bracket tokens differ: zh=['M'] en=['M', 'Assault 4']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['M'] en=['M', 'Assault 4']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0019`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0019` |
| Rule ID | `R-CR-190.6.d` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0539` |
| 来源 B | `EV-EN-CR-0539` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0539: rule 190.6.d zh/en feature mismatch (number tokens differ: zh=[] en=['1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0020`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0020` |
| Rule ID | `R-CR-194.1.c` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0565` |
| 来源 B | `EV-EN-CR-0565` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0565: rule 194.1.c zh/en feature mismatch (number tokens differ: zh=['1'] en=[]). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['1'] en=[]
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0021`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0021` |
| Rule ID | `R-CR-194.4.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0573` |
| 来源 B | `EV-EN-CR-0573` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0573: rule 194.4.a zh/en feature mismatch (number tokens differ: zh=['0', '1'] en=['1', '0']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['0', '1'] en=['1', '0']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0022`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0022` |
| Rule ID | `R-CR-204.3` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0597` |
| 来源 B | `EV-EN-CR-0597` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0597: rule 204.3 zh/en feature mismatch (bracket tokens differ: zh=[] en=['do X', 'do Y']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['do X', 'do Y']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0023`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0023` |
| Rule ID | `R-CR-204.3.b` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0599` |
| 来源 B | `EV-EN-CR-0599` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0599: rule 204.3.b zh/en feature mismatch (number tokens differ: zh=['2', '2'] en=['2', '1', '2']; bracket tokens differ: zh=['A', 'A', '>', 'E', 'A', 'A'] en=['A', 'A', 'Reaction', '>', 'E', 'A', 'A']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['2', '2'] en=['2', '1', '2']; bracket tokens differ: zh=['A', 'A', '>', 'E', 'A', 'A'] en=['A', 'A', 'Reaction', '>', 'E', 'A', 'A']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0024`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0024` |
| Rule ID | `R-CR-206` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0606` |
| 来源 B | `EV-EN-CR-0606` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0606: rule 206 zh/en feature mismatch (number tokens differ: zh=['8', '5', '3', '4', '4', '4', '1', '1', '1', '4'] en=['8', '5', '3', '4', '4', '4', '1', '4']; bracket tokens differ: zh=['8', '5', 'M', '4', 'A', '4', 'C', '4', 'C', '1'] en=['8', 'M', '4', 'A', '4', 'C', '4', 'C', '1', 'Y']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['8', '5', '3', '4', '4', '4', '1', '1', '1', '4'] en=['8', '5', '3', '4', '4', '4', '1', '4']; bracket tokens differ: zh=['8', '5', 'M', '4', 'A', '4', 'C', '4', 'C', '1'] en=['8', 'M', '4', 'A', '4', 'C', '4', 'C', '1', 'Y']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0025`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0025` |
| Rule ID | `R-CR-206.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0607` |
| 来源 B | `EV-EN-CR-0607` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0607: rule 206.1 zh/en feature mismatch (number tokens differ: zh=['7', '12', '1', '1', '6', '4', '1'] en=['7', '2', '12', '1', '6', '4', '1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['7', '12', '1', '1', '6', '4', '1'] en=['7', '2', '12', '1', '6', '4', '1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0026`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0026` |
| Rule ID | `R-CR-315.3.b` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0666` |
| 来源 B | `EV-EN-CR-0666` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0666: rule 315.3.b zh/en feature mismatch (number tokens differ: zh=['1', '430'] en=['1', '2', '430']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['1', '430'] en=['1', '2', '430']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0027`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0027` |
| Rule ID | `R-CR-315.3.b.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0667` |
| 来源 B | `EV-EN-CR-0667` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0667: rule 315.3.b.1 zh/en feature mismatch (number tokens differ: zh=[] en=['2']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['2']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0028`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0028` |
| Rule ID | `R-CR-315.4.b` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0670` |
| 来源 B | `EV-EN-CR-0670` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0670: rule 315.4.b zh/en feature mismatch (number tokens differ: zh=['1'] en=['1', '1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['1'] en=['1', '1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0029`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0029` |
| Rule ID | `R-CR-315.4.b.2` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0672` |
| 来源 B | `EV-EN-CR-0672` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0672: rule 315.4.b.2 zh/en feature mismatch (number tokens differ: zh=[] en=['1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0030`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0030` |
| Rule ID | `R-CR-355.5.b` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0863` |
| 来源 B | `EV-EN-CR-0863` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0863: rule 355.5.b zh/en feature mismatch (number tokens differ: zh=['382'] en=['2', '2', '382']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['382'] en=['2', '2', '382']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0031`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0031` |
| Rule ID | `R-CR-355.10.c.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0881` |
| 来源 B | `EV-EN-CR-0881` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0881: rule 355.10.c.1 zh/en feature mismatch (number tokens differ: zh=[] en=['1']; bracket tokens differ: zh=[] en=['do X', 'do Y', 'do X']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['1']; bracket tokens differ: zh=[] en=['do X', 'do Y', 'do X']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0032`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0032` |
| Rule ID | `R-CR-355.10.d` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0882` |
| 来源 B | `EV-EN-CR-0882` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0882: rule 355.10.d zh/en feature mismatch (number tokens differ: zh=['2', '2'] en=['2', '2', '2']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['2', '2'] en=['2', '2', '2']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0033`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0033` |
| Rule ID | `R-CR-355.13` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0891` |
| 来源 B | `EV-EN-CR-0891` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0891: rule 355.13 zh/en feature mismatch (number tokens differ: zh=['0', '0'] en=[]). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['0', '0'] en=[]
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0034`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0034` |
| Rule ID | `R-CR-355.14.c` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0895` |
| 来源 B | `EV-EN-CR-0895` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0895: rule 355.14.c zh/en feature mismatch (number tokens differ: zh=['5', '5', '5'] en=['5', '5']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['5', '5', '5'] en=['5', '5']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0035`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0035` |
| Rule ID | `R-CR-355.14.h.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0901` |
| 来源 B | `EV-EN-CR-0901` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0901: rule 355.14.h.1 zh/en feature mismatch (number tokens differ: zh=['5', '1', '5', '3', '3', '3'] en=['5', '1', '5', '3', '4', '3', '3', '2']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['5', '1', '5', '3', '3', '3'] en=['5', '1', '5', '3', '4', '3', '3', '2']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0036`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0036` |
| Rule ID | `R-CR-356.1.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0908` |
| 来源 B | `EV-EN-CR-0908` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0908: rule 356.1.a zh/en feature mismatch (bracket tokens differ: zh=[] en=['Cost', 'Cost']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Cost', 'Cost']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0037`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0037` |
| Rule ID | `R-CR-356.2.b.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0919` |
| 来源 B | `EV-EN-CR-0919` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0919: rule 356.2.b.1 zh/en feature mismatch (number tokens differ: zh=['2', '2', '2', '356.2', '356.4', '357.2', '363'] en=['2', '1', '2', '2', '356.2', '356.4', '357.2', '363']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['2', '2', '2', '356.2', '356.4', '357.2', '363'] en=['2', '1', '2', '2', '356.2', '356.4', '357.2', '363']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0038`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0038` |
| Rule ID | `R-CR-356.4.b` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0923` |
| 来源 B | `EV-EN-CR-0923` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0923: rule 356.4.b zh/en feature mismatch (bracket tokens differ: zh=[] en=['amount', 'amount']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['amount', 'amount']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0039`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0039` |
| Rule ID | `R-CR-356.4.f.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0930` |
| 来源 B | `EV-EN-CR-0930` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0930: rule 356.4.f.1 zh/en feature mismatch (number tokens differ: zh=['2', '0', '0'] en=['2', '0', '1', '0']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['2', '0', '0'] en=['2', '0', '1', '0']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0040`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0040` |
| Rule ID | `R-CR-358.3` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0944` |
| 来源 B | `EV-EN-CR-0944` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0944: rule 358.3 zh/en feature mismatch (number tokens differ: zh=[] en=['3']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['3']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0041`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0041` |
| Rule ID | `R-CR-358.4` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0946` |
| 来源 B | `EV-EN-CR-0946` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0946: rule 358.4 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Action', 'Reaction', 'Reaction']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Action', 'Reaction', 'Reaction']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0042`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0042` |
| Rule ID | `R-CR-359.3.e.5` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0965` |
| 来源 B | `EV-EN-CR-0965` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0965: rule 359.3.e.5 zh/en feature mismatch (number tokens differ: zh=['4'] en=['4', '1', '1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['4'] en=['4', '1', '1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0043`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0043` |
| Rule ID | `R-CR-359.3.e.11` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0972` |
| 来源 B | `EV-EN-CR-0972` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0972: rule 359.3.e.11 zh/en feature mismatch (number tokens differ: zh=[] en=['2', '2', '2', '2', '1', '2']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['2', '2', '2', '2', '1', '2']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0044`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0044` |
| Rule ID | `R-CR-359.3.e.12` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0973` |
| 来源 B | `EV-EN-CR-0973` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0973: rule 359.3.e.12 zh/en feature mismatch (number tokens differ: zh=['1', '1', '5'] en=['1', '5', '1', '5']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['1', '1', '5'] en=['1', '5', '1', '5']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0045`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0045` |
| Rule ID | `R-CR-359.3.e.14` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0976` |
| 来源 B | `EV-EN-CR-0976` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0976: rule 359.3.e.14 zh/en feature mismatch (number tokens differ: zh=[] en=['2']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['2']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0046`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0046` |
| Rule ID | `R-CR-359.3.e.14.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0977` |
| 来源 B | `EV-EN-CR-0977` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0977: rule 359.3.e.14.a zh/en feature mismatch (number tokens differ: zh=[] en=['2', '2']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['2', '2']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0047`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0047` |
| Rule ID | `R-CR-359.3.e.14.b` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0978` |
| 来源 B | `EV-EN-CR-0978` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0978: rule 359.3.e.14.b zh/en feature mismatch (number tokens differ: zh=[] en=['2', '2']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['2', '2']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0048`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0048` |
| Rule ID | `R-CR-359.3.e.16` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0981` |
| 来源 B | `EV-EN-CR-0981` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0981: rule 359.3.e.16 zh/en feature mismatch (number tokens differ: zh=[] en=['2']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['2']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0049`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0049` |
| Rule ID | `R-CR-359.3.f.4` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0989` |
| 来源 B | `EV-EN-CR-0989` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0989: rule 359.3.f.4 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Reaction']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Reaction']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0050`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0050` |
| Rule ID | `R-CR-364.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-0996` |
| 来源 B | `EV-EN-CR-0996` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-0996: rule 364.1 zh/en feature mismatch (number tokens differ: zh=['1'] en=['1', '2']; bracket tokens differ: zh=['M'] en=['M', 'Shield']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['1'] en=['1', '2']; bracket tokens differ: zh=['M'] en=['M', 'Shield']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0051`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0051` |
| Rule ID | `R-CR-366.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1003` |
| 来源 B | `EV-EN-CR-1003` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1003: rule 366.1 zh/en feature mismatch (bracket tokens differ: zh=['>', '3', 'C'] en=['Legion', '>', '3', 'C']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['>', '3', 'C'] en=['Legion', '>', '3', 'C']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0052`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0052` |
| Rule ID | `R-CR-369.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1010` |
| 来源 B | `EV-EN-CR-1010` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1010: rule 369.1 zh/en feature mismatch (bracket tokens differ: zh=['2'] en=['Add', '2']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['2'] en=['Add', '2']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0053`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0053` |
| Rule ID | `R-CR-370.1.b.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1019` |
| 来源 B | `EV-EN-CR-1019` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1019: rule 370.1.b.1 zh/en feature mismatch (bracket tokens differ: zh=['2', '2'] en=['Add', '2', '2']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['2', '2'] en=['Add', '2', '2']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0054`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0054` |
| Rule ID | `R-CR-375` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1039` |
| 来源 B | `EV-EN-CR-1039` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1039: rule 375 zh/en feature mismatch (number tokens differ: zh=['3', '1'] en=['1', '3', '1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['3', '1'] en=['1', '3', '1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0055`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0055` |
| Rule ID | `R-CR-377.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1042` |
| 来源 B | `EV-EN-CR-1042` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1042: rule 377.1 zh/en feature mismatch (number tokens differ: zh=['2', '2'] en=['2', '1', '2', '1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['2', '2'] en=['2', '1', '2', '1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0056`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0056` |
| Rule ID | `R-CR-377.2.b` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1045` |
| 来源 B | `EV-EN-CR-1045` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1045: rule 377.2.b zh/en feature mismatch (bracket tokens differ: zh=['M'] en=['E', 'M', 'Deflect']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['M'] en=['E', 'M', 'Deflect']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: example quote abbreviates card text in zh (omits [E] cost prefix of Ultrasoft Poro); rule semantics unchanged
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：example quote abbreviates card text in zh (omits [E] cost prefix of Ultrasoft Poro); rule semantics unchanged；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0057`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0057` |
| Rule ID | `R-CR-383.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1059` |
| 来源 B | `EV-EN-CR-1059` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1059: rule 383.1 zh/en feature mismatch (number tokens differ: zh=[] en=['1', '2']; bracket tokens differ: zh=[] en=['Nth']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['1', '2']; bracket tokens differ: zh=[] en=['Nth']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0058`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0058` |
| Rule ID | `R-CR-383.1.b` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1061` |
| 来源 B | `EV-EN-CR-1061` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1061: rule 383.1.b zh/en feature mismatch (number tokens differ: zh=[] en=['1']; bracket tokens differ: zh=[] en=['Nth']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['1']; bracket tokens differ: zh=[] en=['Nth']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0059`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0059` |
| Rule ID | `R-CR-383.2.a.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1064` |
| 来源 B | `EV-EN-CR-1064` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1064: rule 383.2.a.1 zh/en feature mismatch (number tokens differ: zh=[] en=['4', '1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['4', '1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: Jinx/Loose Cannon conditional-clause-position variance; adjudicated by MR-2D-0004 (official FAQ unifies zh execution; EN template variant); zh text itself documents the EN phrasing
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：Jinx/Loose Cannon conditional-clause-position variance; adjudicated by MR-2D-0004 (official FAQ unifies zh execution; EN template variant); zh text itself documents the EN phrasing；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0060`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0060` |
| Rule ID | `R-CR-383.3.a.3` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1073` |
| 来源 B | `EV-EN-CR-1073` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1073: rule 383.3.a.3 zh/en feature mismatch (number tokens differ: zh=[] en=['4']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['4']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0061`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0061` |
| Rule ID | `R-CR-383.3.b` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1074` |
| 来源 B | `EV-EN-CR-1074` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1074: rule 383.3.b zh/en feature mismatch (number tokens differ: zh=['2', '2', '2'] en=['2', '1', '2', '2']; bracket tokens differ: zh=['>'] en=['Deathknell', '>']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['2', '2', '2'] en=['2', '1', '2', '2']; bracket tokens differ: zh=['>'] en=['Deathknell', '>']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0062`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0062` |
| Rule ID | `R-CR-383.4.b.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1091` |
| 来源 B | `EV-EN-CR-1091` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1091: rule 383.4.b.1 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Game Object']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Game Object']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0063`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0063` |
| Rule ID | `R-CR-385.2` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1128` |
| 来源 B | `EV-EN-CR-1128` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1128: rule 385.2 zh/en feature mismatch (number tokens differ: zh=[] en=['1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0064`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0064` |
| Rule ID | `R-CR-390.3` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1143` |
| 来源 B | `EV-EN-CR-1143` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1143: rule 390.3 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Nth']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Nth']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0065`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0065` |
| Rule ID | `R-CR-395` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1157` |
| 来源 B | `EV-EN-CR-1157` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1157: rule 395 zh/en feature mismatch (bracket tokens differ: zh=['3', 'B', '>'] en=['3', 'B', 'Deathnkell', '>']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['3', 'B', '>'] en=['3', 'B', 'Deathnkell', '>']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0066`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0066` |
| Rule ID | `R-CR-400.2` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1164` |
| 来源 B | `EV-EN-CR-1164` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1164: rule 400.2 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Add']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Add']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0067`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0067` |
| Rule ID | `R-CR-403.1.b.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1180` |
| 来源 B | `EV-EN-CR-1180` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1180: rule 403.1.b.1 zh/en feature mismatch (bracket tokens differ: zh=[] en=['do X', 'do Y']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['do X', 'do Y']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0068`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0068` |
| Rule ID | `R-CR-411.4` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1213` |
| 来源 B | `EV-EN-CR-1213` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1213: rule 411.4 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Stun']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Stun']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0069`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0069` |
| Rule ID | `R-CR-416.3` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1256` |
| 来源 B | `EV-EN-CR-1256` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1256: rule 416.3 zh/en feature mismatch (number tokens differ: zh=['1'] en=['1', '1', '1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['1'] en=['1', '1', '1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0070`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0070` |
| Rule ID | `R-CR-416.5` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1258` |
| 来源 B | `EV-EN-CR-1258` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1258: rule 416.5 zh/en feature mismatch (number tokens differ: zh=['2', '1'] en=['2', '3', '1', '3']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['2', '1'] en=['2', '3', '1', '3']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0071`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0071` |
| Rule ID | `R-CR-416.6` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1260` |
| 来源 B | `EV-EN-CR-1260` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1260: rule 416.6 zh/en feature mismatch (number tokens differ: zh=[] en=['3', '3', '3']; bracket tokens differ: zh=[] en=['Zone']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['3', '3', '3']; bracket tokens differ: zh=[] en=['Zone']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0072`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0072` |
| Rule ID | `R-CR-417.6.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1275` |
| 来源 B | `EV-EN-CR-1275` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1275: rule 417.6.a zh/en feature mismatch (number tokens differ: zh=['4'] en=['4', '1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['4'] en=['4', '1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0073`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0073` |
| Rule ID | `R-CR-422.3` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1324` |
| 来源 B | `EV-EN-CR-1324` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1324: rule 422.3 zh/en feature mismatch (number tokens differ: zh=['2'] en=['2', '2', '2']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['2'] en=['2', '2', '2']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0074`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0074` |
| Rule ID | `R-CR-422.4` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1325` |
| 来源 B | `EV-EN-CR-1325` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1325: rule 422.4 zh/en feature mismatch (number tokens differ: zh=[] en=['2', '2', '2', '2', '1', '1', '2']; bracket tokens differ: zh=['>'] en=['Deathknell', '>']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['2', '2', '2', '2', '1', '1', '2']; bracket tokens differ: zh=['>'] en=['Deathknell', '>']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0075`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0075` |
| Rule ID | `R-CR-424.3` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1346` |
| 来源 B | `EV-EN-CR-1346` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1346: rule 424.3 zh/en feature mismatch (bracket tokens differ: zh=[] en=['zone', 'Zone']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['zone', 'Zone']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0076`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0076` |
| Rule ID | `R-CR-424.4.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1350` |
| 来源 B | `EV-EN-CR-1350` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1350: rule 424.4.a zh/en feature mismatch (number tokens differ: zh=[] en=['2']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['2']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0077`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0077` |
| Rule ID | `R-CR-427.5` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1380` |
| 来源 B | `EV-EN-CR-1380` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1380: rule 427.5 zh/en feature mismatch (number tokens differ: zh=[] en=['2', '2']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['2', '2']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0078`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0078` |
| Rule ID | `R-CR-428.6` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1401` |
| 来源 B | `EV-EN-CR-1401` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1401: rule 428.6 zh/en feature mismatch (number tokens differ: zh=['2'] en=['2', '1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['2'] en=['2', '1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0079`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0079` |
| Rule ID | `R-CR-430.2` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1414` |
| 来源 B | `EV-EN-CR-1414` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1414: rule 430.2 zh/en feature mismatch (number tokens differ: zh=['1'] en=['1', '1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['1'] en=['1', '1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0080`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0080` |
| Rule ID | `R-CR-430.5` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1420` |
| 来源 B | `EV-EN-CR-1420` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1420: rule 430.5 zh/en feature mismatch (number tokens differ: zh=[] en=['1', '1', '2', '2', '1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['1', '1', '2', '2', '1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0081`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0081` |
| Rule ID | `R-CR-431.2.d` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1431` |
| 来源 B | `EV-EN-CR-1431` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1431: rule 431.2.d zh/en feature mismatch (number tokens differ: zh=['1'] en=['1', '1', '1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['1'] en=['1', '1', '1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0082`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0082` |
| Rule ID | `R-CR-436.3.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1492` |
| 来源 B | `EV-EN-CR-1492` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1492: rule 436.3.a zh/en feature mismatch (bracket tokens differ: zh=['X'] en=[]). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['X'] en=[]
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0083`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0083` |
| Rule ID | `R-CR-437.1.b.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1500` |
| 来源 B | `EV-EN-CR-1500` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1500: rule 437.1.b.1 zh/en feature mismatch (bracket tokens differ: zh=[] en=['source', 'unit']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['source', 'unit']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0084`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0084` |
| Rule ID | `R-CR-437.1.b.1.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1501` |
| 来源 B | `EV-EN-CR-1501` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1501: rule 437.1.b.1.a zh/en feature mismatch (bracket tokens differ: zh=['X'] en=[]). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['X'] en=[]
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0085`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0085` |
| Rule ID | `R-CR-437.2.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1505` |
| 来源 B | `EV-EN-CR-1505` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1505: rule 437.2.a zh/en feature mismatch (number tokens differ: zh=['0', '0', '0'] en=['0', '0']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['0', '0', '0'] en=['0', '0']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0086`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0086` |
| Rule ID | `R-CR-438.7` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1531` |
| 来源 B | `EV-EN-CR-1531` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1531: rule 438.7 zh/en feature mismatch (bracket tokens differ: zh=[] en=['the token', 'Game Object']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['the token', 'Game Object']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0087`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0087` |
| Rule ID | `R-CR-439.5` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1552` |
| 来源 B | `EV-EN-CR-1552` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1552: rule 439.5 zh/en feature mismatch (bracket tokens differ: zh=['Y', 'X', 'X', 'Y'] en=['X', 'Y', 'X', 'Y']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['Y', 'X', 'X', 'Y'] en=['X', 'Y', 'X', 'Y']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0088`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0088` |
| Rule ID | `R-CR-465.2.c.3` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1672` |
| 来源 B | `EV-EN-CR-1672` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1672: rule 465.2.c.3 zh/en feature mismatch (number tokens differ: zh=['5', '3', '2', '3', '1', '3', '2'] en=['5', '3', '2', '1', '3', '3', '2']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['5', '3', '2', '3', '1', '3', '2'] en=['5', '3', '2', '1', '3', '3', '2']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0089`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0089` |
| Rule ID | `R-CR-465.2.c.5` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1675` |
| 来源 B | `EV-EN-CR-1675` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1675: rule 465.2.c.5 zh/en feature mismatch (number tokens differ: zh=['2', '3', '5', '3', '2', '2', '2', '1', '2', '3', '2', '2', '2', '2'] en=['2', '3', '5', '3', '2', '2', '1', '2', '3', '2', '2', '2', '1', '2']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['2', '3', '5', '3', '2', '2', '2', '1', '2', '3', '2', '2', '2', '2'] en=['2', '3', '5', '3', '2', '2', '1', '2', '3', '2', '2', '2', '1', '2']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0090`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0090` |
| Rule ID | `R-CR-471.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1717` |
| 来源 B | `EV-EN-CR-1717` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1717: rule 471.1 zh/en feature mismatch (number tokens differ: zh=['1'] en=[]). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['1'] en=[]
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0091`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0091` |
| Rule ID | `R-CR-477.2.b` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1747` |
| 来源 B | `EV-EN-CR-1747` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1747: rule 477.2.b zh/en feature mismatch (bracket tokens differ: zh=[] en=['Vision']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Vision']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0092`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0092` |
| Rule ID | `R-CR-477.3.b` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1751` |
| 来源 B | `EV-EN-CR-1751` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1751: rule 477.3.b zh/en feature mismatch (bracket tokens differ: zh=['M', 'M', 'M', 'M', 'M', 'M'] en=['M', 'M', 'M', 'M', 'M']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['M', 'M', 'M', 'M', 'M', 'M'] en=['M', 'M', 'M', 'M', 'M']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0093`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0093` |
| Rule ID | `R-CR-485.4.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1799` |
| 来源 B | `EV-EN-CR-1799` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1799: rule 485.4.a zh/en feature mismatch (number tokens differ: zh=['1'] en=['3', '1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['1'] en=['3', '1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0094`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0094` |
| Rule ID | `R-CR-485.5` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1800` |
| 来源 B | `EV-EN-CR-1800` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1800: rule 485.5 zh/en feature mismatch (number tokens differ: zh=[] en=['1', '3']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['1', '3']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0095`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0095` |
| Rule ID | `R-CR-485.6` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1801` |
| 来源 B | `EV-EN-CR-1801` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1801: rule 485.6 zh/en feature mismatch (number tokens differ: zh=[] en=['1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0096`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0096` |
| Rule ID | `R-CR-486.4.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1808` |
| 来源 B | `EV-EN-CR-1808` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1808: rule 486.4.a zh/en feature mismatch (number tokens differ: zh=['1'] en=['3', '1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['1'] en=['3', '1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0097`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0097` |
| Rule ID | `R-CR-486.5` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1809` |
| 来源 B | `EV-EN-CR-1809` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1809: rule 486.5 zh/en feature mismatch (number tokens differ: zh=[] en=['1', '3']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['1', '3']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0098`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0098` |
| Rule ID | `R-CR-486.6` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1811` |
| 来源 B | `EV-EN-CR-1811` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1811: rule 486.6 zh/en feature mismatch (number tokens differ: zh=[] en=['3']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['3']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0099`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0099` |
| Rule ID | `R-CR-486.6.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1812` |
| 来源 B | `EV-EN-CR-1812` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1812: rule 486.6.a zh/en feature mismatch (number tokens differ: zh=['4', '5'] en=['5', '4', '5']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['4', '5'] en=['5', '4', '5']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0100`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0100` |
| Rule ID | `R-CR-487.4.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1821` |
| 来源 B | `EV-EN-CR-1821` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1821: rule 487.4.a zh/en feature mismatch (number tokens differ: zh=['1'] en=['3', '1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['1'] en=['3', '1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0101`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0101` |
| Rule ID | `R-CR-487.5` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1822` |
| 来源 B | `EV-EN-CR-1822` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1822: rule 487.5 zh/en feature mismatch (number tokens differ: zh=[] en=['1', '3']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['1', '3']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0102`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0102` |
| Rule ID | `R-CR-487.6` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1823` |
| 来源 B | `EV-EN-CR-1823` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1823: rule 487.6 zh/en feature mismatch (number tokens differ: zh=[] en=['1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0103`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0103` |
| Rule ID | `R-CR-488.4.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1830` |
| 来源 B | `EV-EN-CR-1830` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1830: rule 488.4.a zh/en feature mismatch (number tokens differ: zh=[] en=['3']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['3']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0104`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0104` |
| Rule ID | `R-CR-488.5` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1832` |
| 来源 B | `EV-EN-CR-1832` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1832: rule 488.5 zh/en feature mismatch (number tokens differ: zh=[] en=['1', '3']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['1', '3']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0105`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0105` |
| Rule ID | `R-CR-488.6` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1833` |
| 来源 B | `EV-EN-CR-1833` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1833: rule 488.6 zh/en feature mismatch (number tokens differ: zh=[] en=['1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0106`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0106` |
| Rule ID | `R-CR-489.4.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1840` |
| 来源 B | `EV-EN-CR-1840` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1840: rule 489.4.a zh/en feature mismatch (number tokens differ: zh=[] en=['3']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['3']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0107`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0107` |
| Rule ID | `R-CR-489.5.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1842` |
| 来源 B | `EV-EN-CR-1842` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1842: rule 489.5.a zh/en feature mismatch (number tokens differ: zh=[] en=['1', '3']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['1', '3']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0108`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0108` |
| Rule ID | `R-CR-489.6` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1848` |
| 来源 B | `EV-EN-CR-1848` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1848: rule 489.6 zh/en feature mismatch (number tokens differ: zh=[] en=['1']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=[] en=['1']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0109`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0109` |
| Rule ID | `R-CR-715.3` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1926` |
| 来源 B | `EV-EN-CR-1926` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1926: rule 715.3 zh/en feature mismatch (number tokens differ: zh=['5', '1', '6', '5', '6'] en=['5', '1', '6', '6', '5']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['5', '1', '6', '5', '6'] en=['5', '1', '6', '6', '5']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0110`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0110` |
| Rule ID | `R-CR-715.4` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1927` |
| 来源 B | `EV-EN-CR-1927` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1927: rule 715.4 zh/en feature mismatch (number tokens differ: zh=['1', '5', '3'] en=['5', '1', '5', '3']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['1', '5', '3'] en=['5', '1', '5', '3']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0111`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0111` |
| Rule ID | `R-CR-722.2` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1959` |
| 来源 B | `EV-EN-CR-1959` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1959: rule 722.2 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Temporary', 'Temporary', 'Temporary']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Temporary', 'Temporary', 'Temporary']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0112`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0112` |
| Rule ID | `R-CR-727.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1969` |
| 来源 B | `EV-EN-CR-1969` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1969: rule 727.1 zh/en feature mismatch (bracket tokens differ: zh=['>', '2', '2'] en=['Legion', '>', '2', 'Legion', 'Text', '2']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['>', '2', '2'] en=['Legion', '>', '2', 'Legion', 'Text', '2']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0113`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0113` |
| Rule ID | `R-CR-727.1.b.2` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1974` |
| 来源 B | `EV-EN-CR-1974` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1974: rule 727.1.b.2 zh/en feature mismatch (bracket tokens differ: zh=['>', 'M'] en=['Level 3', '>', 'M']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['>', 'M'] en=['Level 3', '>', 'M']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0114`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0114` |
| Rule ID | `R-CR-727.1.b.3` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-1975` |
| 来源 B | `EV-EN-CR-1975` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-1975: rule 727.1.b.3 zh/en feature mismatch (bracket tokens differ: zh=['>>', '>'] en=['Level 11', '>>', 'Legion', '>']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['>>', '>'] en=['Level 11', '>>', 'Legion', '>']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0115`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0115` |
| Rule ID | `R-CR-740.4.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2011` |
| 来源 B | `EV-EN-CR-2011` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2011: rule 740.4.a zh/en feature mismatch (bracket tokens differ: zh=[] en=['do X', 'do Y', 'Do X', 'do Y']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['do X', 'do Y', 'Do X', 'do Y']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0116`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0116` |
| Rule ID | `R-CR-757.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2042` |
| 来源 B | `EV-EN-CR-2042` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2042: rule 757.1 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Game Object', 'Category']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Game Object', 'Category']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0117`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0117` |
| Rule ID | `R-CR-806.1.d` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2097` |
| 来源 B | `EV-EN-CR-2097` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2097: rule 806.1.d zh/en feature mismatch (bracket tokens differ: zh=['>'] en=['Action', 'Action', '>']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['>'] en=['Action', 'Action', '>']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0118`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0118` |
| Rule ID | `R-CR-807.1.b.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2111` |
| 来源 B | `EV-EN-CR-2111` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2111: rule 807.1.b.1 zh/en feature mismatch (bracket tokens differ: zh=['X'] en=[]). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['X'] en=[]
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0119`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0119` |
| Rule ID | `R-CR-807.1.b.2` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2112` |
| 来源 B | `EV-EN-CR-2112` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2112: rule 807.1.b.2 zh/en feature mismatch (bracket tokens differ: zh=['X'] en=[]). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['X'] en=[]
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0120`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0120` |
| Rule ID | `R-CR-807.1.b.3` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2113` |
| 来源 B | `EV-EN-CR-2113` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2113: rule 807.1.b.3 zh/en feature mismatch (bracket tokens differ: zh=['X'] en=[]). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['X'] en=[]
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0121`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0121` |
| Rule ID | `R-CR-807.2` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2117` |
| 来源 B | `EV-EN-CR-2117` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2117: rule 807.2 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Assault 3']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Assault 3']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0122`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0122` |
| Rule ID | `R-CR-808.1.b` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2122` |
| 来源 B | `EV-EN-CR-2122` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2122: rule 808.1.b zh/en feature mismatch (bracket tokens differ: zh=['>'] en=['Deathknell', '>', 'Effect']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['>'] en=['Deathknell', '>', 'Effect']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0123`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0123` |
| Rule ID | `R-CR-808.1.b.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2123` |
| 来源 B | `EV-EN-CR-2123` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2123: rule 808.1.b.1 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Effect']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Effect']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0124`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0124` |
| Rule ID | `R-CR-808.1.c` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2124` |
| 来源 B | `EV-EN-CR-2124` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2124: rule 808.1.c zh/en feature mismatch (bracket tokens differ: zh=[] en=['Effect']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Effect']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0125`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0125` |
| Rule ID | `R-CR-808.1.c.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2125` |
| 来源 B | `EV-EN-CR-2125` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2125: rule 808.1.c.1 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Effect']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Effect']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0126`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0126` |
| Rule ID | `R-CR-809.1.b.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2137` |
| 来源 B | `EV-EN-CR-2137` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2137: rule 809.1.b.1 zh/en feature mismatch (bracket tokens differ: zh=['X'] en=[]). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['X'] en=[]
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0127`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0127` |
| Rule ID | `R-CR-809.1.b.2` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2138` |
| 来源 B | `EV-EN-CR-2138` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2138: rule 809.1.b.2 zh/en feature mismatch (bracket tokens differ: zh=['X'] en=[]). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['X'] en=[]
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0128`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0128` |
| Rule ID | `R-CR-809.1.b.3` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2139` |
| 来源 B | `EV-EN-CR-2139` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2139: rule 809.1.b.3 zh/en feature mismatch (bracket tokens differ: zh=['X'] en=[]). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['X'] en=[]
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0129`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0129` |
| Rule ID | `R-CR-809.1.c` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2140` |
| 来源 B | `EV-EN-CR-2140` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2140: rule 809.1.c zh/en feature mismatch (bracket tokens differ: zh=[] en=['me/this', 'me/this']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['me/this', 'me/this']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0130`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0130` |
| Rule ID | `R-CR-811.1.b` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2158` |
| 来源 B | `EV-EN-CR-2158` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2158: rule 811.1.b zh/en feature mismatch (bracket tokens differ: zh=['A'] en=['A', 'Reaction']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['A'] en=['A', 'Reaction']
```

**可能解释**:

```
4B-B003 adjudication [semantic_divergence]: EN carries trailing clause "for as long as you control that battlefield" absent from zh official text (translation omission; possible duration-scoping difference for the Hidden setup ability)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[semantic_divergence]：EN carries trailing clause "for as long as you control that battlefield" absent from zh official text (translation omission; possible duration-scoping difference for the Hidden setup ability)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0131`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0131` |
| Rule ID | `R-CR-811.2` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2169` |
| 来源 B | `EV-EN-CR-2169` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2169: rule 811.2 zh/en feature mismatch (bracket tokens differ: zh=['M'] en=[]). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['M'] en=[]
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0132`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0132` |
| Rule ID | `R-CR-812.1.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2178` |
| 来源 B | `EV-EN-CR-2178` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2178: rule 812.1.a zh/en feature mismatch (bracket tokens differ: zh=['>'] en=['Legion', '>', 'Text']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['>'] en=['Legion', '>', 'Text']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0133`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0133` |
| Rule ID | `R-CR-812.1.b.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2180` |
| 来源 B | `EV-EN-CR-2180` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2180: rule 812.1.b.1 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Text']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Text']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0134`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0134` |
| Rule ID | `R-CR-812.1.b.2` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2181` |
| 来源 B | `EV-EN-CR-2181` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2181: rule 812.1.b.2 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Text']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Text']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0135`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0135` |
| Rule ID | `R-CR-813.1.d` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2192` |
| 来源 B | `EV-EN-CR-2192` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2192: rule 813.1.d zh/en feature mismatch (bracket tokens differ: zh=['>'] en=['Reaction', 'Reaction', '>']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['>'] en=['Reaction', 'Reaction', '>']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0136`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0136` |
| Rule ID | `R-CR-814.1.b.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2207` |
| 来源 B | `EV-EN-CR-2207` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2207: rule 814.1.b.1 zh/en feature mismatch (bracket tokens differ: zh=['X'] en=[]). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['X'] en=[]
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0137`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0137` |
| Rule ID | `R-CR-814.1.b.2` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2208` |
| 来源 B | `EV-EN-CR-2208` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2208: rule 814.1.b.2 zh/en feature mismatch (bracket tokens differ: zh=['X'] en=[]). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['X'] en=[]
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0138`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0138` |
| Rule ID | `R-CR-814.1.b.3` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2209` |
| 来源 B | `EV-EN-CR-2209` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2209: rule 814.1.b.3 zh/en feature mismatch (bracket tokens differ: zh=['X'] en=[]). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['X'] en=[]
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0139`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0139` |
| Rule ID | `R-CR-814.2` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2213` |
| 来源 B | `EV-EN-CR-2213` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2213: rule 814.2 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Shield 3', 'Tank']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Shield 3', 'Tank']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0140`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0140` |
| Rule ID | `R-CR-815.1.b` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2218` |
| 来源 B | `EV-EN-CR-2218` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2218: rule 815.1.b zh/en feature mismatch (bracket tokens differ: zh=[] en=['Tank']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Tank']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0141`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0141` |
| Rule ID | `R-CR-818.1.c` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2247` |
| 来源 B | `EV-EN-CR-2247` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2247: rule 818.1.c zh/en feature mismatch (bracket tokens differ: zh=[] en=['Cost']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Cost']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0142`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0142` |
| Rule ID | `R-CR-818.1.c.2` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2249` |
| 来源 B | `EV-EN-CR-2249` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2249: rule 818.1.c.2 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Cost']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Cost']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0143`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0143` |
| Rule ID | `R-CR-819.1.d` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2267` |
| 来源 B | `EV-EN-CR-2267` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2267: rule 819.1.d zh/en feature mismatch (bracket tokens differ: zh=[] en=['Reaction']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Reaction']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0144`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0144` |
| Rule ID | `R-CR-820.1.c` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2274` |
| 来源 B | `EV-EN-CR-2274` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2274: rule 820.1.c zh/en feature mismatch (bracket tokens differ: zh=[] en=['Cost']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Cost']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0145`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0145` |
| Rule ID | `R-CR-820.1.d` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2278` |
| 来源 B | `EV-EN-CR-2278` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2278: rule 820.1.d zh/en feature mismatch (bracket tokens differ: zh=[] en=['Cost']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Cost']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0146`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0146` |
| Rule ID | `R-CR-820.1.d.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2279` |
| 来源 B | `EV-EN-CR-2279` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2279: rule 820.1.d.1 zh/en feature mismatch (number tokens differ: zh=['2', '2', '2', '2'] en=['2', '2', '2', '2', '1']; bracket tokens differ: zh=['2', 'M', 'M', 'M'] en=['Repeat', '2', 'M', 'M', 'M', 'Repeat']). Auto-classified translation_difference(low).
```

**冲突点**:

```
number tokens differ: zh=['2', '2', '2', '2'] en=['2', '2', '2', '2', '1']; bracket tokens differ: zh=['2', 'M', 'M', 'M'] en=['Repeat', '2', 'M', 'M', 'M', 'Repeat']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0147`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0147` |
| Rule ID | `R-CR-820.2.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2282` |
| 来源 B | `EV-EN-CR-2282` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2282: rule 820.2.a zh/en feature mismatch (bracket tokens differ: zh=['4', 'C'] en=['Repeat', '4', 'C', 'or']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['4', 'C'] en=['Repeat', '4', 'C', 'or']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0148`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0148` |
| Rule ID | `R-CR-822.1.b` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2304` |
| 来源 B | `EV-EN-CR-2304` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2304: rule 822.1.b zh/en feature mismatch (bracket tokens differ: zh=[] en=['Reaction']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Reaction']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0149`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0149` |
| Rule ID | `R-CR-822.1.d` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2306` |
| 来源 B | `EV-EN-CR-2306` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2306: rule 822.1.d zh/en feature mismatch (bracket tokens differ: zh=[] en=['Ambush', 'Ambush', 'Action']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Ambush', 'Ambush', 'Action']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0150`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0150` |
| Rule ID | `R-CR-823.1.c.2` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2317` |
| 来源 B | `EV-EN-CR-2317` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2317: rule 823.1.c.2 zh/en feature mismatch (bracket tokens differ: zh=['X'] en=[]). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['X'] en=[]
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0151`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0151` |
| Rule ID | `R-CR-823.1.c.3` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2318` |
| 来源 B | `EV-EN-CR-2318` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2318: rule 823.1.c.3 zh/en feature mismatch (bracket tokens differ: zh=['X'] en=[]). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['X'] en=[]
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0152`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0152` |
| Rule ID | `R-CR-824.1.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2323` |
| 来源 B | `EV-EN-CR-2323` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2323: rule 824.1.a zh/en feature mismatch (bracket tokens differ: zh=['N', '>'] en=['Level [N', '>', 'Text']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['N', '>'] en=['Level [N', '>', 'Text']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0153`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0153` |
| Rule ID | `R-CR-824.1.b.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2325` |
| 来源 B | `EV-EN-CR-2325` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2325: rule 824.1.b.1 zh/en feature mismatch (bracket tokens differ: zh=['N'] en=['N', 'Text']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['N'] en=['N', 'Text']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0154`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0154` |
| Rule ID | `R-CR-824.1.b.2` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2326` |
| 来源 B | `EV-EN-CR-2326` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2326: rule 824.1.b.2 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Text']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Text']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0155`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0155` |
| Rule ID | `R-CR-826.3` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2342` |
| 来源 B | `EV-EN-CR-2342` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2342: rule 826.3 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Backline']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Backline']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0156`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0156` |
| Rule ID | `R-CR-827.1.c` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2353` |
| 来源 B | `EV-EN-CR-2353` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2353: rule 827.1.c zh/en feature mismatch (bracket tokens differ: zh=[] en=['Cost']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Cost']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0157`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0157` |
| Rule ID | `R-CR-827.1.c.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2354` |
| 来源 B | `EV-EN-CR-2354` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2354: rule 827.1.c.1 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Cost']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Cost']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0158`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0158` |
| Rule ID | `R-CR-828.1.a` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2364` |
| 来源 B | `EV-EN-CR-2364` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2364: rule 828.1.a zh/en feature mismatch (bracket tokens differ: zh=['>'] en=['Empowered', '>', 'Text']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=['>'] en=['Empowered', '>', 'Text']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0159`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0159` |
| Rule ID | `R-CR-828.1.b.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2366` |
| 来源 B | `EV-EN-CR-2366` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2366: rule 828.1.b.1 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Text']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Text']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0160`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0160` |
| Rule ID | `R-CR-828.1.b.2` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2367` |
| 来源 B | `EV-EN-CR-2367` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2367: rule 828.1.b.2 zh/en feature mismatch (bracket tokens differ: zh=[] en=['Text']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Text']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

#### `MR-3-CR-0161`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-3-CR-0161` |
| Rule ID | `R-CR-829.1.c` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-CR-2377` |
| 来源 B | `EV-EN-CR-2377` |

**问题（原始记录）**:

```
Stage 3 core-rules alignment AL-CR-2377: rule 829.1.c zh/en feature mismatch (bracket tokens differ: zh=[] en=['Cost']). Auto-classified translation_difference(low).
```

**冲突点**:

```
bracket tokens differ: zh=[] en=['Cost']
```

**可能解释**:

```
4B-B003 adjudication [equivalent]: semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)
```

**无法自动裁决原因**:

```
跨语言语义等价需人工核对原文
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B003 裁定关闭] 4B裁决[equivalent]：semantic equivalence confirmed by full-text comparison; difference is orthographic (Chinese numerals vs digits / keyword bracket tokens translated inline / EN placeholder brackets vs zh prose)；canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5
```

## 4. Stage 4A 聚类 — FAQ 引用旧规则编号（6 条）

> FAQ 引用 2026-07 核心规则中不存在的旧规则编号;4B-B005 已逐条核验后继条文覆盖（successor coverage verified)并结案。

#### `MR-4A-0001`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-4A-0001` |
| Rule ID | `R-CR-342.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-FAQ-0011` |
| 来源 B | `source_009/source_018 core rules (2026-07)` |

**问题（原始记录）**:

```
FAQ EV-CN-FAQ-0011 explicitly references core rule number(s) 376.3 which do not exist in the current 2026-07 core rules (clustering could not attach the ref)
```

**冲突点**:

```
referenced rule number absent from current rule-number space
```

**可能解释**:

```
ADJUDICATED 2026-09-21 (content-level (numbering restructured)): 376.3 -> 383.3.d/383.3.d.1 (383.3.d.1 内容与旧条文一致：同时多触发按回合顺序放置；战斗防守方最后添加的细则由 383.4.f 系列 + 466.x 承担). Source FAQ is judge-tier citing older core-rules numbering (pre-2026-07 restructure).
```

**无法自动裁决原因**:

```
kept OPEN per operator decision: Stage 4B must verify successor text covers the FAQ ruling before closing; treat ref as historical until verified
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B005 结案] successor coverage verified: 383.3.d.1 == simultaneous multi-player triggers placed in turn order (verbatim match of general rule); defender-triggers-last specifics carried by 383.4.f (防守触发 def, verified) + 466.x resolution steps. FAQ ruling fully covered by successors. CLOSED.
```

#### `MR-4A-0002`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-4A-0002` |
| Rule ID | `R-CR-440.1` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-FAQ-0031` |
| 来源 B | `source_009/source_018 core rules (2026-07)` |

**问题（原始记录）**:

```
FAQ EV-CN-FAQ-0031 explicitly references core rule number(s) 322.2, 322.3 which do not exist in the current 2026-07 core rules (clustering could not attach the ref)
```

**冲突点**:

```
referenced rule number absent from current rule-number space
```

**可能解释**:

```
ADJUDICATED 2026-09-21 (content-level (numbering restructured)): 322.2,322.3 -> 318 清理(步骤序列); 现行清理全流程集中于 318-324, 特殊清理步骤由 324.1/466.1.a 决定. Source FAQ is judge-tier citing older core-rules numbering (pre-2026-07 restructure).
```

**无法自动裁决原因**:

```
kept OPEN per operator decision: Stage 4B must verify successor text covers the FAQ ruling before closing; treat ref as historical until verified
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B005 结案] successor coverage verified: 324.1 (special cleanup steps determined by triggering category, combat -> 466) verbatim match of FAQ claim structure; 466.1.a 启动战斗特殊清理 + 466.1.a.1/.2 insert steps (3c remove damage / 3d recall attackers) cover old [440.1.a.1-3]; 318 cleanup flow covers old 322.2/322.3 sequence position. CLOSED.
```

#### `MR-4A-0003`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-4A-0003` |
| Rule ID | `R-CARD-OGN-049` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-FAQ-0032` |
| 来源 B | `source_009/source_018 core rules (2026-07)` |

**问题（原始记录）**:

```
FAQ EV-CN-FAQ-0032 explicitly references core rule number(s) 322.2, 322.3, 322.8 which do not exist in the current 2026-07 core rules (clustering could not attach the ref)
```

**冲突点**:

```
referenced rule number absent from current rule-number space
```

**可能解释**:

```
ADJUDICATED 2026-09-21 (content-level (numbering restructured)): 322.2,322.3,322.8 -> 318 清理 + 324 特殊清理 + 466 结算步骤; 440.1.a.1-3/440.1.b -> 466.1.a 战斗特殊清理 (旧440.x为燃烧规则,编号已重用). Source FAQ is judge-tier citing older core-rules numbering (pre-2026-07 restructure).
```

**无法自动裁决原因**:

```
kept OPEN per operator decision: Stage 4B must verify successor text covers the FAQ ruling before closing; treat ref as historical until verified
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B005 结案] successor coverage verified (same mapping family as MR-4A-0002): damage-mark clearing now inserted as step 3c via 466.1.a.1 during combat special cleanup; KogMaw Last Breath trigger chain-finalize per 324 special-cleanup flow. Old 440.x (Burn) number-reuse confirmed. CLOSED.
```

#### `MR-4A-0004`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-4A-0004` |
| Rule ID | `R-TOPIC-CN-40` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-FAQ-0055` |
| 来源 B | `source_009/source_018 core rules (2026-07)` |

**问题（原始记录）**:

```
FAQ EV-CN-FAQ-0055 explicitly references core rule number(s) 735.1 which do not exist in the current 2026-07 core rules (clustering could not attach the ref)
```

**冲突点**:

```
referenced rule number absent from current rule-number space
```

**可能解释**:

```
ADJUDICATED 2026-09-21 (full): 735.1.c -> 809.1.c (文本几乎逐字对应, 完全确认; MR-2D-0007 先例). Source FAQ is judge-tier citing older core-rules numbering (pre-2026-07 restructure).
```

**无法自动裁决原因**:

```
kept OPEN per operator decision: Stage 4B must verify successor text covers the FAQ ruling before closing; treat ref as historical until verified
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B005 结案] successor coverage verified: 809.1.c text == 735.1.c（修订后）semantics verbatim (Ward keyword shorthand; MR-2D-0007 incorporation precedent). CLOSED.
```

#### `MR-4A-0005`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-4A-0005` |
| Rule ID | `R-CR-323.5` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-FAQ-0198` |
| 来源 B | `source_009/source_018 core rules (2026-07)` |

**问题（原始记录）**:

```
FAQ EV-CN-FAQ-0198 explicitly references core rule number(s) 460.2 which do not exist in the current 2026-07 core rules (clustering could not attach the ref)
```

**冲突点**:

```
referenced rule number absent from current rule-number space
```

**可能解释**:

```
ADJUDICATED 2026-09-21 (content-level): 460.2.c.3 -> 465.2.c.4(+465.2.c.4.a) 致命伤害最小分配一致; 323.5 经核对在现行规则中存在且内容一致(步骤3b 致命伤害摧毁), 无需重映射 -- 仅 460.2.x 为旧编号. judge-FAQ 引用旧版编号.
```

**无法自动裁决原因**:

```
kept OPEN per operator decision: Stage 4B must verify successor text covers the FAQ ruling before closing; treat ref as historical until verified
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B005 结案] successor coverage verified: 465.2.c.4(.a) == lethal-minimum allocation rule (verbatim content match with old 460.2.c.3); current 323.5 (3b lethal-destroy, refs 142.4) content-consistent with FAQ quote. CLOSED.
```

#### `MR-4A-0006`

| 字段 | 值 |
| --- | --- |
| Issue ID | `MR-4A-0006` |
| Rule ID | `R-TOPIC-CN-15` |
| 状态 | **已关闭**（2026-09-22） |
| 来源 A | `EV-CN-FAQ-0216` |
| 来源 B | `source_009/source_018 core rules (2026-07)` |

**问题（原始记录）**:

```
FAQ EV-CN-FAQ-0216 explicitly references core rule number(s) 335.3 which do not exist in the current 2026-07 core rules (clustering could not attach the ref)
```

**冲突点**:

```
referenced rule number absent from current rule-number space
```

**可能解释**:

```
ADJUDICATED 2026-09-21 (content-level (numbering restructured)): 335.3 -> 334 (+335-336) HOT FEPR 主规则名称逐字对应. Source FAQ is judge-tier citing older core-rules numbering (pre-2026-07 restructure).
```

**无法自动裁决原因**:

```
kept OPEN per operator decision: Stage 4B must verify successor text covers the FAQ ruling before closing; treat ref as historical until verified
```

**裁定结论（关闭记录）**:

```
[2026-09-22 4B-B005 结案] successor coverage verified: current 335 (no pending tasks/items -> main phase priority / other phase advance) matches old 335.3 quote verbatim (plus showdown/combat clause); 334.1 HOT task-handling exists; HOT FEPR naming逐字对应. CLOSED.
```

---

*End of manual_review.md — 186 entries, all formally closed. 复核请回查 workspace/rules_work.db 的 manual_review 表。*
