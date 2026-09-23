"""Stage 4B batch 4B-B005 - Tier-1 flagged R-CR reconciliation (VERIF-FLAG adjudication).

Scope: 19 pending R-CR rules carrying 'VERIFICATION FLAG 4B' rule_evidence links
(explicit rule-number refs from pre-2026-07-renumbering sources 001/007) + MR-4A closure
+ 6 R-CR faq:rule_change_candidate links (source_007 0196 x5, 0201 x1).

Adjudication performed by operator agent on 2026-09-22 with full-text reads
(dump: workspace/checkpoints/stage4b_b005_dump.json; existence checks in current
rule-number space source_009). Per-link verdicts embedded below as data.

Verdict types:
  attach      -> citation VALID in current numbering; attach verbatim to field
                 (rule_interpretation->official_interpretation, exception->exception)
  stale_note  -> citation STALE (rule number reused/absent); content NOT written to
                 rule fields; successor pointer recorded in reconciliation frag;
                 link notes annotated
  incorporated-> RCC: FAQ-declared旧->新 revision already present in 2026-07 core
                 rules (same or relocated position); NOT applied (would double-apply);
                 changes row documents the historical revision

Authority: current 2026-07 core rules (source_009/018) > source_007 (2026-04-30) /
source_001 (2025-10-23, judge-community tier) per Group-C topology + spec 15.3/15.4.
canonical = zh official text for all 19 (same-version zh/en pairs).

Per-rule atomic COMMIT (spec 15.8). Idempotent + resumable.
"""
import json
import sqlite3
import sys
from datetime import datetime, timezone

DB = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db'
CHK = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\checkpoints\stage4b_tier1_flagged_checkpoint.json'
RPT = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\reports\stage4b_tier1_flagged.md'

JUDGE_SOURCES = {'source_001', 'source_006', 'source_008'}

