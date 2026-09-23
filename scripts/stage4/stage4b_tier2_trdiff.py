"""
Stage 4B batch 4B-B003 - Tier-2 MR-3-CR translation-difference adjudication.

Scope: the 161 R-CR core rules whose zh/en pair was auto-flagged
translation_difference(low) in Stage 3 (MR-3-CR-0001..0161). Every pair was
re-read in full and adjudicated by the agent (pair dump:
workspace/checkpoints/stage4b_tier2_trdiff_pairs.json).

Adjudication results (VERDICT_OVERRIDES below; all others = equivalent):
  - 160/161 equivalent_despite_diff: differences are orthographic only
    (Chinese numerals vs digits, keyword bracket tokens translated inline,
    EN placeholder brackets vs zh prose placeholders). No semantic change.
  - 1/161 semantic_divergence: MR-3-CR-0130 / R-CR-811.1.b (Hidden keyword)
    EN carries trailing clause "for as long as you control that battlefield"
    absent from the zh official text (translation omission). Recorded as
    conflict CON-4B-T2-0001, deferred to Stage 5.

Per spec 15.7 ("Chinese-English difference") ALL 161 rules get
needs_verification=true even when adjudicated equivalent.

Canonical convention (tier-0/tier-1): canonical = zh official text
(CN Core Rules 2026-07-17 postdates EN Core Rules 2026-07-16; same rule
version confirmed in Stage 2B/3); en = official reference via rule_evidence.

4 of the 161 rules also carry faq:rule_interpretation links (5 links);
those get the tier-1 verbatim attach into official_interpretation in the
same per-rule transaction. R-CR-438.7 additionally carries a
'VERIFICATION FLAG 4B' note (pre-renumbering judge-FAQ ref) - kept flagged
via needs_verification=true; VERIF-FLAG note stays on rule_evidence.

Manual review items MR-3-CR-0001..0161 are closed in-place (project
convention: annotate issue_description + possible_explanation; rule_id
backfilled). Per-rule atomic COMMIT (spec 15.8). Idempotent + resumable.
Out of scope: remaining 19 VERIF-FLAG/FAQ-linked R-CR, R-CARD errata,
R-TOPIC/R-MISC, MR-4A, MR-2D-0010.
"""
import json
import sqlite3
import sys
from datetime import datetime, timezone

DB = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db'
PAIRS = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\checkpoints\stage4b_tier2_trdiff_pairs.json'
CHK = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\checkpoints\stage4b_tier2_trdiff_checkpoint.json'
RPT = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\reports\stage4b_tier2_trdiff.md'

JUDGE_SOURCES = {'source_001', 'source_006', 'source_008'}

# verdict overrides; everything not listed = ('equivalent', default rationale)
VERDICT_OVERRIDES = {
    'MR-3-CR-0056': (
        'equivalent',
        'example quote abbreviates card text in zh (omits [E] cost prefix of '
        'Ultrasoft Poro); rule semantics unchanged'),
    'MR-3-CR-0059': (
        'equivalent',
        'Jinx/Loose Cannon conditional-clause-position variance; adjudicated by '
        'MR-2D-0004 (official FAQ unifies zh execution; EN template variant); '
        'zh text itself documents the EN phrasing'),
    'MR-3-CR-0130': (
        'semantic_divergence',
        'EN carries trailing clause "for as long as you control that battlefield" '
        'absent from zh official text (translation omission; possible duration-'
        'scoping difference for the Hidden setup ability)'),
}
DEFAULT_RATIONALE = ('semantic equivalence confirmed by full-text comparison; '
                     'difference is orthographic (Chinese numerals vs digits / '
                     'keyword bracket tokens translated inline / EN placeholder '
                     'brackets vs zh prose)')


def tier_of(source_id):
    return 'judge-community' if source_id in JUDGE_SOURCES else 'official'


