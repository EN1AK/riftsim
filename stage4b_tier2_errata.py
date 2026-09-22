"""
Stage 4B batch 4B-B004 - Tier-2 errata application on 130 R-CARD rules.

Scope: all pending_reconciliation R-CARD rules (130), each carrying >=1 zh
'replacement' errata link (README next-batch item #2). FAQ attach for these
rules rides the same batch (tier-1 conventions) since their fields are empty
and batch #3 owns only R-CR + rule_change_candidate review.

Per-rule processing (atomic BEGIN/COMMIT, idempotent):
  1. zh errata links ordered by date asc -> canonical = LAST zh errata
     corrected_fragment (official [NEW TEXT]). Chain check: earlier
     corrected_fragment vs later original_fragment (normalized) -> warning
     only, never blocks.
  2. changes rows for EVERY linked errata evidence x rule (zh + en +
     zh_only_translation): original_fragment -> corrected_fragment with
     source metadata; final_conclusion marks which row defines canonical.
  3. reconciliations row REC-4B-T2ER-<rule_id> documenting application.
  4. FAQ verbatim attach identical to stage4b_tier1_faq.py conventions
     (judge-community tier for source_001/006/008; rule_change_candidate NOT
     applied -> recorded in reconciliation).
  5. needs_verification=true for ALL 130 (spec 15.7: modified by errata).
     status='reconciled'.

Canonical comes ONLY from official errata evidence (spec 12.4:
cards_bilingual.db is not a rules source). cards db used only via existing
Stage-3 entity links (card_ids) - not read here.
"""
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone

sys.dont_write_bytecode = True

DB = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db'
CHK = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\checkpoints\stage4b_tier2_errata_checkpoint.json'
RPT = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\reports\stage4b_tier2_errata.md'

JUDGE_SOURCES = {'source_001', 'source_006', 'source_008'}

RULES_SQL = """
SELECT rule_id FROM rules
WHERE rule_id LIKE 'R-CARD-%' AND status = 'pending_reconciliation'
ORDER BY rule_id
"""

ERRATA_SQL = """
SELECT e.evidence_id, e.source_id, e.source_language, e.source_document, e.version, e.date,
       e.original_fragment, e.corrected_fragment, e.modification_type, e.effective_scope, e.notes
FROM rule_evidence re JOIN evidence e ON e.evidence_id = re.evidence_id
WHERE re.rule_id = ? AND re.relationship = 'replacement'
ORDER BY e.date, e.evidence_id
"""

FAQ_SQL = """
SELECT re.relationship, e.evidence_id, e.source_id, e.faq_question, e.faq_answer, e.original_text
FROM rule_evidence re JOIN evidence e ON e.evidence_id = re.evidence_id
WHERE re.rule_id = ? AND re.relationship LIKE 'faq:%'
ORDER BY e.evidence_id
"""


def norm(t):
    if not t:
        return ''
    t = re.sub(r'\{\{[^}]*\}\}', '', t)
    t = re.sub(r'\[[^\]]*\]', '', t)
    return re.sub(r'[\s\W_]+', '', t)


def tier_of(source_id):
    return 'judge-community' if source_id in JUDGE_SOURCES else 'official'


def build_faq_entry(rel, ev_id, src, question, answer, original_text):
    cls = rel.split(':', 1)[1]
    head = f'[{ev_id} | {src} | {tier_of(src)} | {cls}]'
    if question and answer:
        body = f'Q: {question}\nA: {answer}'
    else:
        body = (original_text or '').strip()
    return cls, f'{head}\n{body}'


