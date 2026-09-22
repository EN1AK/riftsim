"""Stage 4B batch 4B-B005 - dump adjudication inputs for VERIF-FLAG R-CR + MR-4A."""
import json
import sqlite3

DB = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db'
OUT = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\checkpoints\stage4b_b005_dump.json'

db = sqlite3.connect(DB)
c = db.cursor()

rules = [r[0] for r in c.execute(
    "SELECT rule_id FROM rules WHERE status='pending_reconciliation' AND rule_id LIKE 'R-CR-%' ORDER BY rule_id")]
extra = ['R-CR-438.7']  # already reconciled (B003) but keeps VERIF-FLAG pointer

out = {'pending_rcr': rules, 'rules': {}, 'mr4a': {}, 'successor_texts': {}}

for rid in rules + extra:
    entry = {'status': c.execute('SELECT status FROM rules WHERE rule_id=?', (rid,)).fetchone()[0],
             'links': []}
    for rel, evid, src, q, a in c.execute(
            "SELECT re.relationship, e.evidence_id, e.source_id, e.faq_question, e.faq_answer "
            "FROM rule_evidence re JOIN evidence e ON e.evidence_id=re.evidence_id "
            "WHERE re.rule_id=? AND re.relationship LIKE 'faq:%' ORDER BY e.evidence_id", (rid,)):
        entry['links'].append({'rel': rel, 'ev': evid, 'src': src, 'q': q, 'a': a})
    same = c.execute(
        "SELECT e.source_language, e.original_text FROM rule_evidence re JOIN evidence e ON e.evidence_id=re.evidence_id "
        "WHERE re.rule_id=? AND re.relationship='same'", (rid,)).fetchall()
    entry['zh'] = next((t for l, t in same if l == 'zh'), None)
    entry['en'] = next((t for l, t in same if l == 'en'), None)
    out['rules'][rid] = entry

# MR-4A items + their FAQ evidence
for item_id, rule_id, src_a, expl in c.execute(
        "SELECT item_id, rule_id, source_a, possible_explanation FROM manual_review WHERE item_id LIKE 'MR-4A-%' ORDER BY item_id").fetchall():
    ev = src_a.strip()
    row = c.execute("SELECT faq_question, faq_answer FROM evidence WHERE evidence_id=?", (ev,)).fetchone()
    out['mr4a'][item_id] = {'rule_id': rule_id, 'evidence': ev,
                            'q': row[0] if row else None, 'a': row[1] if row else None,
                            'adjudication': expl}

# successor rule texts
succ = ['R-CR-383.3.d.1', 'R-CR-318.1', 'R-CR-324.1', 'R-CR-466.1.a', 'R-CR-809.1.c',
        'R-CR-465.2.c.4', 'R-CR-465.2.c.4.a', 'R-CR-334.1', 'R-CR-383.4.f']
for rid in succ:
    row = c.execute(
        "SELECT e.original_text FROM rule_evidence re JOIN evidence e ON e.evidence_id=re.evidence_id "
        "WHERE re.rule_id=? AND re.relationship='same' AND e.source_language='zh'", (rid,)).fetchone()
    out['successor_texts'][rid] = row[0] if row else None

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('rules:', len(rules), '+ 438.7; mr4a:', len(out['mr4a']))
print('bytes:', len(json.dumps(out, ensure_ascii=False)))
