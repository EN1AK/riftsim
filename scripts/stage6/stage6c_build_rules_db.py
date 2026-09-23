# -*- coding: utf-8 -*-
"""
Stage 6C: build workspace/final/rules.db from workspace/rules_work.db (idempotent full rebuild).

Per spec 17.2 rules.db must support queries by:
  rule_id / topic / card_id / keyword / trigger / source / version

Schema of the OUTPUT database (workspace/final/rules.db):
  rules             2984 rows — all source rules columns + verification_status (LEFT JOIN verification);
                    proposed_canonical_rule stays NULL for the 472 FAQ-only R-CARD rows (never fabricated)
  rule_sources      6353 rows — rule_evidence JOIN evidence (rule_id, evidence_id, relationship,
                    source_id/type/language/document, version, date, page, section, rule_number)
                    -> 'source' and 'version' query dimensions
  rule_cards        rule_id <-> card_id (origin='rule_id' parsed from R-CARD-* ids;
                    origin='evidence' from evidence.card_ids JSON via rule_evidence links)
                    -> 'card_id' query dimension
  rule_keywords     bracket-token [X] heuristic over canonical/OI/example/exception text
                    (drops pure-digit and single-char cost/rune symbols; heuristic documented in meta)
                    -> 'keyword' query dimension (structured)
  rules_fts         FTS5 over topic+canonical+OI+example+exception (if FTS5 available)
                    -> 'keyword' query dimension (full text)
  rule_verification 393 rows — full copy of verification table (traceability)
  rule_changes      267 rows — full copy of changes table (traceability; change_log.md is 6D)
  meta              build info / stats / validation summary

Idempotent: deletes the output file and rebuilds deterministically from rules_work.db.
Registers/updates task_6_03, writes workspace/checkpoints/stage6c_checkpoint.json.
Prints short stats only; never dumps rule content to stdout.
"""
import sqlite3, json, re, os, sys, datetime

SRC = 'workspace/rules_work.db'
OUT = 'workspace/final/rules.db'
CKPT = 'workspace/checkpoints/stage6c_checkpoint.json'

def now():
    return datetime.datetime.now().isoformat(timespec='seconds')

BRACKET = re.compile(r'\[([^\[\]]{1,40})\]')
CJK = re.compile(r'[\u4e00-\u9fff]')
CARD_ID = re.compile(r'^[A-Z]{3,4}-[A-Z]*\d+[a-z*]?$')  # plain numbers + T/R/SP-prefixed token/rune/special ids
RCARD = re.compile(r'^R-CARD-([A-Z]{3,4}-\d+)$')

def keep_keyword(tok):
    t = tok.strip()
    if not t:
        return None
    if t.isdigit():            # [1] [12] cost numbers
        return None
    if len(t) == 1:            # [C] [E] [A] [M] ... single-char cost/rune symbols
        return None
    if not (CJK.search(t) or re.search(r'[A-Za-z]', t)):
        return None
    return t

