Project: Riftbound / LoL TCG Rules Knowledge Base
Current stage: COMPLETE 2026-09-22 — all stages completed; pipeline final.
  No unprocessed source, no failed extraction, no pending verification,
  manual_review 186/186 formally closed (incl. 6F Final Consistency Check 24/24 PASS).

Completed stages:
- Stage 0 - Project Initialization
- Stage 1 - Source Inventory + PDF Preprocessing
- Stage 2A - Chinese Rules Evidence Extraction
- Stage 2B - English Rules Evidence Extraction
- Stage 2C - Errata / Correction Evidence Extraction
- Stage 2D - FAQ / Ruling / Official Explanation Extraction
- Stage 3 - Entity Resolution + Chinese-English Alignment
- Stage 4A - Rule Clustering
- Stage 4B - Rule Reconciliation (COMPLETE 2026-09-22; B006 final batch)
- Stage 5 - Independent Verification (COMPLETE 2026-09-22; task_5_01..05, single-session batches v1/v2/v3)
- Stage 6 - Final Build + Coverage Check (COMPLETE 2026-09-22; task_6_01..06)
  - 6A Coverage Check COMPLETED 2026-09-22 (script stage6a_coverage_check.py idempotent; task_6_01;
    checkpoint workspace/checkpoints/stage6a_checkpoint.json; report workspace/final/coverage_report.md):
    13/13 PASS — sources 20/20 processed, tasks 63/63 completed, evidence mapped 5527/5527,
    rules sourced 2984/2984, errata 156 applied/recorded + 3 front_matter, FAQ/OE 604/604 mounted,
    confirmed dates only doc-self-stated (009/018), derived_interpretation=0,
    superseded only EV-CN-FAQ-0089/0090 (links noted), verification 393 terminal + nv=true 0,
    conflicts 1/1 resolved, manual_review 186 formally closed, RCC 134/134 adjudicated.
  - 6B rules.md COMPLETED 2026-09-22 (script stage6b_build_rules_md.py idempotent; task_6_02;
    checkpoint workspace/checkpoints/stage6b_checkpoint.json; output workspace/final/rules.md ~4.2MB):
    2984 entries regenerated from DB in 4 parts (核心规则 R-CR 2382 / 卡牌 R-CARD 514 /
    主题 R-TOPIC-CN 17 + R-TOPIC-EN 64 / 杂项+前言 7), 每条含 spec 17.2 全部字段,
    472 条 canonical NULL 标记为 FAQ 挂载型记录（未伪造 canonical）,
    R-CR-811.1.b 特别说明 (CHG-5-0001 EN 同版本优先), 4 张观察卡标注 (OGN-131/251, UNL-097/177),
    superseded 链接标注; 图例区分 官方规则/官方解释/模型推导(0)/案例/例外/未解决(0);
    validation PASS (2984 unique entries == DB rule ids, 标记计数核验通过)。
  - 6C rules.db COMPLETED 2026-09-22 (script stage6c_build_rules_db.py idempotent; task_6_03;
    checkpoint workspace/checkpoints/stage6c_checkpoint.json; output workspace/final/rules.db):
    自 rules_work.db 全量幂等重建, 支持 spec-17.2 查询维度 rule_id/topic/card_id/keyword/trigger/source/version —
    rules 2984 (canonical NULL 472 保持 NULL 未伪造), rule_sources 6353 (rule_evidence JOIN evidence;
    索引 source_id/source_document/version), rule_cards 7046 行/661 rules (R-CARD id 解析 +
    evidence.card_ids, 含 T/R/SP 前缀 token/rune/special id), rule_keywords 885 行/83 distinct
    (括号关键字启发式, 费用符号剔除), rules_fts FTS5 可用, rule_verification 393 + rule_changes 267
    全量拷贝, meta 表; validation PASS (orphan 0, 无来源规则 0, malformed 0, 10 项 smoke 查询)。
  - 6D change_log.md COMPLETED 2026-09-22 (script stage6d_build_change_log.py idempotent; task_6_04;
    checkpoint workspace/checkpoints/stage6d_checkpoint.json; output workspace/final/change_log.md ~288KB):
    267 entries 自 changes 表全量幂等重建 (CHG-4B-T2ER 222 勘误应用 / CHG-4B-T1F 6 FAQ 内嵌变更
    incorporated / CHG-4B-T3 38 post-core 官方改动 / CHG-5-0001 验证修复), 每条含 spec-17.2 全部
    11 字段, 按 tier → rule_id 分组 (160 rules affected, 含链式勘误多条依 change_id 排序);
    original_content NULL 38 (new_rule_addition) 显式标记未伪造, version NULL 38 标记 -（无版本）;
    原文/新文以动态长度 fence 包裹零转义; validation PASS (267 ids == DB set, 11 字段标签各 267,
    orphan rule refs 0)。
  - 6E manual_review.md COMPLETED 2026-09-22 (script stage6e_build_manual_review.py idempotent; task_6_05;
    checkpoint workspace/checkpoints/stage6e_checkpoint.json; output workspace/final/manual_review.md ~228KB):
    186 entries 自 manual_review 表全量幂等重建 (MR-2C 4 勘误 / MR-2D 15 FAQ / MR-3-CR 161 中英对齐 /
    MR-4A 6 旧编号) ALL formally closed — issue_description 首个带日期括号处拆分为 问题(原始记录)+裁定结论
    (关闭记录) 逐字呈现, 每条含 spec-17.2 全部 8 字段 + 状态=已关闭(最终关闭日期 09-20 x16 / 09-21 x3 /
    09-22 x167), NULL 字段显式标记 (rule_id NULL 18 来源级问题), 旧规则编号引用 1 条 (MR-2D-0007→735.1.c
    非孤儿); validation PASS (186 ids == DB set, 10 字段标签各 186, 已关闭 186 / 待复盘 0, orphan R-* refs 0)。
  - 6F Final Consistency Check COMPLETED 2026-09-22 (script stage6f_final_consistency.py idempotent,
    只读产物; task_6_06; report workspace/reports/stage6f_final_consistency.md; checkpoint
    workspace/checkpoints/stage6f_checkpoint.json): 24/24 PASS — A rules.md↔DB/rules.db
    (2984 unique ids, 14 字段 x2984, NULL-canonical 472, 状态全终态), B rules.db↔work db
    (rules 2984 / rule_sources 6353 / rule_cards 7046 / rule_keywords 885 / rule_verification 393 /
    rule_changes 267, meta.validation PASS), C change_log.md↔DB/rules.db (267 ids, tiers
    T2ER 222/T1F 6/T3 38/5- 1), D manual_review.md↔DB (186 ids, 已关闭 186 / 待复盘 0),
    E coverage_report.md↔live DB (C1..C13 复核 PASS, 17.1 计数逐项一致), F 跨产物状态一致性
    (spec 17.4: 无 resolved/unresolved 矛盾; verification 392+1 链; conflict resolved_stage5 链;
    changes 267 链; R-CR-811.1.b / CHG-5-0001 链; superseded 0089/0090 标记)。
    -> Stage 6 = completed; Current stage: COMPLETE (spec 17.5)。

