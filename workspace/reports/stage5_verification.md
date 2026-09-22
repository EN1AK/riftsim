# Stage 5 — Independent Verification 报告

生成时间: 2026-09-22T08:52:28+00:00   脚本: stage5_verify.py (幂等; 批次 setup/v1/v2/v3/validate)

## 范围
- 393 条 rules.needs_verification='true' + 冲突 CON-4B-T2-0001 (pending_stage5)
- verification 表扩列: stage4_conclusion/verification_conclusion/relevant_evidence/disagreement_reason/verified_at
- 任务: task_5_01..05 全部 completed

## 批次
| 批次 | 范围 | 结果 |
|---|---|---|
| v1 (task_5_02) | 160 条 tr-diff R-CR (除 811.1.b) | 160 verified; canonical==zh官方原文逐字(回查 EV-CN-CR same 链接), en same 链接存在, REC-4B-T2 裁决行在, FAQ 挂载逐字; 0 needs_review |
| v2 (task_5_03) | 130 条 errata R-CARD | 130 verified; canonical==最新zh勘误 corrected_fragment 逐字(按 date-asc 链, 含 7 条双勘误链), CHG-4B-T2ER 行数==替换链接数, EN 对照勘误仅记录未改 canonical, 修改范围未扩大; 0 needs_review |
| v3 (task_5_04) | 102 条混合 (30 FAQ-only卡 + 14 T1F + 57 T3桶 + 811.1.b) + 冲突 | 102 verified + 1 verified_with_changes; 0 needs_review |

注: v3 首跑 23 项 needs_review 全部为检查器对 B005/B006 记录形式理解不足的误报
(stale-ref 故意不挂载字段为 NULL / T3 计数式 REC + OI 逐条挂载 / APPLIED 判定词窗口),
修正检查逻辑后复跑全部通过; 数据无需任何更改。

## 冲突裁决 CON-4B-T2-0001 (R-CR-811.1.b, Hidden 811.1.b)
- **分歧**: EN 官方核心规则 (source_018, 2026-07-16, 与 CN 同版本——2B 已证规则编号序列完全一致)
  带持续时段从句 "for as long as you control that battlefield"; zh 官方译文 (source_009) 缺失该从句。
- **裁决依据**: 规范 2.4/15.4 —— 同版本: 英文官方文本 > 中文官方文本。EN 仅早 1 天且同版本序列证明一致,
  不构成"旧英文机械覆盖新中文"的例外情形。语义差异有实际玩法影响 (待命牌在失去战场控制后的存留)。
- **结论**: verified_with_changes。canonical 补入该从句的中文转写
  (「…此牌保持正面朝下待命状态，直至你不再控制该战场。…」), 符合库内既有中文措辞习惯。
- **记录**: CHG-5-0001 (modification_type=condition_change, 含 old/new 全文与理由);
  conflicts.resolution_status=resolved_stage5; VER-5-R-CR-811.1.b 含 stage4_conclusion /
  verification_conclusion / disagreement_reason (4B zh-约定 vs 5 EN-优先, 证据明确可裁决, 无需 manual_review)。

## 专题核验
- **Errata 应用范围** (规范16.5): 130 规则 canonical 与最新 zh 勘误片段完全相等 → 修改目标正确、范围未扩大、
  未误删未修改部分 (canonical 仅取自 corrected_fragment)。
- **FAQ 泛化**: rules.derived_interpretation 全库 0 行 —— 从未发生 FAQ 过度泛化为一般规则;
  411 条 faq:example_only / rule_interpretation / exception 挂载全部逐字 + 来源前缀回查通过
  (001/006/008 judge-community 层级前缀保持)。
- **中英版本**: 161 tr-diff 全部维持"同版本正字差异"结论; 唯一语义分歧已按上条裁决。
- **RCC 134 链接全覆盖**: source_019 (eff 2026-07-24 > 2026-07 核心) APPLIED 均有 '[eid|...|APPLIED post-core
  official change]' 逐条挂载 + CHG-4B-T3 行; source_012/014/016 (transitional pre-core) NOT applied 记录一致
  (日期逻辑独立复核通过); source_005/007 INCORPORATED 7 条有 CHG-4B-T1F/T3-0006 行, 0055 vs 现行 809.1.c
  语义等价复核通过; B005 stale-ref 7 链接确认字段留空属裁决结果且内容挂载于正确后继规则
  (0206→816.2 ✓, 0207→323.6 ✓, 后继覆盖 340.4/383.x/466.x/471.1.b.1)。
- **MR-2D-0005 watch 4 卡** (OGN-131/OGN-251/UNL-097/UNL-177): REC-4B-T3 watch 行在, 现行口径按
  设计师 FAQ source_008 sec.4, EN 为权威参照, 待 zh 文本更新追踪保留于 REC notes (OGN-251 的
  EV-CN-FAQ-0260 未链警告如实记录)。

## 终态 (validate)
- verification 共 393 行: [{'status': 'verified', 'c': 392}, {'status': 'verified_with_changes', 'c': 1}]
- needs_verification='true' 剩余 0
- conflicts: [{'conflict_id': 'CON-4B-T2-0001', 'rule_id': 'R-CR-811.1.b', 'resolution_status': 'resolved_stage5'}]
- changes 总计 267 (新增 CHG-5 x1)
- rejected=0, failed=0, pending=0, needs_review=0 → **Stage 5 = completed**