def process(c, pair, stats, warnings):
    item_id, rule_id = pair['item_id'], pair['rule_id']
    zh_text, en_text = pair['zh'], pair['en']
    rec_id = f'REC-4B-T2-{rule_id}'
    verdict, rationale = VERDICT_OVERRIDES.get(
        item_id, ('equivalent', DEFAULT_RATIONALE))

    if c.execute('SELECT 1 FROM reconciliations WHERE reconciliation_id=?', (rec_id,)).fetchone():
        stats['skipped_exists'] += 1
        return

    rows = c.execute(
        "SELECT e.source_language FROM rule_evidence re JOIN evidence e "
        "ON e.evidence_id = re.evidence_id WHERE re.rule_id=? AND re.relationship='same'",
        (rule_id,)).fetchall()
    langs = sorted(x[0] for x in rows)
    if langs != ['en', 'zh']:
        c.execute('BEGIN')
        c.execute("UPDATE rules SET status='needs_review', needs_verification='true' WHERE rule_id=?",
                  (rule_id,))
        c.execute('COMMIT')
        stats['needs_review'] += 1
        warnings.append(f'{rule_id}: expected 1 zh + 1 en same-link, got {langs}')
        return

    # tier-1 style verbatim attach for any faq:* links (all are rule_interpretation here)
    faq_links = c.execute(
        "SELECT re.relationship, e.evidence_id, e.source_id, e.faq_question, e.faq_answer, e.original_text "
        "FROM rule_evidence re JOIN evidence e ON e.evidence_id = re.evidence_id "
        "WHERE re.rule_id=? AND re.relationship LIKE 'faq:%' ORDER BY e.evidence_id",
        (rule_id,)).fetchall()
    interp_entries = []
    for rel, ev_id, src, q, a, orig in faq_links:
        cls = rel.split(':', 1)[1]
        head = f'[{ev_id} | {src} | {tier_of(src)} | {cls}]'
        body = f'Q: {q}\nA: {a}' if q and a else (orig or '').strip()
        if cls == 'rule_interpretation':
            interp_entries.append(f'{head}\n{body}')
        else:
            warnings.append(f'{rule_id}: unexpected faq link {rel} on {ev_id}; not attached')
    has_verif_flag = bool(c.execute(
        "SELECT 1 FROM rule_evidence WHERE rule_id=? AND notes LIKE '%VERIFICATION FLAG 4B%'",
        (rule_id,)).fetchone())

    frag = (f'tr-diff adjudication [{verdict}]: {rationale} | auto-flag: '
            f'{pair["flag_reason"].strip()[:180]} | canonical=zh official text '
            f'(CN CR 2026-07-17 postdates EN CR 2026-07-16, same rule version); '
            f'en=official reference; needs_verification=true (spec 15.7 zh/en textual difference)')
    if faq_links:
        frag += f'; faq attach (tier-1 convention): rule_interpretation={len(interp_entries)}'
    if has_verif_flag:
        frag += '; rule_evidence carries VERIFICATION FLAG 4B (judge-FAQ pre-renumbering ref) -> Stage 5'
    corrected = None
    if verdict == 'semantic_divergence':
        corrected = ('zh official text keeps canonical status (newer date); divergence recorded as '
                     'conflict CON-4B-T2-0001 for Stage 5 ruling')

    c.execute('BEGIN')
    c.execute(
        "UPDATE rules SET proposed_canonical_rule=?, official_interpretation=?, "
        "status='reconciled', needs_verification='true' WHERE rule_id=?",
        (zh_text, '\n\n'.join(interp_entries) if interp_entries else None, rule_id))
    c.execute(
        'INSERT INTO reconciliations (reconciliation_id, rule_id, source_id, original_fragment, '
        'corrected_fragment, modification_type, effective_scope, status) VALUES (?,?,?,?,?,?,?,?)',
        (rec_id, rule_id, 'source_009+source_018', frag, corrected, 'none',
         'tr_diff_adjudication', 'reconciled_tier2'))
    if verdict == 'semantic_divergence':
        c.execute(
            'INSERT INTO conflicts (conflict_id, rule_id, evidence_a, evidence_b, conflict_type, '
            'resolution_status, notes) VALUES (?,?,?,?,?,?,?)',
            ('CON-4B-T2-0001', rule_id, pair['zh_ev'], pair['en_ev'], 'translation_omission',
             'pending_stage5',
             'EN text: "...hide this facedown at a battlefield you control that doesn\'t already '
             'have a facedown card hidden there for as long as you control that battlefield." '
             'The zh official text omits the trailing duration clause. Possible gameplay impact '
             '(Hidden card duration when battlefield control is lost). Canonical stays zh per '
             'project convention; Stage 5 to rule on supplementation.'))
        stats['conflicts'] += 1
    close_note = (f' [2026-09-22 4B-B003 裁定关闭] 4B裁决[{verdict}]：{rationale}；'
                  f'canonical=zh官方文本，en=官方参照；needs_verification=true 待Stage 5')
    c.execute(
        'UPDATE manual_review SET rule_id=?, issue_description=issue_description||?, '
        'possible_explanation=? WHERE item_id=?',
        (rule_id, close_note, f'4B-B003 adjudication [{verdict}]: {rationale}', item_id))
    c.execute('COMMIT')

    stats['reconciled'] += 1
    if verdict == 'semantic_divergence':
        stats['semantic_divergence'] += 1
    else:
        stats['equivalent'] += 1
    if interp_entries:
        stats['faq_attached_rules'] += 1
        stats['faq_attached_entries'] += len(interp_entries)