def process_rule(c, rule_id, stats, warnings):
    errata = c.execute(ERRATA_SQL, (rule_id,)).fetchall()
    zh = [e for e in errata if e[2] == 'zh']
    en = [e for e in errata if e[2] == 'en']
    if not zh:
        raise ValueError('no zh errata link (unexpected per probe)')

    # canonical = latest-dated zh errata corrected_fragment
    zh_sorted = sorted(zh, key=lambda e: (e[5] or '', e[0]))
    canonical = zh_sorted[-1][7]
    canonical_ev = zh_sorted[-1][0]

    # chain check for rules with multiple zh errata
    if len(zh_sorted) > 1:
        for prev, nxt in zip(zh_sorted, zh_sorted[1:]):
            np_, no_ = norm(prev[7]), norm(nxt[6])
            if not np_ or not no_ or (np_ not in no_ and no_ not in np_):
                warnings.append(
                    f'{rule_id}: errata chain mismatch {prev[0]}->{nxt[0]} '
                    f'(prev corrected vs next original differ beyond notation)')

    # FAQ attach (tier-1 conventions)
    example, interpretation, exception, change_ids = [], [], [], []
    faq_verif = False
    for rel, ev_id, src, q, a, orig in c.execute(FAQ_SQL, (rule_id,)).fetchall():
        cls, entry = build_faq_entry(rel, ev_id, src, q, a, orig)
        if cls == 'example_only':
            example.append(entry)
        elif cls == 'rule_interpretation':
            interpretation.append(entry)
            if src in JUDGE_SOURCES:
                faq_verif = True
        elif cls == 'exception':
            exception.append(entry)
            faq_verif = True
        elif cls == 'rule_change_candidate':
            change_ids.append(f'{ev_id}({src})')
            faq_verif = True
        else:
            warnings.append(f'{rule_id}: unexpected relationship {rel} on {ev_id}; attached as interpretation')
            interpretation.append(entry)
            faq_verif = True

    c.execute('BEGIN')
    c.execute(
        "UPDATE rules SET proposed_canonical_rule=?, example=?, official_interpretation=?, "
        "exception=?, status='reconciled', needs_verification='true' WHERE rule_id=?",
        (canonical,
         '\n\n'.join(example) if example else None,
         '\n\n'.join(interpretation) if interpretation else None,
         '\n\n'.join(exception) if exception else None,
         rule_id))

    # changes rows: one per errata evidence x rule
    n_chg = 0
    for ev_id, src, lang, doc, ver, date, ofrag, cfrag, mtype, scope, notes in errata:
        chg_id = f'CHG-4B-T2ER-{rule_id[7:]}-{ev_id}'
        zh_only = bool(notes and 'zh_only_translation' in notes)
        if ev_id == canonical_ev:
            conclusion = 'applied: latest zh official errata defines canonical card text'
        elif lang == 'zh' and zh_only:
            conclusion = 'recorded: zh translation-fix errata superseded by later zh errata on same card' if len(zh_sorted) > 1 and ev_id != canonical_ev else 'recorded: zh translation-fix errata'
        elif lang == 'zh':
            conclusion = 'recorded: earlier zh errata in chain; canonical carried by later errata'
        else:
            conclusion = 'recorded: EN-language counterpart errata (zh canonical governed by paired zh errata)'
        if not c.execute('SELECT 1 FROM changes WHERE change_id=?', (chg_id,)).fetchone():
            c.execute(
                'INSERT INTO changes (change_id, rule_id, original_content, new_content, source_type, '
                'source_language, source_document, version, date, modification_type, reason, final_conclusion) '
                'VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                (chg_id, rule_id, ofrag, cfrag, 'errata', lang, doc, ver, date, mtype,
                 f'official errata {ev_id} ({src}) applied per Stage 4B; effective_scope={scope}',
                 conclusion))
            n_chg += 1
        else:
            stats['skipped_chg_exists'] += 1

    # reconciliation row
    rec_id = f'REC-4B-T2ER-{rule_id}'
    zh_ids = ', '.join(e[0] for e in zh_sorted)
    en_ids = ', '.join(e[0] for e in en) or 'none'
    frag = (f'errata application: zh errata [{zh_ids}] (date-asc); canonical = corrected text of {canonical_ev} '
            f'(latest zh official errata); EN counterpart errata [{en_ids}] recorded w/o canonical change')
    if len(zh_sorted) > 1:
        frag += f'; chained errata x{len(zh_sorted)} (earlier superseded in canonical)'
    if change_ids:
        frag += '; rule_change_candidate NOT applied: ' + ', '.join(change_ids)
    frag += (f'; faq attach: example_only={len(example)} rule_interpretation={len(interpretation)} '
             f'exception={len(exception)} (tier-1 conventions)')
    if not c.execute('SELECT 1 FROM reconciliations WHERE reconciliation_id=?', (rec_id,)).fetchone():
        c.execute(
            'INSERT INTO reconciliations (reconciliation_id, rule_id, source_id, original_fragment, '
            'corrected_fragment, modification_type, effective_scope, status) VALUES (?,?,?,?,?,?,?,?)',
            (rec_id, rule_id, 'multi-errata', frag, canonical_ev, 'replacement', 'card_text',
             'reconciled_tier2_errata'))
    else:
        stats['skipped_rec_exists'] += 1
    c.execute('COMMIT')

    stats['reconciled'] += 1
    stats['changes_added'] += n_chg
    stats['zh_errata_links'] += len(zh)
    stats['en_errata_links'] += len(en)
    stats['chained_rules'] += 1 if len(zh_sorted) > 1 else 0
    stats['faq_example'] += len(example)
    stats['faq_interpretation'] += len(interpretation)
    stats['faq_exception'] += len(exception)
    stats['faq_rcc'] += len(change_ids)
    if faq_verif:
        stats['faq_forced_verif'] += 1