# per-rule adjudication verdicts (operator, 2026-09-22)
# fields: nv = needs_verification; links: ev -> (verdict, note)
VERDICTS = {
    'R-CR-135.4': {'nv': False, 'links': {
        'EV-CN-FAQ-0205': ('attach', 'cites 135.4 + 718.2 verbatim; valid in current numbering')}},
    'R-CR-187.4': {'nv': True, 'links': {
        'EV-CN-FAQ-0196': ('incorporated', 'old 187.4.c battlefield-control rule no longer exists (187.4 = Mech token def); contradiction with cleanup rule resolved: control-loss consolidated at 323.6 new text'),
        'EV-CN-FAQ-0206': ('stale_note', 'cites old 187.4.c (open-state control); successor = 323.6; same evidence validly attached to R-CR-816.2 (816.2/816.2.a verbatim)'),
        'EV-CN-FAQ-0207': ('stale_note', 'cites old 187.4.c (chain-not-empty blocks control loss); successor = 323.6; interpretation relocated to R-CR-323.6 (new link, 4B-B005)')}},
    'R-CR-316.5': {'nv': True, 'links': {
        'EV-CN-FAQ-0196': ('incorporated', 'cited 316.5.b old showdown-marking text; 316.5.b now = Neutral Open State def; marking rule relocated to 323.8 with the NEW text verbatim')}},
    'R-CR-317.2': {'nv': True, 'links': {
        'EV-CN-FAQ-0030': ('attach', '[317.2.a] exists in current numbering; [440.1.a] STALE -> successor 466.1.a (MR-4A-0002); judge-community tier')}},
    'R-CR-323.1': {'nv': True, 'links': {
        'EV-CN-FAQ-0203': ('attach', 'cites 323.1 verbatim + 467 (exists); 466.1.b sub-ref STALE -> successor 471.1.b.1 (verified: not-scored-everywhere -> draw a card)')}},
    'R-CR-323.5': {'nv': True, 'links': {
        'EV-CN-FAQ-0198': ('attach', 'cites 323.5 (content-equivalent, reworded w/ 142.4 ref); 460.2.c.3 STALE -> successor 465.2.c.4(.a) verified (MR-4A-0005)')}},
    'R-CR-323.6': {'nv': True, 'links': {
        'EV-CN-FAQ-0196': ('incorporated', 'NEW text present in current 323.6 (minor reword, same condition); canonical unchanged'),
        'EV-CN-FAQ-0207': ('attach_relocated', 'relocated from R-CR-187.4 (stale ref 187.4.c -> successor 323.6); content = open-state control retention while chain items pending')}},
    'R-CR-323.8': {'nv': True, 'links': {
        'EV-CN-FAQ-0196': ('incorporated', 'current 323.8 text == 316.5.b NEW text verbatim (marking relocated here); canonical unchanged')}},
    'R-CR-333.1': {'nv': True, 'links': {
        'EV-CN-FAQ-0020': ('stale_note', 'cites [333.1.c.3] priority rule; current 333.1 = task list; successor = 340.4 (verified verbatim); judge-community tier')}},
    'R-CR-342.1': {'nv': True, 'links': {
        'EV-CN-FAQ-0011': ('stale_note', 'cites [342.1.a] + [376.3.b.1]; 342.1.a gone (342.1 = spell-chain creation); successors: 376.3.b.1 -> 383.3.d.1 (verified), defender-last -> 383.4.f + 466.x (MR-4A-0001); judge-community tier')}},
    'R-CR-344.2': {'nv': True, 'links': {
        'EV-CN-FAQ-0196': ('incorporated', 'NEW text present in current 344.2 (with extra Neutral Open State qualifier); canonical unchanged')}},
    'R-CR-359.3': {'nv': True, 'links': {
        'EV-CN-FAQ-0213': ('attach', 'exception; cites 359.3.e.3 verbatim (exists); valid'),
        'EV-CN-FAQ-0300': ('attach', 'cites 359.3.f.1/f.2/f.3/f.3.b (all exist); valid'),
        'EV-CN-FAQ-0321': ('attach', 'cites 359.3.f.3 (exists); valid')}},
    'R-CR-437.2': {'nv': False, 'links': {
        'EV-CN-FAQ-0210': ('attach', 'cites 437.2.a (exists, damage prevented to 0 = no damage dealt); valid')}},
    'R-CR-438.1': {'nv': False, 'links': {
        'EV-CN-FAQ-0204': ('attach', 'cites 438.1 verbatim + 438.7.b (exists); valid')}},
    'R-CR-440.1': {'nv': True, 'links': {
        'EV-CN-FAQ-0030': ('stale_note', 'cites [440.1.a] = old battle-cleanup specials; 440.1 = Burn now; successor 466.1.a (+318/324.1); judge-community tier'),
        'EV-CN-FAQ-0031': ('stale_note', 'cites [440.1.a.1-3]/[440.1.b] old battle cleanup; successors 466.1.a/466.1.a.1/.2 + 318 (MR-4A-0002); judge-community tier')}},
    'R-CR-461.3': {'nv': True, 'links': {
        'EV-CN-FAQ-0201': ('incorporated', 'cited 461.3.d old battle-outcome text; NEW text present verbatim at 466.3.d (incl. recalled-units clause); 461.3 now = combat showdown opening; canonical unchanged')}},
    'R-CR-466.1': {'nv': True, 'links': {
        'EV-CN-FAQ-0203': ('stale_note', 'cites 466.1.b scoring-action quote; current 466.1 = combat cleanup; successor = 471.1.b.1 (verified); same evidence validly attached to R-CR-323.1')}},
    'R-CR-718.2': {'nv': False, 'links': {
        'EV-CN-FAQ-0205': ('attach', 'cites 718.2 verbatim + 135.4; valid in current numbering')}},
    'R-CR-816.2': {'nv': False, 'links': {
        'EV-CN-FAQ-0206': ('attach', 'cites 816.2 + 816.2.a verbatim (exists); valid')}},
}