def main():
    pairs = json.load(open(PAIRS, encoding='utf-8'))
    db = sqlite3.connect(DB)
    db.isolation_level = None
    c = db.cursor()

    stats = {'candidates': len(pairs), 'reconciled': 0, 'skipped_exists': 0,
             'equivalent': 0, 'semantic_divergence': 0, 'conflicts': 0,
             'faq_attached_rules': 0, 'faq_attached_entries': 0,
             'needs_review': 0, 'errors': 0}
    warnings = []

    for pair in pairs:
        try:
            process(c, pair, stats, warnings)
        except Exception as ex:
            try:
                c.execute('ROLLBACK')
            except Exception:
                pass
            stats['errors'] += 1
            warnings.append(f"{pair['rule_id']}: ERROR {ex}")

    c.execute('BEGIN')
    if not c.execute('SELECT 1 FROM processing_tasks WHERE task_id=?', ('task_4b_03',)).fetchone():
        c.execute(
            'INSERT INTO processing_tasks (task_id, source_id, page_start, page_end, section, status, '
            "assigned_role, notes) VALUES ('task_4b_03', 'multi', NULL, NULL, "
            "'stage4b_tier2_trdiff_adjudication', 'completed', 'agent', ?)",
            (json.dumps(stats, ensure_ascii=False),))
    else:
        c.execute("UPDATE processing_tasks SET status='completed', notes=? WHERE task_id='task_4b_03'",
                  (json.dumps(stats, ensure_ascii=False),))
    c.execute('COMMIT')

    v = {
        'rules_reconciled_total': c.execute("SELECT COUNT(*) FROM rules WHERE status='reconciled'").fetchone()[0],
        'rules_pending': c.execute("SELECT COUNT(*) FROM rules WHERE status='pending_reconciliation'").fetchone()[0],
        'rules_needs_review': c.execute("SELECT COUNT(*) FROM rules WHERE status='needs_review'").fetchone()[0],
        'reconciliations_tier2': c.execute("SELECT COUNT(*) FROM reconciliations WHERE reconciliation_id LIKE 'REC-4B-T2-%'").fetchone()[0],
        'mr3cr_closed': c.execute("SELECT COUNT(*) FROM manual_review WHERE item_id LIKE 'MR-3-CR-%' AND issue_description LIKE '%4B-B003 裁定关闭%'").fetchone()[0],
        'mr3cr_rule_id_backfilled': c.execute("SELECT COUNT(*) FROM manual_review WHERE item_id LIKE 'MR-3-CR-%' AND rule_id IS NOT NULL").fetchone()[0],
        'conflicts_total': c.execute('SELECT COUNT(*) FROM conflicts').fetchone()[0],
        'reconciled_missing_rec': c.execute(
            "SELECT COUNT(*) FROM rules r WHERE r.status='reconciled' AND NOT EXISTS "
            "(SELECT 1 FROM reconciliations x WHERE x.rule_id=r.rule_id)").fetchone()[0],
        'rcr_reconciled_null_text': c.execute(
            "SELECT COUNT(*) FROM rules WHERE status='reconciled' AND rule_id LIKE 'R-CR-%' "
            "AND proposed_canonical_rule IS NULL").fetchone()[0],
        'needs_verification_true': c.execute("SELECT COUNT(*) FROM rules WHERE needs_verification='true'").fetchone()[0],
        'pending_rcr': c.execute("SELECT COUNT(*) FROM rules WHERE status='pending_reconciliation' AND rule_id LIKE 'R-CR-%'").fetchone()[0],
    }

    now = datetime.now(timezone.utc).isoformat(timespec='seconds')
    with open(CHK, 'w', encoding='utf-8') as f:
        json.dump({'batch': '4B-B003-tier2-trdiff-adjudication', 'finished_at': now,
                   'stats': stats, 'validation': v, 'warnings': warnings[:80]},
                  f, ensure_ascii=False, indent=2)
    with open(RPT, 'w', encoding='utf-8') as f:
        f.write('# Stage 4B batch 4B-B003 - Tier-2 MR-3-CR tr-diff adjudication\n\n')
        f.write(f'finished_at: {now}\n\n')
        f.write('Scope: 161 R-CR rules flagged translation_difference(low) in Stage 3 '
                '(MR-3-CR-0001..0161). Each zh/en pair re-read in full and adjudicated.\n\n')
        f.write('Conventions: canonical=zh official text (CN CR 2026-07-17 postdates EN CR '
                '2026-07-16, same rule version); en=official reference. ALL 161 rules '
                'needs_verification=true (spec 15.7 zh/en textual difference).\n\n')
        f.write('Verdicts: 160 equivalent_despite_diff; 1 semantic_divergence '
                '(MR-3-CR-0130 / R-CR-811.1.b Hidden keyword - EN duration clause '
                '"for as long as you control that battlefield" missing in zh official text; '
                'conflict CON-4B-T2-0001 -> Stage 5).\n')
        f.write('Noted example-quote variances: MR-3-CR-0056 (zh quote abbreviates [E] cost '
                'prefix), MR-3-CR-0059 (Jinx conditional-clause position, per MR-2D-0004).\n')
        f.write('4 rules also received tier-1 FAQ attach (5 faq:rule_interpretation entries); '
                'R-CR-438.7 keeps VERIF-FLAG pointer for Stage 5.\n\n')
        f.write(f'## stats\n```json\n{json.dumps(stats, indent=2, ensure_ascii=False)}\n```\n\n')
        f.write(f'## validation\n```json\n{json.dumps(v, indent=2, ensure_ascii=False)}\n```\n\n')
        f.write('## warnings (%d)\n' % len(warnings))
        for w in warnings:
            f.write(f'- {w}\n')

    print('stats:', json.dumps(stats, ensure_ascii=False))
    print('validation:', json.dumps(v, ensure_ascii=False))
    print('warnings:', len(warnings))
    for w in warnings[:20]:
        print(' -', w)


if __name__ == '__main__':
    sys.exit(main())