def main():
    c = sqlite3.connect(SRC)
    c.row_factory = sqlite3.Row
    cur = c.cursor()

    # --- register task (idempotent; cols: task_id/source_id/page_start/page_end/section/status/assigned_role/notes) ---
    row = cur.execute("SELECT task_id, status FROM processing_tasks WHERE task_id='task_6_03'").fetchone()
    note = (f'Stage 6C rules.db build; script stage6c_build_rules_db.py (idempotent); '
            f'output {OUT}; checkpoint {CKPT}; started {now()}')
    if row is None:
        prev = cur.execute("SELECT assigned_role FROM processing_tasks WHERE task_id='task_6_01'").fetchone()
        role = prev['assigned_role'] if prev else 'agent'
        cur.execute(
            "INSERT INTO processing_tasks (task_id, source_id, page_start, page_end, section, status, assigned_role, notes) "
            "VALUES (?,?,?,?,?,?,?,?)",
            ('task_6_03', None, None, None, 'stage6c_rules_db', 'running', role, note))
    else:
        cur.execute("UPDATE processing_tasks SET status='running', notes=? WHERE task_id='task_6_03'", (note,))
    c.commit()

    # --- load source data ---
    rules = [dict(r) for r in cur.execute("SELECT * FROM rules")]
    vmap = {}
    for r in cur.execute("SELECT rule_id, status FROM verification"):
        vmap[r['rule_id']] = r['status']
    verification = [dict(r) for r in cur.execute("SELECT * FROM verification")]
    changes = [dict(r) for r in cur.execute("SELECT * FROM changes")]
    links = [dict(r) for r in cur.execute("""
        SELECT re.rule_id, re.evidence_id, re.relationship, re.confidence,
               e.source_id, e.source_type, e.source_language, e.source_document,
               e.version, e.date, e.page, e.section, e.rule_number, e.card_ids
        FROM rule_evidence re LEFT JOIN evidence e ON e.evidence_id = re.evidence_id
    """)]

    # --- build output db from scratch ---
    if os.path.exists(OUT):
        os.remove(OUT)
    o = sqlite3.connect(OUT)
    oc = o.cursor()
    oc.executescript("""
    CREATE TABLE rules (
        rule_id TEXT PRIMARY KEY,
        topic TEXT,
        proposed_canonical_rule TEXT,
        applicable_object TEXT,
        trigger TEXT,
        precondition TEXT,
        effect TEXT,
        restriction TEXT,
        exception TEXT,
        official_interpretation TEXT,
        derived_interpretation TEXT,
        example TEXT,
        status TEXT,
        needs_verification TEXT,
        verification_status TEXT
    );
    CREATE INDEX idx_rules_topic ON rules(topic);
    CREATE INDEX idx_rules_trigger ON rules(trigger);
    CREATE INDEX idx_rules_status ON rules(status);
    CREATE INDEX idx_rules_verification ON rules(verification_status);

    CREATE TABLE rule_sources (
        rule_id TEXT NOT NULL,
        evidence_id TEXT,
        relationship TEXT,
        confidence TEXT,
        source_id TEXT,
        source_type TEXT,
        source_language TEXT,
        source_document TEXT,
        version TEXT,
        date TEXT,
        page INTEGER,
        section TEXT,
        rule_number TEXT
    );
    CREATE INDEX idx_rs_rule ON rule_sources(rule_id);
    CREATE INDEX idx_rs_evidence ON rule_sources(evidence_id);
    CREATE INDEX idx_rs_source ON rule_sources(source_id);
    CREATE INDEX idx_rs_document ON rule_sources(source_document);
    CREATE INDEX idx_rs_version ON rule_sources(version);

    CREATE TABLE rule_cards (
        rule_id TEXT NOT NULL,
        card_id TEXT NOT NULL,
        origin TEXT NOT NULL
    );
    CREATE INDEX idx_rc_card ON rule_cards(card_id);
    CREATE INDEX idx_rc_rule ON rule_cards(rule_id);

    CREATE TABLE rule_keywords (
        rule_id TEXT NOT NULL,
        keyword TEXT NOT NULL,
        source_field TEXT NOT NULL
    );
    CREATE INDEX idx_rk_keyword ON rule_keywords(keyword);
    CREATE INDEX idx_rk_rule ON rule_keywords(rule_id);

    CREATE TABLE rule_verification (
        verification_id TEXT,
        rule_id TEXT,
        status TEXT,
        notes TEXT,
        stage4_conclusion TEXT,
        verification_conclusion TEXT,
        relevant_evidence TEXT,
        disagreement_reason TEXT,
        verified_at TEXT
    );
    CREATE INDEX idx_rv_rule ON rule_verification(rule_id);

    CREATE TABLE rule_changes (
        change_id TEXT PRIMARY KEY,
        rule_id TEXT,
        original_content TEXT,
        new_content TEXT,
        source_type TEXT,
        source_language TEXT,
        source_document TEXT,
        version TEXT,
        date TEXT,
        modification_type TEXT,
        reason TEXT,
        final_conclusion TEXT
    );
    CREATE INDEX idx_rch_rule ON rule_changes(rule_id);

    CREATE TABLE meta (k TEXT PRIMARY KEY, v TEXT);
    """)

    # rules
    rule_cols = ['rule_id','topic','proposed_canonical_rule','applicable_object','trigger','precondition',
                 'effect','restriction','exception','official_interpretation','derived_interpretation',
                 'example','status','needs_verification']
    oc.executemany(
        "INSERT INTO rules (rule_id,topic,proposed_canonical_rule,applicable_object,trigger,precondition,"
        "effect,restriction,exception,official_interpretation,derived_interpretation,example,status,"
        "needs_verification,verification_status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [tuple(r.get(col) for col in rule_cols) + (vmap.get(r['rule_id']),) for r in rules])

    # rule_sources
    oc.executemany(
        "INSERT INTO rule_sources (rule_id,evidence_id,relationship,confidence,source_id,source_type,"
        "source_language,source_document,version,date,page,section,rule_number) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [(l['rule_id'], l['evidence_id'], l['relationship'], l['confidence'], l['source_id'], l['source_type'],
          l['source_language'], l['source_document'], l['version'], l['date'], l['page'], l['section'],
          l['rule_number']) for l in links])

    # rule_cards: from R-CARD rule_id + evidence.card_ids JSON
    card_rows = set()
    for r in rules:
        m = RCARD.match(r['rule_id'])
        if m:
            card_rows.add((r['rule_id'], m.group(1), 'rule_id'))
    malformed = []
    for l in links:
        raw = l.get('card_ids')
        if not raw:
            continue
        try:
            ids = json.loads(raw)
        except Exception:
            malformed.append((l['evidence_id'], raw[:60]))
            continue
        for cid in ids:
            cid = (cid or '').strip()
            if not cid:
                continue
            if not CARD_ID.match(cid):
                malformed.append((l['evidence_id'], cid))
            card_rows.add((l['rule_id'], cid, 'evidence'))
    oc.executemany("INSERT INTO rule_cards (rule_id, card_id, origin) VALUES (?,?,?)",
                   sorted(card_rows))

    # rule_keywords: bracket-token heuristic over text fields
    kw_rows = set()
    for r in rules:
        for field in ('proposed_canonical_rule','official_interpretation','example','exception'):
            txt = r.get(field) or ''
            for tok in BRACKET.findall(txt):
                t = keep_keyword(tok)
                if t:
                    kw_rows.add((r['rule_id'], t, field))
    oc.executemany("INSERT INTO rule_keywords (rule_id, keyword, source_field) VALUES (?,?,?)",
                   sorted(kw_rows))

    # rule_verification / rule_changes (full copies)
    oc.executemany(
        "INSERT INTO rule_verification (verification_id,rule_id,status,notes,stage4_conclusion,"
        "verification_conclusion,relevant_evidence,disagreement_reason,verified_at) VALUES (?,?,?,?,?,?,?,?,?)",
        [(v['verification_id'], v['rule_id'], v['status'], v['notes'], v['stage4_conclusion'],
          v['verification_conclusion'], v['relevant_evidence'], v['disagreement_reason'],
          v['verified_at']) for v in verification])
    oc.executemany(
        "INSERT INTO rule_changes (change_id,rule_id,original_content,new_content,source_type,"
        "source_language,source_document,version,date,modification_type,reason,final_conclusion) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        [(ch['change_id'], ch['rule_id'], ch['original_content'], ch['new_content'], ch['source_type'],
          ch['source_language'], ch['source_document'], ch['version'], ch['date'], ch['modification_type'],
          ch['reason'], ch['final_conclusion']) for ch in changes])

    # FTS5 (optional)
    fts_ok = True
    try:
        oc.execute("CREATE VIRTUAL TABLE rules_fts USING fts5(rule_id UNINDEXED, text)")
        oc.executemany(
            "INSERT INTO rules_fts (rule_id, text) VALUES (?,?)",
            [(r['rule_id'],
              '\n'.join(x for x in [r.get('topic') or '', r.get('proposed_canonical_rule') or '',
                                    r.get('official_interpretation') or '', r.get('example') or '',
                                    r.get('exception') or ''] if x)) for r in rules])
    except sqlite3.OperationalError:
        fts_ok = False

    meta = {
        'built_at': now(),
        'source_db': SRC,
        'builder': 'stage6c_build_rules_db.py (idempotent full rebuild)',
        'spec': '17.2 — query dimensions: rule_id / topic / card_id / keyword / trigger / source / version',
        'null_canonical_policy': 'FAQ-only R-CARD rows keep proposed_canonical_rule NULL (never fabricated)',
        'keyword_heuristic': 'bracket tokens [X] from canonical/OI/example/exception; pure-digit and single-char cost/rune symbols dropped',
        'fts5': 'available' if fts_ok else 'UNAVAILABLE - use rule_keywords / LIKE queries',
        'trigger_field_note': 'structural extraction only: trigger column NULL by design (semantics in canonical text)',
    }
    oc.executemany("INSERT INTO meta (k,v) VALUES (?,?)", sorted(meta.items()))
    o.commit()

    # ---------------- validation ----------------
    val = {}
    val['rules_rows'] = oc.execute("SELECT COUNT(*) FROM rules").fetchone()[0]
    val['rules_match'] = val['rules_rows'] == len(rules) == 2984
    val['null_canonical'] = oc.execute(
        "SELECT COUNT(*) FROM rules WHERE proposed_canonical_rule IS NULL OR TRIM(proposed_canonical_rule)=''").fetchone()[0]
    val['null_canonical_ok'] = val['null_canonical'] == 472
    val['rs_rows'] = oc.execute("SELECT COUNT(*) FROM rule_sources").fetchone()[0]
    val['rs_match'] = val['rs_rows'] == len(links) == 6353
    val['orphan_sources'] = oc.execute(
        "SELECT COUNT(*) FROM rule_sources rs LEFT JOIN rules r ON r.rule_id=rs.rule_id WHERE r.rule_id IS NULL").fetchone()[0]
    val['rules_without_source'] = oc.execute(
        "SELECT COUNT(*) FROM rules r WHERE NOT EXISTS (SELECT 1 FROM rule_sources rs WHERE rs.rule_id=r.rule_id)").fetchone()[0]
    val['rc_rows'] = oc.execute("SELECT COUNT(*) FROM rule_cards").fetchone()[0]
    val['rc_rules'] = oc.execute("SELECT COUNT(DISTINCT rule_id) FROM rule_cards").fetchone()[0]
    val['rk_rows'] = oc.execute("SELECT COUNT(*) FROM rule_keywords").fetchone()[0]
    val['rk_distinct'] = oc.execute("SELECT COUNT(DISTINCT keyword) FROM rule_keywords").fetchone()[0]
    val['malformed_card_ids'] = len(malformed)
    val['rv_rows'] = oc.execute("SELECT COUNT(*) FROM rule_verification").fetchone()[0]
    val['rv_match'] = val['rv_rows'] == 393
    val['rch_rows'] = oc.execute("SELECT COUNT(*) FROM rule_changes").fetchone()[0]
    val['rch_match'] = val['rch_rows'] == 267
    # query-dimension smoke tests
    q = {}
    q['by_rule_id'] = oc.execute("SELECT COUNT(*) FROM rules WHERE rule_id='R-CR-811.1.b'").fetchone()[0]
    q['by_topic'] = oc.execute("SELECT COUNT(*) FROM rules WHERE topic LIKE 'faq topic%'").fetchone()[0]
    q['by_card_id'] = oc.execute("SELECT COUNT(DISTINCT rule_id) FROM rule_cards WHERE card_id='OGN-107'").fetchone()[0]
    q['by_keyword'] = oc.execute("SELECT COUNT(DISTINCT rule_id) FROM rule_keywords WHERE keyword='迅捷'").fetchone()[0]
    q['by_source'] = oc.execute("SELECT COUNT(DISTINCT rule_id) FROM rule_sources WHERE source_id='source_019'").fetchone()[0]
    q['by_version'] = oc.execute("SELECT COUNT(*) FROM rule_sources WHERE version IS NOT NULL AND version!=''").fetchone()[0]
    q['by_trigger_col'] = oc.execute("SELECT COUNT(*) FROM rules WHERE trigger IS NOT NULL AND trigger!=''").fetchone()[0]
    q['spot_811'] = 1 if oc.execute(
        "SELECT 1 FROM rules WHERE rule_id='R-CR-811.1.b' AND verification_status='verified_with_changes'").fetchone() else 0
    q['spot_watch_card'] = 1 if oc.execute(
        "SELECT 1 FROM rules WHERE rule_id='R-CARD-OGN-251'").fetchone() else 0
    if fts_ok:
        q['fts_smoke'] = oc.execute("SELECT COUNT(*) FROM rules_fts WHERE rules_fts MATCH '迅捷'").fetchone()[0]
    smoke_ok = (q['by_rule_id'] == 1 and q['by_topic'] > 0 and q['by_card_id'] >= 1
                and q['by_keyword'] > 0 and q['by_source'] > 0 and q['spot_811'] == 1
                and q['spot_watch_card'] == 1 and (not fts_ok or q.get('fts_smoke', 0) > 0))

    val['smoke_queries'] = q
    val['fts5'] = fts_ok
    ok = (val['rules_match'] and val['null_canonical_ok'] and val['rs_match']
          and val['orphan_sources'] == 0 and val['rules_without_source'] == 0
          and val['malformed_card_ids'] == 0 and val['rv_match'] and val['rch_match'] and smoke_ok)
    val['PASS'] = ok
    oc.execute("INSERT INTO meta (k,v) VALUES ('validation', ?)", (json.dumps(val, ensure_ascii=False),))
    o.commit()
    o.close()

    ckpt = {
        'task_id': 'task_6_03', 'stage': '6C', 'output': OUT, 'built_at': now(),
        'stats': {'rules': val['rules_rows'], 'null_canonical': val['null_canonical'],
                  'rule_sources': val['rs_rows'], 'rule_cards': val['rc_rows'],
                  'rule_cards_rules': val['rc_rules'], 'rule_keywords': val['rk_rows'],
                  'distinct_keywords': val['rk_distinct'], 'verification': val['rv_rows'],
                  'changes': val['rch_rows'], 'fts5': fts_ok},
        'validation': val,
    }
    with open(CKPT, 'w', encoding='utf-8') as f:
        json.dump(ckpt, f, ensure_ascii=False, indent=2)

    if ok:
        cur.execute("UPDATE processing_tasks SET status='completed', notes=? WHERE task_id='task_6_03'",
                    (f'Stage 6C rules.db build COMPLETED {now()}; script stage6c_build_rules_db.py (idempotent); '
                     f'output {OUT}; rules 2984 (null canonical 472), rule_sources 6353, rule_cards {val["rc_rows"]}, '
                     f'rule_keywords {val["rk_rows"]}/{val["rk_distinct"]} distinct, verification 393, changes 267, '
                     f'fts5={fts_ok}; validation PASS; checkpoint {CKPT}',))
    else:
        cur.execute("UPDATE processing_tasks SET status='failed', notes=? WHERE task_id='task_6_03'",
                    ('validation failed: ' + json.dumps(val, ensure_ascii=False),))
    c.commit()
    c.close()

    print(json.dumps({'stats': ckpt['stats'], 'validation': val}, ensure_ascii=False, indent=2))
    print('RESULT:', 'PASS - task_6_03 completed' if ok else 'FAIL')
    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
