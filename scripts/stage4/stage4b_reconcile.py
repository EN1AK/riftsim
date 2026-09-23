"""
Stage 4B batch 4B-B001 - Tier-0 mechanical rule reconciliation.

Scope (judgment-free subset only):
  R-CR core rules whose rule_evidence =
    - exactly zh+en 'same' links with alignment relation = equivalent
    - NO errata ('replacement') links
    - NO faq:* links
    - NO 'VERIFICATION FLAG 4B' notes
    - NOT translation_difference-flagged
These need no adjudication: EN and CN confirmed as the SAME rule version
(Stage 2B/3), alignment equivalent, no modifiers. Canonical text = zh
official text (project convention: zh canonical / en official reference;
both remain traceable via rule_evidence).

Per-rule atomic COMMIT (spec 15.8). Idempotent + resumable.
Tier-1/2 subsets (tr-diff, VERIF flags, FAQ-linked, R-CARD, R-TOPIC,
R-MISC, MR-4A) are explicitly OUT of scope for this batch.
"""
import json
import sqlite3
import sys
from datetime import datetime, timezone

DB = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db'
CHK = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\checkpoints\stage4b_tier0_checkpoint.json'
RPT = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\reports\stage4b_tier0_reconciliation.md'

TIER0_SQL = """
SELECT r.rule_id, r.topic
FROM rules r
WHERE r.rule_id LIKE 'R-CR-%'
  AND r.status = 'pending_reconciliation'
  AND (SELECT COUNT(*) FROM rule_evidence re WHERE re.rule_id = r.rule_id AND re.relationship = 'same') = 2
  AND NOT EXISTS (SELECT 1 FROM rule_evidence re WHERE re.rule_id = r.rule_id AND re.relationship = 'replacement')
  AND NOT EXISTS (SELECT 1 FROM rule_evidence re WHERE re.rule_id = r.rule_id AND re.relationship LIKE 'faq:%')
  AND NOT EXISTS (SELECT 1 FROM rule_evidence re WHERE re.rule_id = r.rule_id AND re.notes LIKE '%VERIFICATION FLAG 4B%')
  AND NOT EXISTS (
      SELECT 1 FROM rule_evidence re JOIN alignments a ON a.evidence_a = re.evidence_id
      WHERE re.rule_id = r.rule_id AND a.alignment_id LIKE 'AL-CR%' AND a.relation = 'translation_difference')
ORDER BY r.rule_id
"""