# changes rows: FAQ-declared rule revisions already incorporated into 2026-07 core rules
# (recorded for change_log; NOT applied -- current canonical already contains them)
CHANGES = [
    ('CHG-4B-T1F-0001', 'R-CR-187.4',
     '187.4.c.（旧）如果玩家在某战场上没有单位，且该回合处于开环状态，则除非该战场正在进行战斗或法术对决，否则该玩家会在后续的清理阶段失去该战场的控制权。',
     '323.6. 4.如果当前回合处于开环状态，且某处由某玩家控制的战场上没有正在进行的法术对决或战斗，若该处战场没有被该玩家控制的单位占据，则该玩家失去该战场的控制权。',
     'other',
     'FAQ(source_007) declares old 187.4.c contradicted cleanup rule 323.6; control-loss consolidated into 323.6 and 187.4.c removed (187.4 renumbered to Mech token def)',
     'incorporated into 2026-07 core rules; recorded, not applied'),
    ('CHG-4B-T1F-0002', 'R-CR-316.5',
     '316.5.b.（旧）当尚无控制者的战场进入争夺状态时，则将该战场上的法术对决标记为待发生。',
     '323.8. 6.如果战场进入了争夺状态，则将该战场上的法术对决标记为待发生。',
     'condition_change',
     'FAQ(source_007) declares 316.5.b wording change (uncontrolled-only -> any contested battlefield); rule relocated to 323.8; 316.5.b renumbered to Neutral Open State def',
     'incorporated into 2026-07 core rules at 323.8; recorded, not applied'),
    ('CHG-4B-T1F-0003', 'R-CR-323.6',
     '323.6.（旧）4.如果当前回合处于开环状态，则没有单位占据且没有法术对决或战斗正在进行的战场将变为未受控制状态。',
     '323.6.（新）4.如果当前回合处于开环状态，且某处战场上没有正在进行的法术对决或战斗，则玩家将失去未被其单位占据的已控制战场的控制权。',
     'condition_change',
     'FAQ(source_007) declares 323.6 wording change (battlefield becomes uncontrolled -> player loses control of occupied battlefield), resolving contradiction with old 187.4.c',
     'incorporated into 2026-07 core rules (current 323.6, minor reword); recorded, not applied'),
    ('CHG-4B-T1F-0004', 'R-CR-323.8',
     '316.5.b.（旧）当尚无控制者的战场进入争夺状态时，则将该战场上的法术对决标记为待发生。',
     '323.8. 6.如果战场进入了争夺状态，则将该战场上的法术对决标记为待发生。',
     'condition_change',
     'FAQ(source_007) declares showdown-marking now applies to any contested battlefield (cleanup-flow rule takes precedence); carries the 316.5.b NEW text at relocated position 323.8',
     'incorporated into 2026-07 core rules; recorded, not applied'),
    ('CHG-4B-T1F-0005', 'R-CR-344.2',
     '344.2.（旧）如果某处战场的控制权受到争夺，且在争夺发生时处于无人控制状态，则会在导致该战场进入争夺状态的行动结束后的清理步骤中展开法术对决。',
     '344.2.（新）如果某处战场的控制权受到争夺，且该战场上没有由不同玩家控制的单位，则会在导致该战场进入争夺状态的行动结束后的清理步骤中展开法术对决。',
     'condition_change',
     'FAQ(source_007) declares 344.2 condition change (uncontrolled-when-contested -> no units of different players present)',
     'incorporated into 2026-07 core rules (current 344.2 adds Neutral Open State qualifier); recorded, not applied'),
    ('CHG-4B-T1F-0006', 'R-CR-461.3',
     '461.3.d.（旧）如果在此步骤期间，双方玩家都拥有单位，或双方都没有单位，则战斗"无结果"。',
     '466.3.d. 如果在战斗清理的第3d 步骤时，有单位被召回、或双方玩家在此任务期间仍有单位在战场上、或双方玩家在此任务期间都没有单位在战场上，则战斗"无结果"。',
     'condition_change',
     'FAQ(source_007) declares 461.3.d no-result condition adds recalled-units case; rule relocated to 466.3.d in 2026-07 renumbering',
     'incorporated into 2026-07 core rules at 466.3.d (verbatim incl. recall clause); recorded, not applied'),
]

MR4A_CLOSURES = {
    'MR-4A-0001': 'successor coverage verified: 383.3.d.1 == simultaneous multi-player triggers placed in turn order (verbatim match of general rule); defender-triggers-last specifics carried by 383.4.f (防守触发 def, verified) + 466.x resolution steps. FAQ ruling fully covered by successors. CLOSED.',
    'MR-4A-0002': 'successor coverage verified: 324.1 (special cleanup steps determined by triggering category, combat -> 466) verbatim match of FAQ claim structure; 466.1.a 启动战斗特殊清理 + 466.1.a.1/.2 insert steps (3c remove damage / 3d recall attackers) cover old [440.1.a.1-3]; 318 cleanup flow covers old 322.2/322.3 sequence position. CLOSED.',
    'MR-4A-0003': 'successor coverage verified (same mapping family as MR-4A-0002): damage-mark clearing now inserted as step 3c via 466.1.a.1 during combat special cleanup; KogMaw Last Breath trigger chain-finalize per 324 special-cleanup flow. Old 440.x (Burn) number-reuse confirmed. CLOSED.',
    'MR-4A-0004': 'successor coverage verified: 809.1.c text == 735.1.c（修订后）semantics verbatim (Ward keyword shorthand; MR-2D-0007 incorporation precedent). CLOSED.',
    'MR-4A-0005': 'successor coverage verified: 465.2.c.4(.a) == lethal-minimum allocation rule (verbatim content match with old 460.2.c.3); current 323.5 (3b lethal-destroy, refs 142.4) content-consistent with FAQ quote. CLOSED.',
    'MR-4A-0006': 'successor coverage verified: current 335 (no pending tasks/items -> main phase priority / other phase advance) matches old 335.3 quote verbatim (plus showdown/combat clause); 334.1 HOT task-handling exists; HOT FEPR naming逐字对应. CLOSED.',
}

