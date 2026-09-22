import sqlite3

db = sqlite3.connect(r'workspace/rules_work.db')
c = db.cursor()

faq_ids = ['EV-CN-FAQ-0011', 'EV-CN-FAQ-0031', 'EV-CN-FAQ-0032',
           'EV-CN-FAQ-0055', 'EV-CN-FAQ-0198', 'EV-CN-FAQ-0216']
stale = {'EV-CN-FAQ-0011': '376.3', 'EV-CN-FAQ-0031': '322.2,322.3',
         'EV-CN-FAQ-0032': '322.2,322.3,322.8', 'EV-CN-FAQ-0055': '735.1',
         'EV-CN-FAQ-0198': '460.2', 'EV-CN-FAQ-0216': '335.3'}

for eid in faq_ids:
    r = c.execute("SELECT source_id, topic, faq_question, faq_answer FROM evidence WHERE evidence_id=?", (eid,)).fetchone()
    print('=' * 70)
    print(eid, '|', r[0], '| topic:', r[1], '| stale ref:', stale[eid])
    print('Q:', (r[2] or '')[:400])
    print('A:', (r[3] or '')[:500])
    print()

# show current rule neighborhoods: what 322.x / 335.x / 376.x / 460.x / 735.x / 809.1 look like now
print('#' * 70)
print('CURRENT RULE NEIGHBORHOODS (zh text)')
for prefix in ('322.%', '335.%', '376.%', '460.%', '809.1%'):
    print('-' * 60, prefix)
    rows = c.execute(
        "SELECT rule_number, substr(original_text,1,160) FROM evidence "
        "WHERE source_type='rule' AND source_language='zh' AND rule_number LIKE ? ORDER BY rule_number LIMIT 12", (prefix,)).fetchall()
    for rn, txt in rows:
        print(f'  {rn}: {txt}')
