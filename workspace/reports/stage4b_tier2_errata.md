# Stage 4B batch 4B-B004 - Tier-2 errata application (130 R-CARD)

finished_at: 2026-09-22T03:05:44+00:00
(run-stats recovered from DB after sandbox retry zeroed first-run files; same incident as 4B-B002)

Scope: 130 pending R-CARD rules with errata `replacement` links (script stage4b_tier2_errata.py, task_4b_04).
canonical = corrected_fragment of LATEST zh official errata (date-asc chain check, warning-only). EN errata recorded in changes w/o canonical change (paired zh governs). zh_only_translation errata applied like normal zh errata (they correct zh effective text). changes rows CHG-4B-T2ER-* per errata evidence x rule (222). FAQ attach on the same 130 rules per tier-1 conventions; rule_change_candidate NOT applied. ALL 130 needs_verification=true (spec 15.7 errata-modified).

## stats
```json
{
  "candidates": 130,
  "reconciled": 130,
  "errors": 0,
  "changes_added": 222,
  "zh_errata_links": 137,
  "en_errata_links": 85,
  "chained_rules": 7,
  "faq_example": 104,
  "faq_interpretation": 103,
  "faq_exception": 4,
  "faq_rcc": 1,
  "faq_forced_verif": 10
}
```

## validation
```json
{
  "rules_reconciled_total": 2877,
  "rules_pending_left": 107,
  "needs_review": 0,
  "rcard_errata_reconciled": 130,
  "changes_rows_batch": 222,
  "rec_rows_batch": 130,
  "errata_rules_missing_changes": 0,
  "needs_verification_true_total": 318,
  "all_130_needs_verification": 130
}
```

## warnings (1)
- R-CARD-UNL-186: errata chain mismatch EV-CN-ER-0034->EV-CN-ER-0090
