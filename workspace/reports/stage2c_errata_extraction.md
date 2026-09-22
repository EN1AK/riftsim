# Stage 2C — Errata / Correction Evidence Extraction Report

Date: 2026-09-20 · Stage: 2C · Executor script: `stage2c_extract_errata.py`

## 范围

仅处理 Errata / Correction 来源；未重新抽取 Core Rules；未做任何规则裁决（
Reconciliation 职责），未修改 `rules` / `canonical_rule`。

## 统计

```text
Errata documents:   8 (zh: 4 / en: 4)
Errata evidence:    159 (156 card_errata + 3 front_matter)
Mapped targets:     156
Unmapped targets:   0
Warnings:           8 (见下)
```

### 按文档

| source_id | 文档 | 语言 | 条目 | Mapped |
|---|---|---|---|---|
| source_002 | 符文战场_勘误汇总_1028 | zh | 31 | 31 |
| source_003 | 破限系列_勘误汇总_260403 | zh | 31 | 31 |
| source_004 | 铸魂淬炼系列_勘误汇总_260114 | zh | 18 | 18 |
| source_010 | 卡牌新旧文本勘误 (2026-07-24) | zh | 13 | 13 |
| source_013 | Origins_Errata | en | 31 (+1 front_matter) | 31 |
| source_015 | Spiritforged_Errata | en | 16 | 16 |
| source_017 | Unleashed_Errata | en | 8 (+1 front_matter) | 8 |
| source_020 | Vendetta_Errata | en | 8 (+1 front_matter) | 8 |

Mapped target 定义（本阶段）：成功识别目标卡名（`target_rule_candidate`）且新旧文本
片段（`original_fragment` / `corrected_fragment`）完整的条目。卡牌语料不在 rules 表中，
与印刷卡文本的对照不属于 Stage 2C。

### modification_type 分布（启发式，未经裁决）

| type | 数量 | 说明 |
|---|---|---|
| partial_replacement | 73 | 相似度 ≥0.85 的小幅改写 |
| condition_change | 30 | 时序/条件结构变化 |
| terminology_fix | 28 | 全部来自 zh「翻译勘误/翻译优化」分节 |
| effect_change | 19 | 新增“然后进行一次/do this”结算结构等 |
| replacement | 5 | 相似度 <0.5 的整体重写 |
| numeric_change | 1 | 仅数值差异 |
| uncertain | 0 | — |

### effective_scope 特值

- `english_card_text_only`：6 条（zh 002 三条「注：只有英文版卡牌的文本有所不同」+ zh 003
  涌泉之恨「只有英文版卡牌的文本需要勘误」+ en 013 三条对应条目：传送门大营救/Portal Rescue、
  塞壬号/The Syren、疾风剑豪/Unforgiven、Death from Below/涌泉之恨）
- `printed_text_alignment`：4 条（zh 010「新文本与目前卡面文本一致」：德莱文、帝王神坛、
  黛安娜、普朗克）

## needs_review（manual_review，共 4 项）

| item_id | 问题 |
|---|---|
| MR-2C-0001 | zh source_004 的 沉没神庙/遗忘丰碑 2 条在 EN source_015 无对应（条目覆盖不一致，中英文差异候选） |
| MR-2C-0002 | source_013 内部 "Last Updated: 2025-10-21" 早于文件名日期 2025-10-28（日期歧义） |
| MR-2C-0003 | source_020 文章日期 2026-07-24 与文件名 2026-07-23 差 1 天（与 zh 对应文档 source_010 2026-07-24 一致） |
| MR-2C-0004 | zh source_003 有 13 条纯中文「翻译勘误/翻译优化」条目无 EN 对应（跨语言等价需 Stage 3 验证） |

## Warnings

1. modification_type 为启发式分类（notes: `modification_type_source: heuristic`），Reconciliation 阶段需复核。
2. 跨语言条目映射（zh↔en 同卡对应）本阶段未尝试，留待 Stage 3；已知异常见 MR-2C-0001。
3. source_013 日期歧义（MR-2C-0002）；source_020 日期歧义（MR-2C-0003）。
4. EN 站点导出文档（source_017/020）含页脚/侧栏噪音（版权、PRIVACY、RELATED ARTICLES 等），解析时已过滤；
   source_020 的 Resonating Strike 卡名在 p6、正文在 p7（噪音夹其间），已正确拼接并在 notes 记录页码差异。
5. 跨页条目（如 zh 003 乐芙兰 p2→p3、普朗克 - 海上霸主 p4→p5、EN 013/015 多条）已按 PAGE 标记拼接，
   evidence.page 记为 `[新文本]/[NEW TEXT]` 起始页。
6. 元数据修正：source_002/003/004 的 source_type `other→errata`、language `unknown→zh`；
   source_013/015/017 language `unknown→en`。
7. 任务页码缺口修正：task_002_01 page_end 10→13、task_003_01 10→14、task_013_01 10→14。
8. 跨文档重复条目（德莱文：zh 003 翻译优化 + zh 010；沃利贝尔/巨神峰之巅：zh 002 + zh 010 翻译优化；
   涌泉之恨：zh 003 + zh 010 + en 013/017）均逐源保留，去重留待 Reconciliation。

## 数据落点

- `workspace/rules_work.db` `evidence`：159 行（EV-CN-ER-0001..0093 / EV-EN-ER-0001..0066），
  新增勘误专用列：`target_rule_candidate, target_source, original_fragment, corrected_fragment,
  modification_type, effective_scope`。
- `manual_review`：MR-2C-0001..0004。
- `processing_tasks`：8 个任务全部 completed（页码范围已覆盖全文）。
- 机器可读统计：`workspace/reports/stage2c_stats.json`。

## 处理脚本

`stage2c_extract_errata.py`（仓库根目录）：状态机解析（卡名 → [新文本]/[NEW TEXT] → ▲ →
[旧文本]/[OLD TEXT]），EN 网页噪音过滤，跨页拼接，启发式 modification_type 分类。