def main():
    db = sqlite3.connect(DB)
    db.isolation_level = None  # manual transactions
    c = db.cursor()

    cols = [r[1] for r in c.execute('PRAGMA table_info(rules)')]
    added_col = False
    if 'needs_verification' not in cols:
        c.execute("ALTER TABLE rules ADD COLUMN needs_verification TEXT")
        added_col = True

    candidates = c.execute(TIER0_SQL).fetchall()
    stats = {'candidates': len(candidates), 'reconciled': 0, 'skipped_exists': 0,
             'needs_review': 0, 'errors': 0}
    warnings = []

    for rule_id, topic in candidates:
        try:
            rows = c.execute(
                "SELECT re.evidence_id, e.source_language, e.original_text "
                "FROM rule_evidence re JOIN evidence e ON e.evidence_id = re.evidence_id "
                "WHERE re.rule_id = ? AND re.relationship = 'same'", (rule_id,)).fetchall()
            zh = [r for r in rows if r[1] == 'zh']
            en = [r for r in rows if r[1] == 'en']
            if len(zh) != 1 or len(en) != 1:
                c.execute('BEGIN')
                c.execute("UPDATE rules SET status='needs_review', needs_verification='true' WHERE rule_id=?", (rule_id,))
                c.execute('COMMIT')
                stats['needs_review'] += 1
                warnings.append(f'{rule_id}: expected 1 zh + 1 en same-link, got {len(zh)} zh / {len(en)} en')
                continue

            zh_ev, _, zh_text = zh[0]
            en_ev, _, en_text = en[0]
            rec_id = f'REC-4B-T0-{rule_id}'

            c.execute('BEGIN')
            # rules row
            c.execute(
                "UPDATE rules SET proposed_canonical_rule=?, status='reconciled', "
                "needs_verification='false' WHERE rule_id=?", (zh_text, rule_id))
            # reconciliation record (Stage 3 alignment basis; idempotent)
            if not c.execute('SELECT 1 FROM reconciliations WHERE reconciliation_id=?', (rec_id,)).fetchone():
                c.execute(
                    'INSERT INTO reconciliations (reconciliation_id, rule_id, source_id, '
                    'original_fragment, corrected_fragment, modification_type, effective_scope, status) '
                    'VALUES (?,?,?,?,?,?,?,?)',
                    (rec_id, rule_id, 'source_009+source_018',
                     f'zh+en same-version equivalent pair ({zh_ev} / {en_ev}); en=official, zh=canonical; no errata/FAQ links',
                     None, 'none', 'full_rule', 'reconciled_tier0'))
            else:
                stats['skipped_exists'] += 1
            c.execute('COMMIT')
            stats['reconciled'] += 1
        except Exception as ex:  # never let one rule kill the batch
            try:
                c.execute('ROLLBACK')
            except Exception:
                pass
            stats['errors'] += 1
            warnings.append(f'{rule_id}: ERROR {ex}')

    # batch-level bookkeeping (single commit)
    c.execute('BEGIN')
    if not c.execute('SELECT 1 FROM processing_tasks WHERE task_id=?', ('task_4b_01',)).fetchone():
        c.execute(
            'INSERT INTO processing_tasks (task_id, source_id, page_start, page_end, section, status, assigned_role, notes) '
            "VALUES ('task_4b_01', 'multi', NULL, NULL, 'stage4b_tier0_mechanical_reconciliation', 'completed', 'agent', ?)",
            (json.dumps(stats),))
    else:
        c.execute("UPDATE processing_tasks SET status='completed', notes=? WHERE task_id='task_4b_01'",
                  (json.dumps(stats),))
    c.execute('COMMIT')

    # validation (read-only)
    v = {
        'rules_reconciled_total': c.execute("SELECT COUNT(*) FROM rules WHERE status='reconciled'").fetchone()[0],
        'rules_pending': c.execute("SELECT COUNT(*) FROM rules WHERE status='pending_reconciliation'").fetchone()[0],
        'rules_needs_review': c.execute("SELECT COUNT(*) FROM rules WHERE status='needs_review'").fetchone()[0],
        'reconciliations_tier0': c.execute("SELECT COUNT(*) FROM reconciliations WHERE reconciliation_id LIKE 'REC-4B-T0-%'").fetchone()[0],
        'reconciled_missing_rec': c.execute(
            "SELECT COUNT(*) FROM rules r WHERE r.status='reconciled' AND NOT EXISTS "
            "(SELECT 1 FROM reconciliations x WHERE x.rule_id=r.rule_id)").fetchone()[0],
        'reconciled_null_text': c.execute(
            "SELECT COUNT(*) FROM rules WHERE status='reconciled' AND proposed_canonical_rule IS NULL").fetchone()[0],
    }

    now = datetime.now(timezone.utc).isoformat(timespec='seconds')
    with open(CHK, 'w', encoding='utf-8') as f:
        json.dump({'batch': '4B-B001-tier0', 'finished_at': now, 'stats': stats,
                   'validation': v, 'warnings': warnings[:50]}, f, ensure_ascii=False, indent=2)
    with open(RPT, 'w', encoding='utf-8') as f:
        f.write('# Stage 4B batch 4B-B001 - Tier-0 mechanical reconciliation\n\n')
        f.write(f'finished_at: {now}\n\n')
        f.write('Scope: R-CR rules with zh+en same-version equivalent alignment, no errata/FAQ/VERIF links.\n\n')
        f.write(f'## stats\n```json\n{json.dumps(stats, indent=2)}\n```\n\n')
        f.write(f'## validation\n```json\n{json.dumps(v, indent=2)}\n```\n\n')
        f.write('## warnings (%d)\n' % len(warnings))
        for w in warnings:
            f.write(f'- {w}\n')

    print('stats:', json.dumps(stats))
    print('validation:', json.dumps(v))
    print('added needs_verification col:', added_col)
    print('warnings:', len(warnings))
    for w in warnings[:20]:
        print(' -', w)


if __name__ == '__main__':
    sys.exit(main())
