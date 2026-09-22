# Stage 4B batch 4B-B003 - Tier-2 MR-3-CR tr-diff adjudication

finished_at: 2026-09-22T02:39:48+00:00

Scope: 161 R-CR rules flagged translation_difference(low) in Stage 3 (MR-3-CR-0001..0161). Each zh/en pair re-read in full and adjudicated.

Conventions: canonical=zh official text (CN CR 2026-07-17 postdates EN CR 2026-07-16, same rule version); en=official reference. ALL 161 rules needs_verification=true (spec 15.7 zh/en textual difference).

Verdicts: 160 equivalent_despite_diff; 1 semantic_divergence (MR-3-CR-0130 / R-CR-811.1.b Hidden keyword - EN duration clause "for as long as you control that battlefield" missing in zh official text; conflict CON-4B-T2-0001 -> Stage 5).
Noted example-quote variances: MR-3-CR-0056 (zh quote abbreviates [E] cost prefix), MR-3-CR-0059 (Jinx conditional-clause position, per MR-2D-0004).
4 rules also received tier-1 FAQ attach (5 faq:rule_interpretation entries); R-CR-438.7 keeps VERIF-FLAG pointer for Stage 5.

## stats
```json
{
  "candidates": 161,
  "reconciled": 161,
  "skipped_exists": 0,
  "equivalent": 160,
  "semantic_divergence": 1,
  "conflicts": 1,
  "faq_attached_rules": 4,
  "faq_attached_entries": 5,
  "needs_review": 0,
  "errors": 0
}
```

## validation
```json
{
  "rules_reconciled_total": 2747,
  "rules_pending": 237,
  "rules_needs_review": 0,
  "reconciliations_tier2": 161,
  "mr3cr_closed": 161,
  "mr3cr_rule_id_backfilled": 161,
  "conflicts_total": 1,
  "reconciled_missing_rec": 0,
  "rcr_reconciled_null_text": 0,
  "needs_verification_true": 188,
  "pending_rcr": 19
}
```

## warnings (0)
