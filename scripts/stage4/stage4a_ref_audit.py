import sqlite3, json

db = sqlite3.connect(r'workspace/rules_work.db')
c = db.cursor()

rows = c.execute(
    "SELECT re.evidence_id, re.rule_id, e.source_id, e.source_language, substr(e.faq_question,1,60) "
    "FROM rule_evidence re JOIN evidence e ON e.evidence_id = re.evidence_id "
    "WHERE re.notes LIKE '%explicit rule-number reference%' ORDER BY re.evidence_id").fetchall()
print('explicit-ref links:', len(rows))
for r in rows:
    print(r)

# for each linked rule target, show its zh text head
print()
print('--- targets content ---')
targets = sorted({r[1] for r in rows})
for t in targets:
    txt = c.execute(
        "SELECT substr(original_text,1,110) FROM evidence WHERE evidence_id=("
        "SELECT evidence_id FROM rule_evidence WHERE rule_id=? AND relationship='same' AND notes LIKE '%zh canonical%')",
        (t,)).fetchone()
    print(t, '=>', txt[0] if txt else '(none)')
