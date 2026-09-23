# Stage 6F — Final Consistency Check (spec 17.4)

- 执行时间: 2026-09-23T12:44:15  脚本: stage6f_final_consistency.py (幂等, 只读产物)
- 数据源: workspace/rules_work.db (事实来源) + workspace/final/{rules.md, rules.db, change_log.md, manual_review.md, coverage_report.md}
- 结论: **全部检查 PASS** (24/24)

| ID | 检查项 | 结果 | 明细 |
|---|---|---|---|
| F0 | 五个最终产物齐备且非空 | PASS | missing=[] |
| A1 | rules.md 条目数/ID 集合 == DB rules == rules.db | PASS | file=2984 distinct=2984 db=2984 rules_db=2984 |
| A2 | rules.md 每条含 9 个恒显字段；结构化五字段 DB 全 NULL 且条目级行已省略 | PASS | expected=2984 each (9 fields); bad=[]; struct_md_lines=[]; struct_db_nonempty=0 |
| A3 | rules.md NULL-canonical 标记数 == DB NULL canonical（两者一致） | PASS | markers=472 db_null=472 rules_db_null=472 |
| A4 | rules.md 每条状态均为终态（无未解决/待验证） | PASS | status_lines=2984 unresolved=[] |
| B1 | rules.db 各表计数 == rules_work.db | PASS | {"rules_db": {"rules": 2984, "rule_sources": 6353, "rule_cards": 7046, "rule_keywords": 885, "rule_verification": 393, "rule_changes": 267, "null_canon": 472}, "db": {"rules": 2984, "rule_evidence": 6353, "verification": 393, "changes": 267 |
| B2 | rules.db meta.validation PASS | PASS | builder=stage6c_build_rules_db.py (idempotent full rebuild) |
| B3 | verification 状态分布一致 (verified=392, verified_with_changes=1) | PASS | work={'verified': 392, 'verified_with_changes': 1} rules_db={'verified': 392, 'verified_with_changes': 1} nv_true=0 |
| C1 | change_log.md 条目 ID 集合 == DB changes == rules.db rule_changes | PASS | file=267 distinct=267 db=267 rules_db=267 |
| C2 | change_log.md 总数声明 267 且 tier 分布与文件/DB 一致 | PASS | claim=267 tiers={'T2ER': 222, 'T1F': 6, 'T3': 38, '5': 1} |
| D1 | manual_review.md 条目 ID 集合 == DB manual_review | PASS | file=186 db=186 |
| D2 | manual_review.md 全部已关闭（无待复盘） | PASS | closed=186 pending=0 |
| E0 | coverage_report.md 强制检查清单 13 行全 PASS | PASS | rows=13 fail=[] |
| E1 | coverage: Documents discovered/processed/failed == DB | PASS | doc=20/20/0 db=20/20 bad_tasks_x6f=0 |
| E2 | coverage: Evidence extracted/mapped/unmapped == DB | PASS | 5527/5527/0 |
| E3 | coverage: Rules generated/verified == DB | PASS | generated=2984 verified=393 dist={'verified': 392, 'verified_with_changes': 1} |
| E4 | coverage: Errata applied / FAQ attached / Rulings attached == DB | PASS | errata_zh=137 faq=1354 rulings=225/225 |
| E5 | coverage: Conflicts resolved/unresolved、Manual review items == DB | PASS | conflicts=1/0 mr=186 |
| F1 | manual_review 全部关闭 ⟷ rules.md 无未决 ⟷ coverage C12 PASS（无 resolved/unresolved 矛盾） | PASS | mr_closed=186/186 rules_unresolved=0 c12=PASS |
| F2 | rules.md 统计声明 == DB verification 分布 == rules.db == coverage | PASS | rules_md_claims=True dist={'verified': 392, 'verified_with_changes': 1} |
| F3 | conflicts 状态一致: DB resolved_stage5 ⟷ rules.md 图例 ⟷ coverage 1/0 | PASS | [{"conflict_id": "CON-4B-T2-0001", "rule_id": "R-CR-811.1.b", "resolution_status": "resolved_stage5"}] |
| F4 | changes 计数一致: change_log 267 ⟷ DB ⟷ rules.db ⟷ coverage | PASS | changes=267 |
| F5 | R-CR-811.1.b 链一致: rules.md verified_with_changes ⟷ change_log CHG-5-0001 ⟷ DB | PASS | verification=['verified_with_changes'] chg5=yes |
| F6 | superseded 标记一致: rules.md [superseded-已被取代] >=2 ⟷ coverage C9 指向 EV-CN-FAQ-0089/0090 | PASS | markers=15 |

## 互查矩阵摘要

- rules.md: 2984 entries == rules 2984 == rules.db 2984; 14 字段齐全; NULL-canonical 标记 472 == DB 472
- change_log.md: 267 entries == changes 267 == rules.db 267; tiers {'T2ER': 222, 'T1F': 6, 'T3': 38, '5': 1}
- manual_review.md: 186 entries == manual_review 186; 已关闭 186, 待复盘 0
- coverage_report.md: C1..C13 PASS; 计数与 DB 逐项一致 (docs 20/20, evidence 5527/5527, rules 2984, verified 393, conflicts 1/0, mr 186)
- rules.db: rules/2984 rule_sources/6353 rule_cards/7046 rule_keywords/885 rule_verification/393 rule_changes/267; meta.validation.PASS=True

spec 17.4 互查要求: rules.md / rules.db / change_log.md / manual_review.md / coverage_report.md 数量与状态一致 — 达成。
