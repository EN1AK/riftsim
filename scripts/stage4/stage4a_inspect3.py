import sqlite3, json, re, collections

db = sqlite3.connect(r'workspace/rules_work.db')
c = db.cursor()

print('=== 3 errata rows w/o card_ids ===')
for row in c.execute("SELECT evidence_id, source_id, heading, substr(original_text,1,120) FROM evidence WHERE source_type='errata' AND (card_ids IS NULL OR card_ids IN ('[]','null'))"):
    print(row)

print()
print('=== FAQ topic distribution ===')
for row in c.execute("SELECT topic, COUNT(*) FROM evidence WHERE source_type IN ('faq','official_explanation') GROUP BY topic ORDER BY 2 DESC LIMIT 20"):
    print(row)

print()
print('=== FAQ heading/section sample (rows w/o refs/cards) ===')
for row in c.execute("SELECT evidence_id, source_id, section, heading, topic FROM evidence WHERE source_type IN ('faq','official_explanation') AND (card_ids IS NULL OR card_ids IN ('[]','null')) LIMIT 15"):
    print(row)

print()
print('=== rule_change_candidate with rule-number refs ===')
rows = c.execute("SELECT evidence_id, source_id, faq_question, faq_answer FROM evidence WHERE faq_classification='rule_change_candidate'").fetchall()
print('total rule_change_candidate:', len(rows))
withref = 0
for eid, sid, q, a in rows:
    text = (q or '') + ' ' + (a or '')
    refs = re.findall(r'(?<![\d.])\d{3}(?:\.\d+[a-z]?)*', text)
    if refs:
        withref += 1
        if withref <= 8:
            print(' ', eid, sid, 'refs=', refs[:5])
print('with refs:', withref)

print()
print('=== core rule heading pattern sample ===')
for row in c.execute("SELECT rule_number, heading, section FROM evidence WHERE source_type='rule' AND source_language='en' AND rule_number IN ('100','200','300','400','500','600','700','800','900')"):
    print(row)

print()
print('=== source_012 (patch notes) sample rows ===')
for row in c.execute("SELECT evidence_id, heading, substr(faq_question,1,80), substr(faq_answer,1,150) FROM evidence WHERE source_id='source_012' LIMIT 6"):
    print(row)