FAQ_SQL = """
SELECT re.relationship, e.evidence_id, e.source_id, e.faq_question, e.faq_answer, e.original_text
FROM rule_evidence re JOIN evidence e ON e.evidence_id = re.evidence_id
WHERE re.rule_id = ? AND e.evidence_id = ?
"""

FLAG_NOTE = '4B-B005 adjudicated VERIF-FLAG: '


def tier_of(src):
    return 'judge-community' if src in JUDGE_SOURCES else 'official'


def build_entry(cls, ev_id, src, q, a, orig):
    head = f'[{ev_id} | {src} | {tier_of(src)} | {cls}]'
    body = f'Q: {q}\nA: {a}' if q and a else (orig or '').strip()
    return f'{head}\n{body}'


def process_rule(c, rule_id, verdict, stats, warnings):
    links_v = verdict['links']
    same = c.execute(
        "SELECT e.source_language, e.original_text FROM rule_evidence re "
        "JOIN evidence e ON e.evidence_id = re.evidence_id "
        "WHERE re.rule_id=? AND re.relationship='same'", (rule_id,)).fetchall()
    zh = [t for lang, t in same if lang == 'zh']
    if len(zh) != 1:
        raise ValueError(f'expected 1 zh same-link, got {len(zh)}')
    canonical = zh[0]

    oi, exc = [], []
    frags = []
    for ev_id, (vtype, note) in sorted(links_v.items()):
        row = c.execute(FAQ_SQL, (rule_id, ev_id)).fetchone()
        if not row and vtype != 'attach_relocated':
            raise ValueError(f'link missing: {rule_id} <- {ev_id}')
        if vtype == 'attach_relocated':
            # create relocated link + attach content to this rule
            if not c.execute('SELECT 1 FROM rule_evidence WHERE rule_id=? AND evidence_id=?',
                             (rule_id, ev_id)).fetchone():
                c.execute(
                    "INSERT INTO rule_evidence (rule_id, evidence_id, relationship, confidence, notes) "
                    "VALUES (?,?,?,?,?)",
                    (rule_id, ev_id, 'faq:rule_interpretation', 'medium',
                     'relocated 4B-B005 from R-CR-187.4 (stale ref 187.4.c -> successor 323.6)'))
                stats['links_relocated'] += 1
            er = c.execute(
                "SELECT source_id, faq_question, faq_answer, original_text FROM evidence WHERE evidence_id=?",
                (ev_id,)).fetchone()
            oi.append(build_entry('rule_interpretation', ev_id, er[0], er[1], er[2], er[3]))
            frags.append(f'{ev_id}: attach_relocated ({note})')
            stats['entries_oi'] += 1
            continue
        rel, _ev, src, q, a, orig = row
        cls = rel.split(':', 1)[1]
        if vtype == 'attach':
            entry = build_entry(cls, ev_id, src, q, a, orig)
            if cls == 'exception':
                exc.append(entry)
                stats['entries_exc'] += 1
            else:
                oi.append(entry)
                stats['entries_oi'] += 1
            frags.append(f'{ev_id}: attach ({note})')
        elif vtype == 'stale_note':
            frags.append(f'{ev_id}: STALE REF - content not attached to this cluster ({note})')
            stats['links_stale'] += 1
        elif vtype == 'incorporated':
            frags.append(f'{ev_id}: rule_change_candidate INCORPORATED into 2026-07 core rules - NOT applied, recorded ({note})')
            stats['links_rcc_incorporated'] += 1
        else:
            raise ValueError(f'unknown verdict {vtype}')
        # annotate link notes
        old = c.execute('SELECT notes FROM rule_evidence WHERE rule_id=? AND evidence_id=?',
                        (rule_id, ev_id)).fetchone()
        if old and FLAG_NOTE not in (old[0] or ''):
            c.execute('UPDATE rule_evidence SET notes=? WHERE rule_id=? AND evidence_id=?',
                      ((old[0] or '') + ' | ' + FLAG_NOTE + vtype + ' - ' + note, rule_id, ev_id))

    rec_id = f'REC-4B-T1F-{rule_id}'
    frag = ('VERIF-FLAG adjudication (4B-B005): ' + ' || '.join(frags) +
            '; canonical=zh official text, en=official reference (same-version equivalent pair)')
    c.execute('BEGIN')
    c.execute(
        "UPDATE rules SET proposed_canonical_rule=?, example=NULL, official_interpretation=?, "
        "exception=?, status='reconciled', needs_verification=? WHERE rule_id=?",
        (canonical, '\n\n'.join(oi) if oi else None, '\n\n'.join(exc) if exc else None,
         'true' if verdict['nv'] else 'false', rule_id))
    if not c.execute('SELECT 1 FROM reconciliations WHERE reconciliation_id=?', (rec_id,)).fetchone():
        c.execute(
            'INSERT INTO reconciliations (reconciliation_id, rule_id, source_id, original_fragment, '
            'corrected_fragment, modification_type, effective_scope, status) VALUES (?,?,?,?,?,?,?,?)',
            (rec_id, rule_id, 'multi-faq', frag, None, 'none', 'faq_attach_flagged', 'reconciled_tier1f'))
    else:
        stats['skipped_exists'] += 1
    c.execute('COMMIT')
    stats['reconciled'] += 1
    if verdict['nv']:
        stats['flagged_verification'] += 1