Pending stages: none — pipeline COMPLETE

Completed sources:
- source_009 (09_2026-07-23_6f47b6....pdf) = 《符文战场》核心规则 CN, 125p:
  2382 evidence rows (EV-CN-CR-0000 front matter + EV-CN-CR-0001..2381), tasks task_009_01..13 completed.
- source_018 (07_2026-07-16_Core_Rules.pdf) = Riftbound Core Rules EN, 120p:
  2382 evidence rows (EV-EN-CR-0000 front matter + EV-EN-CR-0001..2381), tasks task_018_01..12 completed.
  EN rule-number sequence == CN sequence exactly (2381 entries, 0 diff) -> same rule version confirmed.
- Errata (8 docs, Stage 2C): 156 card_errata evidence rows (zh 93: source_002 31, source_003 31,
  source_004 18, source_010 13; en 63: source_013 31, source_015 16, source_017 8, source_020 8)
  + 3 front_matter rows (source_013/017/020); EV-CN-ER-0001..0093, EV-EN-ER-0001..0066;
  tasks task_002/003/004/010/013/015/017/020_01 completed.
- FAQ / Official Explanation (10 docs, Stage 2D): 594 items + 10 front_matter
  (zh 326: source_001 50, source_005 47, source_006 93, source_007 23, source_008 79, source_011 34;
   en 268: source_012 86, source_014 45, source_016 75, source_019 62);
  EV-CN-FAQ-0001..0332, EV-EN-OE-0001..0272;
  tasks task_001/005/006/007/008/011/012/014/016/019_01 completed (full page coverage);
  4 needs_review entries resolved by human review on 2026-09-20 (needs_review=0).

Pending sources: none (all 20 sources extracted through Stage 2D)

Database:
- workspace/rules_work.db

