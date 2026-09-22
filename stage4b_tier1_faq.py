"""
Stage 4B batch 4B-B002 - Tier-1 mechanical FAQ attach.

Scope (judgment-free only):
  A) FAQ-only R-CARD: pending_reconciliation, NO 'replacement' links (384).
     These clusters have no core-rule/errata text -> proposed_canonical_rule
     stays NULL; reconciliation row documents "FAQ-only card cluster".
  B) FAQ-linked clean R-CR: pending_reconciliation, has faq:* links, no
     'replacement', no 'VERIFICATION FLAG 4B' notes, no translation_difference
     alignment (14). Canonical = zh official text (same-version equivalent,
     per tier-0 convention); en = official reference.

Mechanical attach (verbatim, deterministic rebuild from current links):
  faq:example_only          -> rules.example
  faq:rule_interpretation   -> rules.official_interpretation
  faq:exception             -> rules.exception            + needs_verification=true
  faq:rule_change_candidate -> NOT written into rule fields (never modifies
                               canonical per spec 12.5/15); listed in the
                               reconciliation record     + needs_verification=true

Every attached entry is prefixed with [evidence_id | source_id | tier | class].
tier = 'judge-community' for source_001/006/008 (MR-2D-0013: self-declared
"not official FAQ"), else 'official'. A judge-tier rule_interpretation entry
also forces needs_verification=true (authority-tier flag).

Per-rule atomic COMMIT (spec 15.8). Idempotent + resumable.
Out of scope: tr-diff MR-3-CR, VERIF-FLAG links, errata application,
R-TOPIC/R-MISC, MR-4A successor checks.
"""
import json
import sqlite3
import sys
from datetime import datetime, timezone

DB = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db'
CHK = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\checkpoints\stage4b_tier1_checkpoint.json'
RPT = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\reports\stage4b_tier1_faq_attach.md'

JUDGE_SOURCES = {'source_001', 'source_006', 'source_008'}

RCARD_SQL = """
SELECT r.rule_id FROM rules r
WHERE r.rule_id LIKE 'R-CARD-%' AND r.status = 'pending_reconciliation'
  AND NOT EXISTS (SELECT 1 FROM rule_evidence re WHERE re.rule_id = r.rule_id AND re.relationship = 'replacement')
ORDER BY r.rule_id
"""

RCR_SQL = """
SELECT r.rule_id FROM rules r
WHERE r.rule_id LIKE 'R-CR-%' AND r.status = 'pending_reconciliation'
  AND EXISTS (SELECT 1 FROM rule_evidence re WHERE re.rule_id = r.rule_id AND re.relationship LIKE 'faq:%')
  AND NOT EXISTS (SELECT 1 FROM rule_evidence re WHERE re.rule_id = r.rule_id AND re.relationship = 'replacement')
  AND NOT EXISTS (SELECT 1 FROM rule_evidence re WHERE re.rule_id = r.rule_id AND re.notes LIKE '%VERIFICATION FLAG 4B%')
  AND NOT EXISTS (
      SELECT 1 FROM rule_evidence re JOIN alignments a ON a.evidence_a = re.evidence_id
      WHERE re.rule_id = r.rule_id AND a.alignment_id LIKE 'AL-CR%' AND a.relation = 'translation_difference')
ORDER BY r.rule_id
"""

FAQ_SQL = """
SELECT re.relationship, e.evidence_id, e.source_id, e.faq_question, e.faq_answer, e.original_text
FROM rule_evidence re JOIN evidence e ON e.evidence_id = re.evidence_id
WHERE re.rule_id = ? AND re.relationship LIKE 'faq:%'
ORDER BY e.evidence_id
"""


def tier_of(source_id):
    return 'judge-community' if source_id in JUDGE_SOURCES else 'official'


def build_entry(rel, ev_id, src, question, answer, original_text):
    cls = rel.split(':', 1)[1]
    head = f'[{ev_id} | {src} | {tier_of(src)} | {cls}]'
    if question and answer:
        body = f'Q: {question}\nA: {answer}'
    else:
        body = (original_text or '').strip()
    return cls, f'{head}\n{body}'


