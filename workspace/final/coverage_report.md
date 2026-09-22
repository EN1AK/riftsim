# Stage 6A — Coverage Report (最终覆盖检查)

生成时间: 2026-09-22T09:14:16+00:00   脚本: stage6a_coverage_check.py (幂等)   依据: spec 17.1 / 17.2
数据来源: workspace/rules_work.db (rules 2984 / evidence 5527 — Stage 5 终态验证后)

## 总体计数 (spec 17.2)

```text
Documents discovered: 20
Documents processed:  20
Documents failed:     0

Evidence extracted:   5527  (rule=4764, errata=159, faq=332, official_explanation=272)
Evidence mapped:      5527
Unmapped evidence:    0

Rules generated:      2984
Rules verified:       393  (verified=392, verified_with_changes=1)
                      其余 2591 条 needs_verification=false (Stage 4B tier-0 等价合入, spec 16.1 不属 Stage 5 范围)
                      pending verification = 0

Errata applied:       137 zh replacement links → 130 R-CARD rules (canonical==最新 zh 勘误 corrected_fragment; Stage 5 v2 130/130 逐字回查)
                      EN counterpart recorded: 85 links (仅记录, 不改 canonical)
                      errata front_matter: 3; uncovered errata: 0
FAQ attached:         1354 faq:* links; unmounted faq/oe: 0
Rulings attached:     225/225  (裁判FAQ source_001/006/008, judge-community 层级 per MR-2D-0013)

Conflicts resolved:   1
Unresolved conflicts: 0

Manual review items:  186  (全部经 Stage 2D/3/4A/4B 正式裁决关闭; 详情见 manual_review.md [6E])
```

## 强制检查清单 (spec 17.1)

| ID | 检查项 | 结果 | 明细 |
|---|---|---|---|
| C1 | source 全部已处理 (evidence>0) | PASS | documents discovered=20 processed=20 failed=0 |
| C2 | 无未恢复 failed/running/pending task | PASS | processing_tasks={'completed': 64} |
| C3 | Evidence 全部已映射 (rule_evidence) | PASS | mapped=5527/5527 unmapped=0 |
| C4 | Rule 全部有来源 | PASS | rules=2984 without-evidence=0 |
| C5 | Errata 全部已应用/记录 | PASS | card errata w/ replacement link=156 (zh links=137, en links=85), front_matter=3, uncovered=0 |
| C6 | FAQ/OE 全部已挂载 | PASS | faq:* links=1354 on 604 faq/oe rows, unmounted=0 |
| C7 | inferred 日期未误写 confirmed | PASS | confirmed=2 [('source_009', '2026-07-17'), ('source_018', '2026-07-16')] (doc-self-stated only); date_confidence dist={'confirmed': 2, 'declared': 8, 'inferred': 10} |
| C8 | FAQ 无过度泛化 (derived_interpretation=0) | PASS | derived_interpretation non-empty=0 |
| C9 | superseded 项已标记且不作为现行规则 | PASS | superseded-tagged=['EV-CN-FAQ-0089', 'EV-CN-FAQ-0090'] (expected ['EV-CN-FAQ-0089', 'EV-CN-FAQ-0090']), all links noted=True; Group-C chain 0089/0090 superseded_by 0307 |
| C10 | verification 无 pending | PASS | verification={'verified': 392, 'verified_with_changes': 1} (total 393), rules.needs_verification=true remaining=0 |
| C11 | 冲突全部已裁决 | PASS | conflicts=[{'conflict_id': 'CON-4B-T2-0001', 'rule_id': 'R-CR-811.1.b', 'resolution_status': 'resolved_stage5'}] |
| C12 | manual_review 无擅自裁决 (186 项, 全部经正式裁决流程关闭) | PASS | total=186, rule_id NULL=18 (18 document-level: MR-2C x4 + MR-2D x14; MR-2D-0007 rule_id='735.1.c' 为 incorporated 关闭时回填的历史编号), MR-3-CR x161 / MR-4A x6 backfilled; DB 无 status 列, 关闭记录见各 stage 报告 |
| C13 | RCC 链接全部经 4B 裁决 | PASS | faq:rule_change_candidate links=134 (37 source_019 APPLIED + 1 incorporated-not-applied + 90 pre-core 记录未应用 + 6 incorporated CHG-4B-T1F = 134) |

## 补充统计
- changes: 267 行 (CHG-4B-T2ER=222, CHG-4B-T1F=6, CHG-4B-T3=38, CHG-5=1)
- rule_evidence 关系分布: faq:example_only=512, faq:exception=27, faq:rule_change_candidate=134, faq:rule_interpretation=681, front_matter=13, replacement=222, same=4764
- sources date_confidence: confirmed=2, declared=8, inferred=10; version_confidence: inferred=20
- canonical 为空的 rules: 472 条 (FAQ-only R-CARD by design, canonical NULL; 其内容以 official_interpretation/example 挂载形式呈现)
- conflicts: CON-4B-T2-0001 R-CR-811.1.b → resolved_stage5 (CHG-5-0001)

## 结论
全部强制检查 PASS。无未处理 source、无未恢复 failed extraction、无 pending verification。
pipeline 达到 Stage 6 最终构建条件; 剩余 manual_review 项 0 未决 (186 项均已正式裁决并记录)。
已知且有意保留的非阻断事项:
- 4 卡 (OGN-131/OGN-251/UNL-097/UNL-177) zh 文本待官方更新的 watch 记录保留于 REC-4B-T3 notes (现行口径按 source_008 sec.4);
- EV-CN-FAQ-0260 未链接 R-CARD-OGN-251 的 doc-level 警告如实保留;
- manual_review 表无 status 列 — 关闭记录在各 stage 报告中, 6E 将汇总为 manual_review.md;
- R-CR-811.1.b canonical 含 EN 同版本优先补入的持续时段从句 (CHG-5-0001), rules.md 需标注来源。