Important tables:
- sources (20 rows, language/page_count populated for all; all 2D sources carry extraction notes)
- processing_tasks (69 rows: 43 extraction (source_001..020) + 5 stage-3 + 4 stage-4A + 6 stage-4B + 5 stage-5 + 6 stage-6 (task_6_01..06); all completed)
- evidence (5527 rows: 4764 core rules + 156 card_errata + 3 errata front_matter
  + 594 faq/oe items + 10 faq front_matter;
  columns: core + errata (target_rule_candidate ... effective_scope)
  + faq (faq_question/faq_answer/faq_classification/related_cards) + card_ids;
  Stage 3 added notes tags: stage3_entity / stage3_alignment / zh_only_translation)
- alignments (2445 rows: 2382 AL-CR core-rule pairs [equivalent 2221 / translation_difference 161]
  + 63 AL-ER errata pairs [all equivalent/high]; 0 FAQ/OE pairs -- no cross-language counterparts)
- manual_review (186 rows: MR-2C-0001..0004, MR-2D-0001..0015 (all closed incl. 3 Stage-3 deferred,
  closed 2026-09-21), MR-3-CR-0001..0161 (ALL CLOSED 2026-09-22 in 4B-B003, rule_id backfilled);
  MR-4A-0001..0006 ALL CLOSED 2026-09-22 in 4B-B005 successor-coverage verification)
- rules (2984 rows: R-CR x2381 + R-CR-FRONT, R-CARD x514, R-TOPIC-CN x17, R-TOPIC-EN x64,
  R-ER-FRONT, R-FAQ-FRONT, R-MISC x5; ALL 2984 status=reconciled (needs_verification=true now 0),
  pending_reconciliation=0)
- rule_evidence (6353 rows: same 4764, replacement 222, faq:* 1354 (incl. 1 relocated EV-CN-FAQ-0207), front_matter 13)
- reconciliations (2996 rows: 2188 tier-0 + 398 tier-1 + 19 REC-4B-T1F-* + 161 REC-4B-T2-* tr-diff
  + 130 REC-4B-T2ER-* errata + 100 REC-4B-T3-* B006)
- conflicts (1 row: CON-4B-T2-0001 R-CR-811.1.b zh translation omission, RESOLVED_stage5 via CHG-5-0001);
  changes (267 rows: 222 CHG-4B-T2ER-* + 6 CHG-4B-T1F-* + 38 CHG-4B-T3-* [37 source_019 applied
  new_rule_addition + 1 EV-CN-FAQ-0055 incorporated recorded] + 1 CHG-5-0001 811.1.b duration-clause fix);
  verification (393 rows: 392 verified + 1 verified_with_changes; 0 rejected / 0 needs_review / 0 pending)

Statistics:
- sources: 20
- evidence: 5527 (mapped 5527/5527, unmapped 0)
- alignments: 2445
- rules: 2984 (4B COMPLETE: reconciled 2984 / pending 0 / needs_review 0 / needs_verification=true 0)
- rule_evidence: 6353
- reconciliations: 2996
- changes: 267
- conflicts: 1 (CON-4B-T2-0001 resolved_stage5)
- verification: 393 (392 verified + 1 verified_with_changes)
- manual_review: 186 (ALL CLOSED)

Stage 3 results (workspace/reports/stage3_closeout.md; batch reports stage3_er_alignment.md, stage3_faq_alignment.md):
- 3-ENT (task_3_01): card entity resolution, 481 entity-tagged evidence rows
- 3-CR (task_3_02): core rules zh-en aligned by rule_number 2382 pairs; translation_diff 161 flagged
- 3-ER (task_3_03): 63 errata pairs equivalent; 30 zh-only tagged (incl. EV-CN-ER-0059..0062 newly
  confirmed zh_only_translation; EV-CN-ER-0093 VEN-079 corrected mistranslated targeting restriction --
  changes zh effective card text, use corrected text in Stage 4); EN unmatched 0
- 3-FAQ (task_3_04): 0 cross-language pairs (6 signal candidates reviewed+rejected: shared example
  card but different ruling content); all 604 faq/oe rows explicitly tagged; doc-level relations archived
- closeout (task_3_05): MR-2D-0004 closed (trigger-ability condition-clause position = translation
  template variance, not semantic difference); MR-2D-0005 closed (4 cards zh/en divergence documented,
  watch continues; current resolution per source_008 sec.4); MR-2D-0010 closed (previous Origins
  official FAQ external; EN Patch Notes authoritative side -> Stage 4B)
