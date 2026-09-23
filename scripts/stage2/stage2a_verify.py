# -*- coding: utf-8 -*-
"""Stage 2A verification: completeness of CN Core Rules evidence."""
import sqlite3, re, json, random

con = sqlite3.connect('workspace/rules_work.db')
cur = con.cursor()

rule_re = re.compile(r'^(\d{3}(?:\.[A-Za-z0-9]+)*\.)\s*(.*)$')
txt_numbers = []
with open('extracted/loltcg_pdfs__09_2026-07-23_6f47b6ebe57341a5bb5f4bed5548d051.txt', encoding='utf-8') as f:
    for line in f:
        m = rule_re.match(line.strip())
        if m:
            txt_numbers.append(m.group(1)[:-1])

db_numbers = [r[0] for r in cur.execute(
    "SELECT rule_number FROM evidence WHERE source_id='source_009' AND rule_number IS NOT NULL ORDER BY evidence_id")]

report = {
    'txt_rule_numbers': len(txt_numbers),
    'db_rule_numbers': len(db_numbers),
    'sequence_identical': txt_numbers == db_numbers,
    'db_duplicates': len(db_numbers) - len(set(db_numbers)),
}

pages = {r[0] for r in cur.execute("SELECT page FROM evidence WHERE source_id='source_009'")}
report['pages_with_evidence'] = len(pages)
report['missing_pages'] = [p for p in range(1, 126) if p not in pages]

report['tasks_009'] = [list(r) for r in cur.execute(
    "SELECT task_id, page_start, page_end, status FROM processing_tasks WHERE source_id='source_009' ORDER BY task_id")]
report['source_009'] = list(cur.execute(
    "SELECT source_id, source_type, language, date, date_confidence, page_count, possible_counterpart FROM sources WHERE source_id='source_009'").fetchone())
report['total_sources'] = cur.execute('SELECT COUNT(*) FROM sources').fetchone()[0]
report['total_tasks'] = cur.execute('SELECT COUNT(*) FROM processing_tasks').fetchone()[0]
report['evidence_009'] = cur.execute("SELECT COUNT(*) FROM evidence WHERE source_id='source_009'").fetchone()[0]
report['null_original_text'] = cur.execute(
    "SELECT COUNT(*) FROM evidence WHERE source_id='source_009' AND (original_text IS NULL OR original_text='')").fetchone()[0]
report['null_page'] = cur.execute(
    "SELECT COUNT(*) FROM evidence WHERE source_id='source_009' AND page IS NULL").fetchone()[0]
report['heading_candidates'] = cur.execute(
    "SELECT COUNT(*) FROM evidence WHERE source_id='source_009' AND notes LIKE '%heading_candidate%'").fetchone()[0]
report['top_sections'] = [list(r) for r in cur.execute(
    "SELECT rule_number, original_text FROM evidence WHERE source_id='source_009' AND notes LIKE '%top_section%'")]

# random spot-check: original_text verbatim against source lines
random.seed(42)
sample_ids = random.sample(range(len(db_numbers)), 5)
checks = []
with open('extracted/loltcg_pdfs__09_2026-07-23_6f47b6ebe57341a5bb5f4bed5548d051.txt', encoding='utf-8') as f:
    raw = f.read().replace('\n', '')
for i in sample_ids:
    rn = db_numbers[i]
    row = cur.execute(
        "SELECT evidence_id, page, original_text FROM evidence WHERE source_id='source_009' AND rule_number=?", (rn,)).fetchone()
    txt_frag = row[2][:60].replace(' ', '')
    raw_norm = raw.replace(' ', '')
    checks.append({'rule': rn, 'evidence_id': row[0], 'page': row[1],
                   'text_head': row[2][:30], 'verbatim_in_source': txt_frag in raw_norm})
report['spot_checks'] = checks

con.close()
print(json.dumps(report, ensure_ascii=False, indent=2))
