# Stage 2B Verification — EN Core Rules (source_018)

Date: 2026-09-20
Source: 07_2026-07-16_Core_Rules.pdf (120 pages), extracted: riftbound_en_rules__07_2026-07-16_Core_Rules.txt

## Result: PASS

- txt numbered entries 2381 == DB rule_number count 2381, identical order, 0 duplicates
- Rule-number sequence identical to CN Core Rules (source_009): EN(2026-07-16) and CN(2026-07-17)
  are structurally the same version (0 only-in-EN, 0 only-in-CN) -> resolves Stage 2A warning
- Page coverage 120/120, no missing pages; every entry's page_start matches the txt parse
- original_text spot-check 8/8 verbatim (whitespace-insensitive containment)
- No NULL original_text / page; semantic fields (trigger/effect/...) intentionally NULL
  (structural extraction only; semantics deferred to Stage 4)
- Official part headers (top_section): 000 / 100 / 300 / 700 / 800 only;
  200 / 400 are real rules (same as CN data after Stage 2A fix)
- heading_candidate flags: 266 (heuristic flags, e.g. rule 054 is a real rule, not a heading)
- Extraction clips: none detected (full-text re-check of every entry's first line)
- EV-EN-CR-0000 front matter: "Riftbound Core Rules / Last Updated: 2026-07-16"
- tasks task_018_01..12: completed; processing_tasks.json synced (completed 25 / pending 18)
- source_018 metadata: rule / en / v2026 / 2026-07-16 confirmed (doc self-states date) / counterpart source_009

## Evidence totals

- source_009 (CN): 2382 rows (EV-CN-CR-0000..2381)
- source_018 (EN): 2382 rows (EV-EN-CR-0000..2381)
- DB total evidence: 4764

Scripts: stage2b_verify.py (verification), stage2b_fix.py (top_section parity with CN fix).