- validation: rule_evidence_unpaired=0, errata_unresolved=0, faq_oe_untagged=0, dup_pairs=0

Stage 2D results (workspace/reports/stage2d_faq_extraction.md):
- 10/10 faq/official_explanation docs extracted: 594 items + 10 front_matter (zh 332 / en 272 rows)
- faq_classification (heuristic): example_only 193, rule_interpretation 270,
  rule_change_candidate 127, exception 5, additional_condition 0, uncertain 0
- rule_change_candidate = Extraction tag only (zh 旧/新对照 与 规则(修订后); en NEW RULE/SYSTEM/EDIT/REMOVAL);
  NO canonical rule modifications (Reconciliation responsibility)
- 4 needs_review items human-reviewed & fixed 2026-09-20 (0169 A1 prefix restored,
  0248->merged into 0247, 0263 verified, 0264/0265 scene-line relocated); needs_review=0
- typo 'Q：可以。' auto-merged w/ note
- 15 manual_review entries: date conflicts (001/006/008/014/016/019), FAQ-supersession (011>005),
  735.1.c core-rule revision via FAQ, FAQ-embedded errata cross-refs, authority/expiry declarations,
  008 sec.4 zh-en text divergences, judge-FAQ authority level, prose-entry classification heuristics
- cards_bilingual.db used ONLY for card-name -> card_key alignment (related_cards / card_ids)

Stage 2B verification results (workspace/reports/stage2b_en_rules_verification.md):
- EN txt numbered entries 2381 == DB rule_number count 2381, identical order, 0 duplicates
- EN-CN rule-number sequences identical -> EN(2026-07-16) and CN(2026-07-17) are the same rule version
- Page coverage 120/120; page_start matches re-parse; no extraction clips detected
- original_text spot-check 8/8 verbatim
- Semantic fields (trigger/effect/...) intentionally NULL: structural extraction only; semantics deferred to Stage 4
- Official part headers only 000/100/300/700/800 (200/400 are real rules; flags fixed for CN parity)
- EV-EN-CR-0000 = "Riftbound Core Rules / Last Updated: 2026-07-16"

Stage 2A verification results:
- CN txt numbered entries 2381 == DB rule_number count 2381, identical order, 0 duplicates
- Page coverage 125/125
- original_text spot-check 5/5 verbatim

Corrections made so far:
- source_009 -> rule/zh, date 2026-07-17 confirmed; source_010 -> errata/zh; source_011 -> faq/zh (Stage 2A)
- source_018 -> language en, date 2026-07-16 confirmed (doc self-states Last Updated date) (Stage 2B)
- source_009 <-> source_018 marked as possible_counterpart
- EN top_section flags on 200/400 removed for parity with CN (they are real rules, not headers)
- Stage 2C: source_002/003/004 -> errata/zh; source_013/015/017 -> language en
- Stage 2C: task_002_01 page_end 10->13, task_003_01 10->14, task_013_01 10->14 (full coverage)
- Stage 2D: source_012 reclassified rule->official_explanation (Core Rules Patch Notes)
- Stage 2D: task_005/006/007/008/011_01 page_end -> 21/25/24/24/22 (full coverage)
- 2026-09-20 4 needs_review FAQ entries human-fixed (0248 merged into 0247, 0169 A1 prefix,
  0263 verified, 0264/0265 scene-line relocated); zh ids renumbered 0001..0332
- 2026-09-20 Group-A date rulings: 001/006/008 -> doc-internal dates (2025-10-23/2026-01-14/2026-05-11,
  file-name dates demoted to notes); 013 -> 2025-10-21 (in-page Last Updated);
  016 -> 2026-03-31, 020 -> 2026-07-24 (byline); 014/019 effective_date -> declared
  2025-12-12 / 2026-07-24; date_confidence=declared for all 8; evidence.date synced;
  MR-2C-0002/0003 + MR-2D-0001/0002/0003/0011 closed
- 2026-09-20 Group-B rulings: MR-2C-0001/0004 adjudicated zh-only (21 errata rows tagged
  zh_only_translation incl. source_003 19 translation-fix cards + source_004 沉没神庙/遗忘丰碑);
  MR-2D-0008 closed after row-level comparison: 21 FAQ-embedded errata mentions all consistent
  with 2C (005 18/18 exact-or-superset, 008 沙丘亚龙 semantic-identical w/ note,
  008 永恩 partial-quote noted, 011 星界灵鹭 consistent); cross_ref_errata/cross_ref_faq
  pointers established on 21 FAQ rows / 20 errata rows (永恩 referenced twice)
