# Stage 4B batch 4B-B005 - Tier-1 flagged R-CR reconciliation (VERIF-FLAG adjudication)

finished_at: 2026-09-22T06:12:25+00:00

Scope: 19 pending R-CR with VERIF-FLAG links + 6 R-CR rule_change_candidate links (source_007) + MR-4A-0001..0006 closure + R-CR-438.7 flag clear.

Authority: current 2026-07 core rules (source_009/018) > source_007 (2026-04-30) / source_001 (judge-community). canonical = zh official text. RCC links all INCORPORATED (recorded via CHG-4B-T1F-0001..0006, NOT applied).
Remaining 128 faq:rule_change_candidate links attach to R-TOPIC-EN (100), R-MISC (16), R-CARD (11), R-TOPIC-CN (1) rules -> deferred to next batch with those rules (incl. MR-2D-0010 patch-notes adjudication: 012/014/016 transitional < current core; 019 post-dates core -> authoritative side).

## verdicts per rule
- R-CR-135.4 (needs_verification=False)
  - EV-CN-FAQ-0205: attach -- cites 135.4 + 718.2 verbatim; valid in current numbering
- R-CR-187.4 (needs_verification=True)
  - EV-CN-FAQ-0196: incorporated -- old 187.4.c battlefield-control rule no longer exists (187.4 = Mech token def); contradiction with cleanup rule resolved: control-loss consolidated at 323.6 new text
  - EV-CN-FAQ-0206: stale_note -- cites old 187.4.c (open-state control); successor = 323.6; same evidence validly attached to R-CR-816.2 (816.2/816.2.a verbatim)
  - EV-CN-FAQ-0207: stale_note -- cites old 187.4.c (chain-not-empty blocks control loss); successor = 323.6; interpretation relocated to R-CR-323.6 (new link, 4B-B005)
- R-CR-316.5 (needs_verification=True)
  - EV-CN-FAQ-0196: incorporated -- cited 316.5.b old showdown-marking text; 316.5.b now = Neutral Open State def; marking rule relocated to 323.8 with the NEW text verbatim
- R-CR-317.2 (needs_verification=True)
  - EV-CN-FAQ-0030: attach -- [317.2.a] exists in current numbering; [440.1.a] STALE -> successor 466.1.a (MR-4A-0002); judge-community tier
- R-CR-323.1 (needs_verification=True)
  - EV-CN-FAQ-0203: attach -- cites 323.1 verbatim + 467 (exists); 466.1.b sub-ref STALE -> successor 471.1.b.1 (verified: not-scored-everywhere -> draw a card)
- R-CR-323.5 (needs_verification=True)
  - EV-CN-FAQ-0198: attach -- cites 323.5 (content-equivalent, reworded w/ 142.4 ref); 460.2.c.3 STALE -> successor 465.2.c.4(.a) verified (MR-4A-0005)
- R-CR-323.6 (needs_verification=True)
  - EV-CN-FAQ-0196: incorporated -- NEW text present in current 323.6 (minor reword, same condition); canonical unchanged
  - EV-CN-FAQ-0207: attach_relocated -- relocated from R-CR-187.4 (stale ref 187.4.c -> successor 323.6); content = open-state control retention while chain items pending
- R-CR-323.8 (needs_verification=True)
  - EV-CN-FAQ-0196: incorporated -- current 323.8 text == 316.5.b NEW text verbatim (marking relocated here); canonical unchanged
- R-CR-333.1 (needs_verification=True)
  - EV-CN-FAQ-0020: stale_note -- cites [333.1.c.3] priority rule; current 333.1 = task list; successor = 340.4 (verified verbatim); judge-community tier
- R-CR-342.1 (needs_verification=True)
  - EV-CN-FAQ-0011: stale_note -- cites [342.1.a] + [376.3.b.1]; 342.1.a gone (342.1 = spell-chain creation); successors: 376.3.b.1 -> 383.3.d.1 (verified), defender-last -> 383.4.f + 466.x (MR-4A-0001); judge-community tier
- R-CR-344.2 (needs_verification=True)
  - EV-CN-FAQ-0196: incorporated -- NEW text present in current 344.2 (with extra Neutral Open State qualifier); canonical unchanged
- R-CR-359.3 (needs_verification=True)
  - EV-CN-FAQ-0213: attach -- exception; cites 359.3.e.3 verbatim (exists); valid
  - EV-CN-FAQ-0300: attach -- cites 359.3.f.1/f.2/f.3/f.3.b (all exist); valid
  - EV-CN-FAQ-0321: attach -- cites 359.3.f.3 (exists); valid