def process_rule(c, rule_id, is_rcr, stats, warnings):
    links = c.execute(FAQ_SQL, (rule_id,)).fetchall()
    if not links:
        raise ValueError('no faq links found')

    canonical = None
    if is_rcr:
        rows = c.execute(
            "SELECT e.source_language, e.original_text FROM rule_evidence re "
            "JOIN evidence e ON e.evidence_id = re.evidence_id "
            "WHERE re.rule_id = ? AND re.relationship = 'same'", (rule_id,)).fetchall()
        zh = [t for lang, t in rows if lang == 'zh']
        en = [t for lang, t in rows if lang == 'en']
        if len(zh) != 1 or len(en) != 1:
            c.execute('BEGIN')
            c.execute("UPDATE rules SET status='needs_review', needs_verification='true' WHERE rule_id=?", (rule_id,))
            c.execute('COMMIT')
            stats['needs_review'] += 1
            warnings.append(f'{rule_id}: expected 1 zh + 1 en same-link, got {len(zh)} zh / {len(en)} en')
            return
        canonical = zh[0]

    example, interpretation, exception, change_ids = [], [], [], []
    needs_verif = False
    for rel, ev_id, src, q, a, orig in links:
        cls, entry = build_entry(rel, ev_id, src, q, a, orig)
        if cls == 'example_only':
            example.append(entry)
        elif cls == 'rule_interpretation':
            interpretation.append(entry)
            if src in JUDGE_SOURCES:
                needs_verif = True
        elif cls == 'exception':
            exception.append(entry)
            needs_verif = True
        elif cls == 'rule_change_candidate':
            change_ids.append(f'{ev_id}({src})')
            needs_verif = True
        else:
            warnings.append(f'{rule_id}: unexpected relationship {rel} on {ev_id}; attached as interpretation')
            interpretation.append(entry)
            needs_verif = True

    rec_id = f'REC-4B-T1-{rule_id}'
    frag = (f'faq attach: example_only={len(example)} rule_interpretation={len(interpretation)} '
            f'exception={len(exception)} rule_change_candidate={len(change_ids)}')
    if change_ids:
        frag += '; rule_change_candidate NOT applied (deferred to Stage 5 verification): ' + ', '.join(change_ids)
    if is_rcr:
        frag += '; canonical=zh official text, en=official reference (same-version equivalent pair)'
    else:
        frag += '; FAQ-only card cluster: no core-rule/errata text, canonical stays NULL'

    c.execute('BEGIN')
    c.execute(
        "UPDATE rules SET proposed_canonical_rule=?, example=?, official_interpretation=?, "
        "exception=?, status='reconciled', needs_verification=? WHERE rule_id=?",
        (canonical,
         '\n\n'.join(example) if example else None,
         '\n\n'.join(interpretation) if interpretation else None,
         '\n\n'.join(exception) if exception else None,
         'true' if needs_verif else 'false',
         rule_id))
    if not c.execute('SELECT 1 FROM reconciliations WHERE reconciliation_id=?', (rec_id,)).fetchone():
        c.execute(
            'INSERT INTO reconciliations (reconciliation_id, rule_id, source_id, original_fragment, '
            'corrected_fragment, modification_type, effective_scope, status) VALUES (?,?,?,?,?,?,?,?)',
            (rec_id, rule_id, 'multi-faq', frag, None, 'none', 'faq_attach', 'reconciled_tier1'))
    else:
        stats['skipped_exists'] += 1
    c.execute('COMMIT')
    stats['reconciled'] += 1
    if needs_verif:
        stats['flagged_verification'] += 1
    stats['example_entries'] += len(example)
    stats['interpretation_entries'] += len(interpretation)
    stats['exception_entries'] += len(exception)
    stats['rule_change_links'] += len(change_ids)