- 2026-09-20 Group-C rulings: authority topology adjudicated (current core rules >
  transitional official FAQ/Patch Notes until next core release > later-FAQ-supersedes-earlier
  > judge-FAQ community tier) closing MR-2D-0009/0013; supersession chain built
  (005 0089/0090 superseded_by=0307) closing MR-2D-0006; MR-2D-0007 closed as incorporated
  (FAQ 735.1.c revision absorbed into 2026-07 core rules as 809.1.c, renumbered/restructured);
  MR-2D-0012 closed (Unleashed FAQ is an external doc not in this corpus; declaration archived
  as reconciliation metadata in 019 front_matter); MR-2D-0015 closed (007 prose classifications
  reviewed: 9 rows, distribution reasonable); 0307/0308 question-boundary fracture fixed;
  MR-2D-0004/0005/0010 deferred to Stage 3 with evidence watch-tags
  (cross_language_note / pending_zh_text_update / superseded-marking procedure)

Stage 4A results (workspace/reports/stage4a_rule_clustering.md; scripts stage4a_cluster.py, stage4a_fix.py;
tasks task_4a_01..04 completed):
- All 5527 evidence mapped to 2984 clusters; unmapped=0, dup links=0, rules w/o evidence=0
- Core rules: 2381 R-CR clusters zh+en merged (161 tr-diff pairs tagged in rule_evidence.notes)
- Cards: 514 R-CARD clusters (errata 130 + FAQ-only 384); errata linked as 'replacement'
- FAQ/OE linked via rule-ref (45) / card (1035) / topic-cluster R-TOPIC (81; 17 zh + 64 en) / R-MISC (5 src buckets, 17 rows);
  faq:* relationship keeps Stage 2D classification for 4B
- 25 pre-created topic clusters w/o members pruned
- MR-4A-0001..0006: FAQ refs to rule numbers absent from 2026-07 core rules (stale numbering) -> 4B;
  ADJUDICATED 2026-09-21 with successor mappings; ALL CLOSED 2026-09-22 in 4B-B005
  (successor coverage verified):
  376.3->383.3.d.1; 322.2/322.3/322.8->318 清理+324 特殊清理; 旧440.1.x->466.1.a;
  735.1.c->809.1.c (full, text verbatim); 460.2.c.3->465.2.c.4(.a) (323.5 verified current, no remap);
  335.3->334 HOT FEPR (+335-336)
- 23 explicit-ref rule_evidence links from pre-renumbering judge sources (001 x5, 007 x18) tagged
  'VERIFICATION FLAG 4B' (matched number may denote a different rule; e.g. 440.1 burn vs old battle-cleanup)

Stage 4B batches:
- 4B-B001 tier-0 (2026-09-21, script stage4b_reconcile.py idempotent; task_4b_01;
  report workspace/reports/stage4b_tier0_reconciliation.md; checkpoint workspace/checkpoints/stage4b_tier0_checkpoint.json):
  2188 R-CR rules reconciled (canonical=zh official text; en=official reference -- same rule version confirmed;
  reconciliation rows REC-4B-T0-*; needs_verification=false because equivalents w/o modifiers).
  0 needs_review / 0 errors.
- 4B-B002 tier-1 FAQ-attach (2026-09-21, script stage4b_tier1_faq.py idempotent; task_4b_02;
  report workspace/reports/stage4b_tier1_faq_attach.md; checkpoint workspace/checkpoints/stage4b_tier1_checkpoint.json):
  398 rules reconciled = 384 FAQ-only R-CARD (canonical NULL by design) + 14 clean FAQ-linked R-CR (canonical=zh).
  Verbatim attach w/ [evidence_id|source_id|tier|class] prefixes: 408 example_only->example,
  399 rule_interpretation->official_interpretation (judge-community tier for source_001/006/008 per MR-2D-0013),
  22 exception->exception (+needs_verification); 10 faq:rule_change_candidate links NOT applied,
  recorded in REC-4B-T1-* original_fragment (+needs_verification). needs_verification=true x27.
  0 needs_review / 0 errors. (sandbox retry zeroed run-stats in files; real stats recovered from DB.)