def main():
    db = sqlite3.connect(DB)
    db.isolation_level = None
    c = db.cursor()

    stats = {'candidates': len(VERDICTS), 'reconciled': 0, 'skipped_exists': 0, 'errors': 0,
             'flagged_verification': 0, 'entries_oi': 0, 'entries_exc': 0,
             'links_stale': 0, 'links_rcc_incorporated': 0, 'links_relocated': 0,
             'changes_written': 0, 'mr4a_closed': 0}
    warnings = []

    for rule_id, verdict in VERDICTS.items():
        try:
            process_rule(c, rule_id, verdict, stats, warnings)
        except Exception as ex:
            try:
                c.execute('ROLLBACK')
            except Exception:
                pass
            stats['errors'] += 1
            warnings.append(f'{rule_id}: ERROR {ex}')

    # changes rows (idempotent)
    c.execute('BEGIN')
    for chg_id, rid, old, new, mtype, reason, concl in CHANGES:
        if not c.execute('SELECT 1 FROM changes WHERE change_id=?', (chg_id,)).fetchone():
            c.execute(
                'INSERT INTO changes (change_id, rule_id, original_content, new_content, source_type, '
                'source_language, source_document, version, date, modification_type, reason, final_conclusion) '
                'VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                (chg_id, rid, old, new, 'faq', 'zh', '07_2026-04-30_破限系列_官方FAQ.pdf',
                 'v2026', '2026-04-30', mtype, reason, concl))
            stats['changes_written'] += 1
    # MR-4A closures
    for item_id, closure in MR4A_CLOSURES.items():
        row = c.execute('SELECT issue_description FROM manual_review WHERE item_id=?', (item_id,)).fetchone()
        if row and '4B-B005 结案' not in row[0]:
            c.execute('UPDATE manual_review SET issue_description=? WHERE item_id=?',
                      (row[0] + '\n[2026-09-22 4B-B005 结案] ' + closure, item_id))
            stats['mr4a_closed'] += 1
    # R-CR-438.7 flag clear note (already reconciled in 4B-B003; citation verified valid)
    r7 = c.execute("SELECT notes FROM rule_evidence WHERE rule_id='R-CR-438.7' AND evidence_id='EV-CN-FAQ-0204'").fetchone()
    if r7 and FLAG_NOTE not in (r7[0] or ''):
        c.execute("UPDATE rule_evidence SET notes=? WHERE rule_id='R-CR-438.7' AND evidence_id='EV-CN-FAQ-0204'",
                  ((r7[0] or '') + ' | ' + FLAG_NOTE + 'citation valid - 438.7.b exists verbatim in current numbering; flag cleared, rule stays needs_verification=true (tr-diff batch)',))
    # task row
    if not c.execute('SELECT 1 FROM processing_tasks WHERE task_id=?', ('task_4b_05',)).fetchone():
        c.execute(
            'INSERT INTO processing_tasks (task_id, source_id, page_start, page_end, section, status, assigned_role, notes) '
            "VALUES ('task_4b_05', 'multi', NULL, NULL, 'stage4b_tier1_flagged_reconciliation', 'completed', 'agent', ?)",
            (json.dumps(stats, ensure_ascii=False),))
    else:
        c.execute("UPDATE processing_tasks SET status='completed', notes=? WHERE task_id='task_4b_05'",
                  (json.dumps(stats, ensure_ascii=False),))
    c.execute('COMMIT')

    v = {
        'rules_reconciled_total': c.execute("SELECT COUNT(*) FROM rules WHERE status='reconciled'").fetchone()[0],
        'rules_pending': c.execute("SELECT COUNT(*) FROM rules WHERE status='pending_reconciliation'").fetchone()[0],
        'pending_rcr_left': c.execute("SELECT COUNT(*) FROM rules WHERE status='pending_reconciliation' AND rule_id LIKE 'R-CR-%'").fetchone()[0],
        'rec_tier1f': c.execute("SELECT COUNT(*) FROM reconciliations WHERE reconciliation_id LIKE 'REC-4B-T1F-%'").fetchone()[0],
        'reconciled_missing_rec': c.execute(
            "SELECT COUNT(*) FROM rules r WHERE r.status='reconciled' AND NOT EXISTS "
            "(SELECT 1 FROM reconciliations x WHERE x.rule_id=r.rule_id)").fetchone()[0],
        'needs_verification_true': c.execute("SELECT COUNT(*) FROM rules WHERE needs_verification='true'").fetchone()[0],
        'changes_total': c.execute('SELECT COUNT(*) FROM changes').fetchone()[0],
        'mr4a_open_left': c.execute(
            "SELECT COUNT(*) FROM manual_review WHERE item_id LIKE 'MR-4A-%' AND issue_description NOT LIKE '%4B-B005 结案%'").fetchone()[0],
        'verif_flag_left': c.execute(
            "SELECT COUNT(*) FROM rule_evidence WHERE notes LIKE '%VERIFICATION FLAG 4B%' AND notes NOT LIKE '%4B-B005 adjudicated%'").fetchone()[0],
    }

    now = datetime.now(timezone.utc).isoformat(timespec='seconds')
    with open(CHK, 'w', encoding='utf-8') as f:
        json.dump({'batch': '4B-B005-tier1-flagged', 'finished_at': now, 'stats': stats,
                   'validation': v, 'warnings': warnings}, f, ensure_ascii=False, indent=2)
    with open(RPT, 'w', encoding='utf-8') as f:
        f.write('# Stage 4B batch 4B-B005 - Tier-1 flagged R-CR reconciliation (VERIF-FLAG adjudication)\n\n')
        f.write(f'finished_at: {now}\n\n')
        f.write('Scope: 19 pending R-CR with VERIF-FLAG links + 6 R-CR rule_change_candidate links '
                '(source_007) + MR-4A-0001..0006 closure + R-CR-438.7 flag clear.\n\n')
        f.write('Authority: current 2026-07 core rules (source_009/018) > source_007 (2026-04-30) / '
                'source_001 (judge-community). canonical = zh official text. RCC links all INCORPORATED '
                '(recorded via CHG-4B-T1F-0001..0006, NOT applied).\n')
        f.write('Remaining 128 faq:rule_change_candidate links attach to R-TOPIC-EN (100), R-MISC (16), '
                'R-CARD (11), R-TOPIC-CN (1) rules -> deferred to next batch with those rules '
                '(incl. MR-2D-0010 patch-notes adjudication: 012/014/016 transitional < current core; '
                '019 post-dates core -> authoritative side).\n\n')
        f.write('## verdicts per rule\n')
        for rid, vd in VERDICTS.items():
            f.write(f'- {rid} (needs_verification={vd["nv"]})\n')
            for ev, (vt, note) in sorted(vd['links'].items()):
                f.write(f'  - {ev}: {vt} -- {note}\n')
        f.write('\n## MR-4A closures\n')
        for k, t in MR4A_CLOSURES.items():
            f.write(f'- {k}: {t}\n')
        f.write(f'\n## stats\n```json\n{json.dumps(stats, ensure_ascii=False, indent=2)}\n```\n\n')
        f.write(f'## validation\n```json\n{json.dumps(v, indent=2)}\n```\n\n')
        f.write('## warnings (%d)\n' % len(warnings))
        for w in warnings:
            f.write(f'- {w}\n')

    print('stats:', json.dumps(stats, ensure_ascii=False))
    print('validation:', json.dumps(v))
    print('warnings:', len(warnings))
    for w in warnings:
        print(' -', w)
    return 1 if stats['errors'] else 0


if __name__ == '__main__':
    sys.exit(main())
