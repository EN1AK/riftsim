# Stage 4B batch 4B-B002 - Tier-1 mechanical FAQ attach

finished_at: 2026-09-21T11:35:04+00:00
script: stage4b_tier1_faq.py (idempotent); task_4b_02

Scope: FAQ-only R-CARD (no errata links, 384) + clean FAQ-linked R-CR
(no replacement / tr-diff / VERIFICATION-FLAG links, 14).

Attach rules (verbatim, deterministic rebuild from current links):
- faq:example_only -> rules.example
- faq:rule_interpretation -> rules.official_interpretation
- faq:exception -> rules.exception + needs_verification=true
- faq:rule_change_candidate -> NOT written into rule fields (never modifies
  canonical); recorded in reconciliation.original_fragment + needs_verification=true
- every entry prefixed [evidence_id | source_id | tier | class];
  tier=judge-community for source_001/006/008 (MR-2D-0013 self-declared
  "not official FAQ"); judge-tier rule_interpretation forces needs_verification=true
- R-CR: canonical = zh official text (same-version equivalent pair, tier-0 convention)
- FAQ-only R-CARD: no rule text exists; canonical stays NULL by design

## stats
```json
{
  "candidates_rcard": 384,
  "candidates_rcr": 14,
  "reconciled": 398,
  "skipped_exists": 0,
  "needs_review": 0,
  "errors": 0,
  "flagged_verification": 27,
  "example_entries": 408,
  "interpretation_entries": 399,
  "exception_entries": 22,
  "rule_change_links": 10
}
```
(note: sandbox auto-retry reran the script after the first full pass; the
second pass found 0 pending candidates and overwrote task notes / checkpoint
with zeros. Values above were recovered from DB: sums of
reconciliations.original_fragment counters + rules.needs_verification.)

## validation
```json
{
  "rules_reconciled_total": 2586,
  "rules_pending": 398,
  "rules_needs_review": 0,
  "reconciliations_tier1": 398,
  "reconciled_missing_rec": 0,
  "rcr_reconciled_null_text": 0,
  "rcard_faqonly_null_text_expected": 384,
  "needs_verification_true": 27
}
```

## warnings
- none

## rule_change_candidate links deferred to Stage 5 (10, recorded in REC rows)
These remain linked via rule_evidence (faq:rule_change_candidate) and are
explicitly listed in each rule's reconciliation.original_fragment. Canonical
text was NOT modified by FAQ content anywhere in this batch.