- 4B-B003 tier-2 MR-3-CR tr-diff adjudication (2026-09-22, script stage4b_tier2_trdiff.py idempotent;
  task_4b_03; report workspace/reports/stage4b_tier2_trdiff.md; checkpoint
  workspace/checkpoints/stage4b_tier2_trdiff_checkpoint.json; pair dump + verdict inputs
  workspace/checkpoints/stage4b_tier2_trdiff_pairs.json):
  all 161 zh/en pairs re-read in full + adjudicated: 160 equivalent_despite_diff (orthographic only:
  Chinese numerals vs digits / keyword brackets translated inline / placeholder brackets);
  1 semantic_divergence = MR-3-CR-0130 R-CR-811.1.b (Hidden): EN trailing clause
  "for as long as you control that battlefield" absent in zh official text -> conflict
  CON-4B-T2-0001 (translation_omission, pending_stage5). canonical=zh (convention);
  ALL 161 needs_verification=true (spec 15.7 zh/en textual difference).
  4 rules also tier-1 FAQ-attached (5 faq:rule_interpretation entries); R-CR-438.7 keeps
  VERIF-FLAG pointer. MR-3-CR-0001..0161 all closed in-place + rule_id backfilled.
  Noted example-quote variances: MR-3-CR-0056 (zh quote abbreviates [E] cost prefix),
  MR-3-CR-0059 (Jinx conditional-clause position, per MR-2D-0004). 0 needs_review / 0 errors.
- 4B-B004 tier-2 R-CARD errata application (2026-09-22, script stage4b_tier2_errata.py idempotent;
  task_4b_04; report workspace/reports/stage4b_tier2_errata.md; checkpoint
  workspace/checkpoints/stage4b_tier2_errata_checkpoint.json):
  130 R-CARD errata rules reconciled. canonical = corrected_fragment of LATEST zh official errata
  (official errata evidence only, per spec 12.4 cards db not a rules source; cards db
  text_cn/errata_cn probe showed 31/130 keys missing post-errata text -> not usable as canonical).
  137 zh errata links applied, 7 rules chained x2 (date-asc; canonical = last link);
  85 EN counterpart errata recorded w/o canonical change; 222 changes rows CHG-4B-T2ER-*
  (per errata evidence x rule, incl. EV-CN-ER-0093 VEN-079 zh_only_translation fix).
  FAQ attach on same 130 rules per tier-1 conventions: 104 example + 103 rule_interpretation
  + 4 exception; 1 rule_change_candidate (R-CARD-UNL-106 / EV-EN-OE-0269) NOT applied, recorded.
  ALL 130 needs_verification=true (spec 15.7 errata-modified) -> total 318.
  1 chain warning (R-CARD-UNL-186 EV-CN-ER-0034->0090 wording drift 3[M] vs 3 战力, expected).
  canonical == latest zh corrected_fragment verified 130/130. 0 needs_review / 0 errors.
  (sandbox retry zeroed run-stats in files; real stats recovered from DB, same incident as 4B-B002.)
  First validation via script-run also confirmed: reconciled 2877, pending 107, changes 222, rec 130.
- 4B-B005 tier-1 flagged R-CR (2026-09-22, script stage4b_tier1_flagged.py idempotent; task_4b_05;
  dump workspace/checkpoints/stage4b_b005_dump.json; report workspace/reports/stage4b_tier1_flagged.md;
  checkpoint workspace/checkpoints/stage4b_tier1_flagged_checkpoint.json):
  19 VERIF-FLAG R-CR adjudicated w/ full-text reads + current-number-space existence checks:
  12 attach (valid citations) -> 11 official_interpretation + 1 exception entries;
  7 stale_note (number reused/absent; successors verified: 187.4.c->323.6, 316.5.b->323.8,
  333.1.c.3->340.4, 342.1.a->383.4.f/466.x, 376.3.b.1->383.3.d.1, 440.1.a(.b)->466.1.a/318/324.1,
  460.2.c.3->465.2.c.4(.a), 466.1.b->471.1.b.1; content NOT written to wrong clusters);
  6 RCC links (source_007 0196 x5 + 0201) ALL INCORPORATED into 2026-07 core (recorded via
  CHG-4B-T1F-0001..0006, NOT applied); EV-CN-FAQ-0207 relocated R-CR-187.4 -> R-CR-323.6.
  MR-4A-0001..0006 ALL CLOSED (successor coverage verified); R-CR-438.7 flag cleared (citation valid).
  needs_verification: 14 true / 5 false. canonical=zh everywhere. 0 needs_review / 0 errors.
  (sandbox retry re-ran script, same incident as B002/B004; stats in files corrected from DB.)
  Scope decision: remaining 128 RCC links attach to R-TOPIC-EN (100) / R-MISC (16) / R-CARD (11) /
  R-TOPIC-CN (1) rules -> adjudicated together with those rules in 4B-B006 (includes MR-2D-0010
  patch-notes authority: 012/014/016 transitional < 2026-07 core; 019 eff 2026-07-24 post-dates core
  = authoritative side to apply).
  Remaining pending 88 rules: 81 R-TOPIC (17 CN + 64 EN), 5 R-MISC, R-ER-FRONT, R-FAQ-FRONT.