- R-CR-437.2 (needs_verification=False)
  - EV-CN-FAQ-0210: attach -- cites 437.2.a (exists, damage prevented to 0 = no damage dealt); valid
- R-CR-438.1 (needs_verification=False)
  - EV-CN-FAQ-0204: attach -- cites 438.1 verbatim + 438.7.b (exists); valid
- R-CR-440.1 (needs_verification=True)
  - EV-CN-FAQ-0030: stale_note -- cites [440.1.a] = old battle-cleanup specials; 440.1 = Burn now; successor 466.1.a (+318/324.1); judge-community tier
  - EV-CN-FAQ-0031: stale_note -- cites [440.1.a.1-3]/[440.1.b] old battle cleanup; successors 466.1.a/466.1.a.1/.2 + 318 (MR-4A-0002); judge-community tier
- R-CR-461.3 (needs_verification=True)
  - EV-CN-FAQ-0201: incorporated -- cited 461.3.d old battle-outcome text; NEW text present verbatim at 466.3.d (incl. recalled-units clause); 461.3 now = combat showdown opening; canonical unchanged
- R-CR-466.1 (needs_verification=True)
  - EV-CN-FAQ-0203: stale_note -- cites 466.1.b scoring-action quote; current 466.1 = combat cleanup; successor = 471.1.b.1 (verified); same evidence validly attached to R-CR-323.1
- R-CR-718.2 (needs_verification=False)
  - EV-CN-FAQ-0205: attach -- cites 718.2 verbatim + 135.4; valid in current numbering
- R-CR-816.2 (needs_verification=False)
  - EV-CN-FAQ-0206: attach -- cites 816.2 + 816.2.a verbatim (exists); valid

## MR-4A closures
- MR-4A-0001: successor coverage verified: 383.3.d.1 == simultaneous multi-player triggers placed in turn order (verbatim match of general rule); defender-triggers-last specifics carried by 383.4.f (防守触发 def, verified) + 466.x resolution steps. FAQ ruling fully covered by successors. CLOSED.
- MR-4A-0002: successor coverage verified: 324.1 (special cleanup steps determined by triggering category, combat -> 466) verbatim match of FAQ claim structure; 466.1.a 启动战斗特殊清理 + 466.1.a.1/.2 insert steps (3c remove damage / 3d recall attackers) cover old [440.1.a.1-3]; 318 cleanup flow covers old 322.2/322.3 sequence position. CLOSED.
- MR-4A-0003: successor coverage verified (same mapping family as MR-4A-0002): damage-mark clearing now inserted as step 3c via 466.1.a.1 during combat special cleanup; KogMaw Last Breath trigger chain-finalize per 324 special-cleanup flow. Old 440.x (Burn) number-reuse confirmed. CLOSED.
- MR-4A-0004: successor coverage verified: 809.1.c text == 735.1.c（修订后）semantics verbatim (Ward keyword shorthand; MR-2D-0007 incorporation precedent). CLOSED.
- MR-4A-0005: successor coverage verified: 465.2.c.4(.a) == lethal-minimum allocation rule (verbatim content match with old 460.2.c.3); current 323.5 (3b lethal-destroy, refs 142.4) content-consistent with FAQ quote. CLOSED.
- MR-4A-0006: successor coverage verified: current 335 (no pending tasks/items -> main phase priority / other phase advance) matches old 335.3 quote verbatim (plus showdown/combat clause); 334.1 HOT task-handling exists; HOT FEPR naming逐字对应. CLOSED.

## stats
```json
{
  "candidates": 19,
  "reconciled": 19,
  "errors": 0,
  "flagged_verification": 14,
  "entries_oi": 11,
  "entries_exc": 1,
  "links_stale": 7,
  "links_rcc_incorporated": 6,
  "links_relocated": 1,
  "changes_written": 6,
  "mr4a_closed": 6,
  "note": "sandbox retry re-ran script (same incident as 4B-B002/B004); stats corrected to effective first-pass values recovered from DB"
}
```

## validation
```json
{
  "rules_reconciled_total": 2896,
  "rules_pending": 88,
  "pending_rcr_left": 0,
  "rec_tier1f": 19,
  "reconciled_missing_rec": 0,
  "needs_verification_true": 332,
  "changes_total": 228,
  "mr4a_open_left": 0,
  "verif_flag_left": 0
}
```

## warnings (0)