def main():
    db = sqlite3.connect(DB)
    db.isolation_level = None
    c = db.cursor()

    rcards = [r[0] for r in c.execute(RCARD_SQL)]
    rcrs = [r[0] for r in c.execute(RCR_SQL)]
    stats = {'candidates_rcard': len(rcards), 'candidates_rcr': len(rcrs), 'reconciled': 0,
             'skipped_exists': 0, 'needs_review': 0, 'errors': 0, 'flagged_verification': 0,
             'example_entries': 0, 'interpretation_entries': 0, 'exception_entries': 0,
             'rule_change_links': 0}
    warnings = []

    for rule_id in rcards:
        try:
            process_rule(c, rule_id, False, stats, warnings)
        except Exception as ex:
            try:
                c.execute('ROLLBACK')
            except Exception:
                pass
            stats['errors'] += 1
            warnings.append(f'{rule_id}: ERROR {ex}')

    for rule_id in rcrs:
        try:
            process_rule(c, rule_id, True, stats, warnings)
        except Exception as ex:
            try:
                c.execute('ROLLBACK')
            except Exception:
                pass
            stats['errors'] += 1
            warnings.append(f'{rule_id}: ERROR {ex}')

    c.execute('BEGIN')
    if not c.execute('SELECT 1 FROM processing_tasks WHERE task_id=?', ('task_4b_02',)).fetchone():
        c.execute(
            'INSERT INTO processing_tasks (task_id, source_id, page_start, page_end, section, status, assigned_role, notes) '
            "VALUES ('task_4b_02', 'multi', NULL, NULL, 'stage4b_tier1_faq_attach', 'completed', 'agent', ?)",
            (json.dumps(stats),))
    else:
        c.execute("UPDATE processing_tasks SET status='completed', notes=? WHERE task_id='task_4b_02'",
                  (json.dumps(stats),))
    c.execute('COMMIT')

    v = {
        'rules_reconciled_total': c.execute("SELECT COUNT(*) FROM rules WHERE status='reconciled'").fetchone()[0],
        'rules_pending': c.execute("SELECT COUNT(*) FROM rules WHERE status='pending_reconciliation'").fetchone()[0],
        'rules_needs_review': c.execute("SELECT COUNT(*) FROM rules WHERE status='needs_review'").fetchone()[0],
        'reconciliations_tier1': c.execute("SELECT COUNT(*) FROM reconciliations WHERE reconciliation_id LIKE 'REC-4B-T1-%'").fetchone()[0],
        'reconciled_missing_rec': c.execute(
            "SELECT COUNT(*) FROM rules r WHERE r.status='reconciled' AND NOT EXISTS "
            "(SELECT 1 FROM reconciliations x WHERE x.rule_id=r.rule_id)").fetchone()[0],
        'rcr_reconciled_null_text': c.execute(
            "SELECT COUNT(*) FROM rules WHERE status='reconciled' AND rule_id LIKE 'R-CR-%' "
            "AND proposed_canonical_rule IS NULL").fetchone()[0],
        'rcard_faqonly_null_text_expected': c.execute(
            "SELECT COUNT(*) FROM rules r WHERE r.status='reconciled' AND r.rule_id LIKE 'R-CARD-%' "
            "AND r.proposed_canonical_rule IS NULL AND NOT EXISTS "
            "(SELECT 1 FROM rule_evidence re WHERE re.rule_id=r.rule_id AND re.relationship='replacement')").fetchone()[0],
        'needs_verification_true': c.execute("SELECT COUNT(*) FROM rules WHERE needs_verification='true'").fetchone()[0],
    }

    now = datetime.now(timezone.utc).isoformat(timespec='seconds')
    with open(CHK, 'w', encoding='utf-8') as f:
        json.dump({'batch': '4B-B002-tier1-faq-attach', 'finished_at': now, 'stats': stats,
                   'validation': v, 'warnings': warnings[:80]}, f, ensure_ascii=False, indent=2)
    with open(RPT, 'w', encoding='utf-8') as f:
        f.write('# Stage 4B batch 4B-B002 - Tier-1 mechanical FAQ attach\n\n')
        f.write(f'finished_at: {now}\n\n')
        f.write('Scope: FAQ-only R-CARD (no errata) + clean FAQ-linked R-CR (no replacement/tr-diff/VERIF).\n')
        f.write('example_only->example; rule_interpretation->official_interpretation; exception->exception(+verify); '
                'rule_change_candidate NOT applied, recorded in reconciliation (+verify).\n')
        f.write('tier=judge-community for source_001/006/008 (MR-2D-0013); judge-tier interpretation forces verify.\n\n')
        f.write(f'## stats\n```json\n{json.dumps(stats, indent=2)}\n```\n\n')
        f.write(f'## validation\n```json\n{json.dumps(v, indent=2)}\n```\n\n')
        f.write('## warnings (%d)\n' % len(warnings))
        for w in warnings:
            f.write(f'- {w}\n')

    print('stats:', json.dumps(stats))
    print('validation:', json.dumps(v))
    print('warnings:', len(warnings))
    for w in warnings[:20]:
        print(' -', w)


if __name__ == '__main__':
    sys.exit(main())