- 4B-B006 tier-3 topic/misc/front + RCC (2026-09-22, script stage4b_b006_reconcile.py idempotent;
  task_4b_06; report workspace/reports/stage4b_b006_topic_misc_front.md;
  checkpoint workspace/checkpoints/stage4b_b006_checkpoint.json):
  88/88 pending rules reconciled (pending_reconciliation=0 -> Stage 4B COMPLETE).
  128 RCC links adjudicated: 37 source_019 (post-core Vendetta eff 2026-07-24) APPLIED as official
  changes (38 CHG-4B-T3 rows incl. 1 EV-CN-FAQ-0055 INCORPORATED into 809.1.c recorded-not-applied;
  applied text attached verbatim w/ 'APPLIED post-core official change' prefix);
  90 source_012/014/016 transitional pre-core NOT applied (authority superseded by 2026-07 core;
  recorded in REC; Stage 5 spot-check). 156 faq:rule_interpretation entries attached verbatim.
  11 RCC links on 8 already-reconciled R-CARD rules adjudicated w/o touching B002/B004 canonical.
  MR-2D-0005 watch fold-in: OGN-131/OGN-251/UNL-097/UNL-177 REC-4B-T3 rows + nv=true
  (zh FAQ sec.4 现行口径, EN authority reference, pending zh errata).
  100 REC-4B-T3 rows; nv=true 332->393. 0 needs_review / 0 errors.
  Warning: EV-CN-FAQ-0260 not linked to R-CARD-OGN-251 (doc-level, noted in REC; links unchanged).

Stage 5 results (2026-09-22, script stage5_verify.py idempotent batches setup/v1/v2/v3/validate +
stage5_finalize.py; tasks task_5_01..05 ALL completed; report workspace/reports/stage5_verification.md;
checkpoint workspace/checkpoints/stage5_checkpoint.json):
- Scope: 393 nv=true rules + conflict CON-4B-T2-0001; verification table extended
  (stage4_conclusion/verification_conclusion/relevant_evidence/disagreement_reason/verified_at).
- Outcome: 393 verification rows = 392 verified + 1 verified_with_changes; 0 rejected / 0 needs_review /
  0 failed / 0 pending; needs_verification='true' remaining 0; per-rule COMMIT.
- v1 (160 tr-diff R-CR): canonical==zh official evidence verbatim (回查 same-linked EV-CN-CR), en links
  present, REC-4B-T2 verdicts intact, FAQ attaches verbatim -> verified x160.
- v2 (130 errata R-CARD): canonical==latest zh errata corrected_fragment (date-asc, incl. 7 two-link
  chains), CHG-4B-T2ER rows == replacement links (137 zh applied + 85 en recorded), errata scope NOT
  expanded, FAQ attaches verbatim -> verified x130.
- v3 (102 mixed + conflict): 30 FAQ-only cards (canonical NULL by design), 14 T1F flagged (B005
  stale-ref NULL fields confirmed intentional; 0206->816.2 / 0207->323.6 relinks verified), 57-ish T3
  topic/misc buckets: RCC 134 links coverage verified (source_019 eff 2026-07-24 post-core APPLIED w/
  verbatim '[eid|...|APPLIED post-core official change]' attach + CHG-4B-T3; source_012/014/016
  transitional pre-core NOT applied, date-logic independently re-checked; source_005/007 INCORPORATED
  w/ CHG rows; 0055 vs current 809.1.c semantic equivalence re-confirmed).
- CON-4B-T2-0001 (R-CR-811.1.b Hidden): EN same-version duration clause "for as long as you control
  that battlefield" omitted in zh official translation; per spec 2.4/15.4 (same version: EN>zh) canonical
  supplemented with zh rendering ('此牌保持正面朝下待命状态，直至你不再控制该战场'); CHG-5-0001
  (condition_change); conflict resolved_stage5; no manual_review (evidence decisive).