def main():
    db = sqlite3.connect(DB)
    db.isolation_level = None
    c = db.cursor()

    rule_ids = [r[0] for r in c.execute(RULES_SQL)]
    stats = {'candidates': len(rule_ids), 'reconciled': 0, 'errors': 0,
             'changes_added': 0, 'skipped_chg_exists': 0, 'skipped_rec_exists': 0,
             'zh_errata_links': 0, 'en_errata_links': 0, 'chained_rules': 0,
             'faq_example': 0, 'faq_interpretation': 0, 'faq_exception': 0,
             'faq_rcc': 0, 'faq_forced_verif': 0}
    warnings = []

    for rule_id in rule_ids:
        try:
            process_rule(c, rule_id, stats, warnings)
        except Exception as ex:
            try:
                c.execute('ROLLBACK')
            except Exception:
                pass
            stats['errors'] += 1
            warnings.append(f'{rule_id}: ERROR {ex}')

    c.execute('BEGIN')
    if not c.execute('SELECT 1 FROM processing_tasks WHERE task_id=?', ('task_4b_04',)).fetchone():
        c.execute(
            'INSERT INTO processing_tasks (task_id, source_id, page_start, page_end, section, status, '
            "assigned_role, notes) VALUES ('task_4b_04', 'multi', NULL, NULL, 'stage4b_tier2_errata', "
            "'completed', 'agent', ?)", (json.dumps(stats),))
    else:
        c.execute("UPDATE processing_tasks SET status='completed', notes=? WHERE task_id='task_4b_04'",
                  (json.dumps(stats),))
    c.execute('COMMIT')

    v = {
        'rules_reconciled_total':
            c.execute("SELECT COUNT(*) FROM rules WHERE status='reconciled'").fetchone()[0],
        'rules_pending_left':
            c.execute("SELECT COUNT(*) FROM rules WHERE status='pending_reconciliation'").fetchone()[0],
        'needs_review':
            c.execute("SELECT COUNT(*) FROM rules WHERE status='needs_review'").fetchone()[0],
        'rcard_errata_reconciled':
            c.execute("SELECT COUNT(*) FROM rules r WHERE r.rule_id LIKE 'R-CARD-%' AND r.status='reconciled' "
                      "AND EXISTS (SELECT 1 FROM rule_evidence re WHERE re.rule_id=r.rule_id "
                      "AND re.relationship='replacement')").fetchone()[0],
        'rcard_errata_null_canonical':
            c.execute("SELECT COUNT(*) FROM rules r WHERE r.rule_id LIKE 'R-CARD-%' AND r.status='reconciled' "
                      "AND r.proposed_canonical_rule IS NULL AND EXISTS "
                      "(SELECT 1 FROM rule_evidence re WHERE re.rule_id=r.rule_id AND re.relationship='replacement')").fetchone()[0],
        'changes_rows_batch':
            c.execute("SELECT COUNT(*) FROM changes WHERE change_id LIKE 'CHG-4B-T2ER-%'").fetchone()[0],
        'rec_rows_batch':
            c.execute("SELECT COUNT(*) FROM reconciliations WHERE reconciliation_id LIKE 'REC-4B-T2ER-%'").fetchone()[0],
        'errata_rules_missing_changes':
            c.execute("SELECT COUNT(*) FROM rules r WHERE r.status='reconciled' AND r.rule_id LIKE 'R-CARD-%' "
                      "AND EXISTS (SELECT 1 FROM rule_evidence re WHERE re.rule_id=r.rule_id AND re.relationship='replacement') "
                      "AND NOT EXISTS (SELECT 1 FROM changes ch WHERE ch.rule_id=r.rule_id AND ch.change_id LIKE 'CHG-4B-T2ER-%')").fetchone()[0],
        'needs_verification_true_total':
            c.execute("SELECT COUNT(*) FROM rules WHERE needs_verification='true'").fetchone()[0],
    }

    now = datetime.now(timezone.utc).isoformat(timespec='seconds')
    with open(CHK, 'w', encoding='utf-8') as f:
        json.dump({'batch': '4B-B004-tier2-errata', 'finished_at': now, 'stats': stats,
                   'validation': v, 'warnings': warnings[:120]}, f, ensure_ascii=False, indent=2)
    with open(RPT, 'w', encoding='utf-8') as f:
        f.write('# Stage 4B batch 4B-B004 - Tier-2 errata application (130 R-CARD)\n\n')
        f.write(f'finished_at: {now}\n\n')
        f.write('Scope: 130 pending R-CARD rules with errata `replacement` links.\n')
        f.write('canonical = corrected_fragment of LATEST zh official errata (date-asc chain check, warning-only). '
                'EN errata recorded in changes w/o canonical change (paired zh governs). '
                'changes rows per errata evidence x rule. FAQ attach per tier-1 conventions; '
                'rule_change_candidate NOT applied. ALL 130 needs_verification=true (spec 15.7 errata-modified).\n\n')
        f.write(f'## stats\n```json\n{json.dumps(stats, indent=2, ensure_ascii=False)}\n```\n\n')
        f.write(f'## validation\n```json\n{json.dumps(v, indent=2)}\n```\n\n')
        f.write('## warnings (%d)\n' % len(warnings))
        for w in warnings:
            f.write(f'- {w}\n')

    print('stats:', json.dumps(stats, ensure_ascii=False))
    print('validation:', json.dumps(v))
    print('warnings:', len(warnings))
    for w in warnings[:25]:
        print(' -', w)


if __name__ == '__main__':
    sys.exit(main())
