# -*- coding: utf-8 -*-
"""Stage 2B verification: completeness/quality of EN Core Rules evidence (source_018)."""
import sqlite3, re, json, random

con = sqlite3.connect('workspace/rules_work.db')
cur = con.cursor()

EN_TXT = 'extracted/riftbound_en_rules__07_2026-07-16_Core_Rules.txt'
PAGE_RE = re.compile(r"^===== PAGE (\d+) =====$")
RN_RE = re.compile(r"^(\d{3}(?:\.(?:\d+|[a-z]))*)\.\s*(.*)$")

# re-parse txt rule numbers + entry page ranges
txt_numbers = []
txt_pages = {}   # rn -> (page_start, page_end)
page = 0
cur_rn = None
for raw in open(EN_TXT, encoding='utf-8'):
    line = raw.strip()
    pm = PAGE_RE.match(line)
    if pm:
        page = int(pm.group(1))
        continue
    if not line:
        continue
    m = RN_RE.match(line)
    if m:
        cur_rn = m.group(1)
        txt_numbers.append(cur_rn)
        txt_pages[cur_rn] = [page, page]
    elif cur_rn:
        txt_pages[cur_rn][1] = page

db_rows = cur.execute(
    "SELECT evidence_id, rule_number, page, notes FROM evidence "
    "WHERE source_id='source_018' AND rule_number IS NOT NULL ORDER BY evidence_id").fetchall()
db_numbers = [r[1] for r in db_rows]

report = {
    'txt_rule_numbers': len(txt_numbers),
    'db_rule_numbers': len(db_numbers),
    'sequence_identical': txt_numbers == db_numbers,
    'db_duplicates': len(db_numbers) - len(set(db_numbers)),
}

# page coverage + page-start correctness
pages = {r[0] for r in cur.execute("SELECT page FROM evidence WHERE source_id='source_018'")}
report['pages_with_evidence'] = len(pages)
report['missing_pages'] = [p for p in range(1, 121) if p not in pages]
bad_page = [(r[0], r[1], r[2], txt_pages[r[1]][0]) for r in db_rows if txt_pages[r[1]][0] != r[2]]
report['page_start_mismatches'] = bad_page[:10]
missing_span_flag = [r[0] for r in db_rows
                     if txt_pages[r[1]][1] > txt_pages[r[1]][0] and 'spans_pages' not in (r[3] or '')]
report['missing_span_flags'] = missing_span_flag[:10]

# CN vs EN numbers
cn_numbers = [r[0] for r in cur.execute(
    "SELECT rule_number FROM evidence WHERE source_id='source_009' AND rule_number IS NOT NULL ORDER BY evidence_id")]
report['cn_entries'] = len(cn_numbers)
report['en_cn_sequence_identical'] = (cn_numbers == db_numbers)
report['only_in_en'] = sorted(set(db_numbers) - set(cn_numbers))
report['only_in_cn'] = sorted(set(cn_numbers) - set(db_numbers))

# field integrity
report['null_original_text'] = cur.execute(
    "SELECT COUNT(*) FROM evidence WHERE source_id='source_018' AND (original_text IS NULL OR original_text='')").fetchone()[0]
report['null_page'] = cur.execute(
    "SELECT COUNT(*) FROM evidence WHERE source_id='source_018' AND page IS NULL").fetchone()[0]
report['semantic_cols_nonnull'] = cur.execute(
    "SELECT COUNT(*) FROM evidence WHERE source_id='source_018' AND (trigger IS NOT NULL OR precondition IS NOT NULL OR effect IS NOT NULL OR restriction IS NOT NULL OR exception IS NOT NULL OR example IS NOT NULL OR normalized_summary IS NOT NULL)").fetchone()[0]
report['heading_candidates'] = cur.execute(
    "SELECT COUNT(*) FROM evidence WHERE source_id='source_018' AND notes LIKE '%heading_candidate%'").fetchone()[0]
report['clip_flags'] = cur.execute(
    "SELECT COUNT(*) FROM evidence WHERE source_id='source_018' AND notes LIKE '%clip%'").fetchone()[0]
report['top_sections'] = [list(r) for r in cur.execute(
    "SELECT rule_number, original_text FROM evidence WHERE source_id='source_018' AND notes LIKE '%top_section%'")]
report['front_matter'] = list(cur.execute(
    "SELECT evidence_id, page, original_text FROM evidence WHERE source_id='source_018' AND rule_number IS NULL").fetchone() or (None,)*3)

# random spot-check: original_text verbatim against source lines (whitespace-insensitive)
raw = open(EN_TXT, encoding='utf-8').read()
raw_norm = re.sub(r'\s+', '', raw)
random.seed(7)
checks = []
for i in random.sample(range(len(db_numbers)), 8):
    rn = db_numbers[i]
    row = cur.execute(
        "SELECT evidence_id, page, original_text FROM evidence WHERE source_id='source_018' AND rule_number=?",
        (rn,)).fetchone()
    frag = re.sub(r'\s+', '', row[2][:80])
    checks.append({'rule': rn, 'evidence_id': row[0], 'page': row[1],
                   'verbatim_in_source': frag in raw_norm})
report['spot_checks'] = checks

# tasks + sources state
report['tasks_018'] = [list(r) for r in cur.execute(
    "SELECT task_id, page_start, page_end, status FROM processing_tasks WHERE source_id='source_018' ORDER BY task_id")]
report['source_018'] = list(cur.execute(
    "SELECT source_id, source_type, language, date, date_confidence, version, page_count, possible_counterpart FROM sources WHERE source_id='source_018'").fetchone())
report['evidence_totals'] = dict(cur.execute("SELECT source_id, COUNT(*) FROM evidence GROUP BY source_id").fetchall())

con.close()
print(json.dumps(report, ensure_ascii=False, indent=2))