- MR-2D-0005 watch cards (OGN-131/251, UNL-097/177): verified w/ documented divergence notes; current
  ruling per source_008 sec.4, pending zh-text-update tracked in REC notes.
- derived_interpretation=0 rows confirmed DB-wide (no FAQ over-generalization ever materialized).
- Note: v3 first pass flagged 23 needs_review -- ALL were checker-form false positives (count-style REC
  rows vs per-eid OI attach / intentional NULL on stale-ref), fixed check logic, re-ran -> all pass;
  no data changes needed beyond the 811.1.b fix.

Known warnings:
- 161 MR-3-CR tr-diff pairs: CLOSED 2026-09-22 (4B-B003; 160 equivalent + 1 conflict CON-4B-T2-0001);
  4 cards pending_zh_text_update watch (MR-2D-0005);
  authority handoff for source_012 Patch Notes to Stage 4B (MR-2D-0010)
- evidence rows carry notes='structural_extraction'; 'heading_candidate' flags are heuristic (e.g. rule 054 is a real rule)
- kb/core_rules_cn.json / core_rules_en.json are older prep artifacts without page info; evidence table is authoritative
- EN and CN are now confirmed same rule version; Stage 3 still must check translation-level differences
- Errata modification_type is heuristic (notes: modification_type_source: heuristic)
- EN errata site exports (source_017/020) contained footer/sidebar noise, filtered during parse
- FAQ aggregation sources (001/006/008 judge FAQ) declare 'not official FAQ' -> authority tier flagged in MR-2D-0013
- date fields adjudicated 2026-09-20 (Group A rulings in sources.notes 'Date ruling');
  Group B (cross-source consistency) closed 2026-09-20: zh-only errata tagged, cross_ref pointers built;
  Group C resolved 2026-09-20: authority topology ruled, supersession/incorporation chains built;
  no unresolved manual_review remains — 3 items formally deferred to Stage 3 with watch-tags
  (MR-2D-0004 cross-language, MR-2D-0005 pending zh text update, MR-2D-0010 Origins-FAQ conflicts)
  -> all 3 closed with Stage 3 findings 2026-09-21

Next recommended action:
None — pipeline COMPLETE 2026-09-22 (per spec 17.5)。最终产物 (workspace/final/):
- rules.md (2984 entries), rules.db (FTS5 可查), change_log.md (267), manual_review.md
  (186 全部已关闭), coverage_report.md (13/13 PASS); 事实来源 workspace/rules_work.db。
- 验证手段: 6F stage6f_final_consistency.py (idempotent, 24/24 PASS) 可随时重跑复核
  五产物与 DB 的一致性。
已知且有意保留的非阻断事项 (见 coverage_report.md 结论节):
- 4 卡 (OGN-131/OGN-251/UNL-097/UNL-177) zh 文本待官方更新的 watch 记录保留于 REC-4B-T3 notes;
- EV-CN-FAQ-0260 未链接 R-CARD-OGN-251 的 doc-level 警告如实保留;
- R-CR-811.1.b canonical 含 EN 同版本优先补入的持续时段从句 (CHG-5-0001), rules.md 已标注。
Reusable scripts in repo root: stage2a_extract_zh_rules.py, stage2a_fix.py, stage2a_verify.py,
stage2a_finalize.py, stage2b_verify.py, stage2b_fix.py, stage2c_extract_errata.py,
stage2d_extract_faq.py, stage2d_manual_review.py, stage2d_finalize.py, stage2d_renumber.py,
stage3_er_pair.py, stage3_er_apply.py, stage3_faq_candidates.py, stage3_closeout.py,
stage4a_cluster.py, stage4a_fix.py, stage4b_reconcile.py, stage4b_tier1_faq.py,
stage4b_tier2_trdiff.py, stage4b_tier2_errata.py, stage4b_b005_dump.py, stage4b_tier1_flagged.py,
stage4b_b006_probe*.py, stage4b_b006_reconcile.py, stage4b_b006_taskreg.py, stage4b_b006_verify.py,
stage5_verify.py, stage5_finalize.py, stage6a_coverage_check.py, stage6b_build_rules_md.py,
stage6c_build_rules_db.py, stage6d_build_change_log.py, stage6e_build_manual_review.py,
stage6f_final_consistency.py
(stage4a_inspect*.py / stage4b_b006_show.py are throwaway probes; stage5_probe*/stage5_counts.py
and stage6d_inspect.py were throwaway probes and have been removed; 6F 前的临时探针
stage6f_probe.py 已删除).
