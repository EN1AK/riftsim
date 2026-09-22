# Stage 4B — Batch 006 (4B-B006): R-TOPIC / R-MISC / front-matter + 128 RCC 裁决

- 日期: 2026-09-22
- Task: task_4b_06（processing_tasks, status=completed）
- 脚本: stage4b_b006_reconcile.py（幂等：先删 REC-4B-T3-% / CHG-4B-T3-% 再重算写入；单次运行）
- Checkpoint: workspace/checkpoints/stage4b_b006_checkpoint.json
- 探查转储: workspace/checkpoints/stage4b_b006_probe{,2,3,4,5,6}.json

## 范围

最后 88 条 pending_reconciliation 规则（81 R-TOPIC [17 CN + 64 EN] + 5 R-MISC + R-ER-FRONT + R-FAQ-FRONT）
以及 B005 范围决议中剩余的 128 条 `faq:rule_change_candidate`（RCC）链接：
117 条挂在 pending 规则上 + 11 条挂在 B002/B004 已裁决的 R-CARD 规则上（8 张卡）。

## 权威裁决（Group-C 权威拓扑 MR-2D-0009/0010/0013 + B005 范围决议）

| 分组 | 来源 | 链接数 | 裁决 |
|---|---|---|---|
| zh FAQ 核心前 | source_005 (EV-CN-FAQ-0055, R-TOPIC-CN-40) | 1 | INCORPORATED：735.1.c 修订文已并入 2026-07 核心规则 809.1.c（EV-CN-CR-2140；MR-2D-0007 + B005 先例）→ 记 CHG-4B-T3，不应用 |
| EN patch notes 过渡性（核心前）| source_012/014/016（2025-10-24 / 2025-12-05 / 2026-03-31，均早于 2026-07 核心规则）| 90（85 pending + 5 R-CARD）| NOT applied：权威随 2026-07 核心规则发布被取代；逐条记录于 REC original_fragment；逐项并入核对留 Stage 5 抽查 |
| EN patch notes 核心后 | source_019（Vendetta，eff 2026-07-24，晚于核心）| 37（31 pending + 6 R-CARD）| APPLIED：作为官方变更应用；每条链接写 CHG-4B-T3（modification_type=new_rule_addition），声明文本逐字附加到规则的 official_interpretation（前缀标记 `APPLIED post-core official change`）；needs_verification=true |

## 执行结果（全部经 DB 复核，非脚本打印）

- 88/88 规则 reconciled：**pending_reconciliation = 0；rules 全表 2984/2984 reconciled**
- FAQ attach（tier-1 约定，`[evidence_id | source | tier | class]` 前缀 + Q/A 原文逐字）：
  156 条 faq:rule_interpretation → official_interpretation（tier：source_001/006/008=judge-community，其余 official；q 为空的 34 条散文条目以 faq_answer/original_text 为正文）
- 37 条 source_019 RCC 应用 → 38 CHG-4B-T3 行（另 1 条 EV-CN-FAQ-0055 incorporated CHG，final_conclusion=recorded, not applied）
- 100 条 REC-4B-T3 行（88 pending 规则 + 8 R-CARD RCC 裁决 + 4 观察卡 fold-in），status=reconciled_tier3
- canonical：R-TOPIC/R-MISC/front 聚合桶无自身规则书/勘误文本，canonical 保持 NULL（设计，写入 REC original_fragment）；
  8 张 R-CARD 的 B002/B004 canonical 未触碰
- needs_verification='true'：58 条携带 RCC 的 pending 规则 + 4 张观察卡（其余 30 条纯 attach/front 为 false）→ 全表 nv=true 332→393
- task_4b_06 已登记 completed（stage4b_tier3_topic_misc_front_rcc）

## MR-2D-0005 观察卡 fold-in

R-CARD-OGN-131 / OGN-251 / UNL-097 / UNL-177 各写 REC-4B-T3（effective_scope=mr2d0005_watch_fold_in），
nv 全部置 true（中英文本语义分歧 → spec 15.7）：现行口径 = zh 设计师 FAQ source_008 第4节（EV-CN-FAQ-0260）结算链分析，
EN 原文为效力参照，pending_zh_text_update 观察持续，等后续中文勘误。

## Warnings / 已知事项

1. **EV-CN-FAQ-0260 未链接到 R-CARD-OGN-251**（其余 3 卡及其 a 变体已挂 example_only 链接）；
   金克丝在 MR-2D-0005 issue 正文中列名，sec.4 为文档级分析——已在 REC 注记中如实标注，链接层不动（Stage 4A 管辖）。
2. 118 条 R-CARD/挂 R-CARD 的 RCC 中 UNL-138 同时接收 014（3 条 transitional）与 019（1 条 applied）两种裁决，均已分别记录。
3. 6 条 R-CR 上的 RCC（source_007 0196×5/0201）B005 已裁决（INCORPORATED），本批不重复处理。

## Batch 统计

```
Rules processed:      88 (pending) + 8 (R-CARD RCC) + 4 (watch) = 100 REC 行
Resolved:             88/88 → Stage 4B 全部完成
RCC attached:         156 (interpretation) / 128 (RCC: 37 applied + 90 transitional + 1 incorporated)
Changes written:      38 (CHG-4B-T3-0001..0038)
Needs verification:   58 条 RCC-carrying pending 规则 + 4 观察卡（其中 3 张由 false→true；OGN-131 原本即 true）
                      → 全表 nv=true: 332 → 393
Conflicts:            本批 0（全表 1：CON-4B-T2-0001 待 Stage 5）
Needs review:         0
Failed:               0
```

## Stage 4B 完成判定（spec 15.10）

- 所有 Rule 均有 proposed canonical rule 或明确 NULL-canonical 桶记录（R-TOPIC/R-MISC/front/FAQ-only R-CARD）→ 无 unresolved
- pending = 0 / running = 0 / failed = 0

**Stage 4B = completed。** 下一阶段：Stage 5（needs_verification='true' 的 393 条规则 + 1 条 pending_stage5 冲突）。
