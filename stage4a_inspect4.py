import sqlite3, json, collections

db = sqlite3.connect(r'workspace/rules_work.db')
c = db.cursor()

print('=== FAQ topic=None rows by source/lang ===')
for row in c.execute("SELECT source_id, source_language, COUNT(*) FROM evidence WHERE source_type IN ('faq','official_explanation') AND topic IS NULL GROUP BY 1,2"):
    print(row)

print()
print('=== FAQ distinct topics by lang (counts) ===')
for lang in ('zh','en'):
    n = c.execute("SELECT COUNT(DISTINCT topic) FROM evidence WHERE source_type IN ('faq','official_explanation') AND source_language=? AND topic IS NOT NULL", (lang,)).fetchone()[0]
    print(lang, 'distinct topics:', n)

print()
print('=== AL-CR coverage check ===')
zh_rules = [r[0] for r in c.execute("SELECT evidence_id FROM evidence WHERE evidence_id LIKE 'EV-CN-CR-%'")]
en_rules = [r[0] for r in c.execute("SELECT evidence_id FROM evidence WHERE evidence_id LIKE 'EV-EN-CR-%'")]
pairs = {r[0]: (r[1], r[2], r[3]) for r in c.execute("SELECT alignment_id, evidence_a, evidence_b, relation FROM alignments WHERE alignment_id LIKE 'AL-CR-%'")}
a_set = {v[0] for v in pairs.values()}
b_set = {v[1] for v in pairs.values()}
print('zh rules:', len(zh_rules), 'covered as evidence_a:', len(a_set & set(zh_rules)))
print('en rules:', len(en_rules), 'covered as evidence_b:', len(b_set & set(en_rules)))

print()
print('=== AL-ER coverage check ===')
er = {r[0] for r in c.execute("SELECT evidence_id FROM evidence WHERE source_type='errata'")}
er_pairs = list(c.execute("SELECT evidence_a, evidence_b FROM alignments WHERE alignment_id LIKE 'AL-ER-%'"))
er_in_a = {p[0] for p in er_pairs} | {p[1] for p in er_pairs}
print('errata rows:', len(er), 'in AL-ER pairs:', len(er & er_in_a))

print()
print('=== rule_number uniqueness per lang ===')
dup = c.execute("SELECT rule_number, COUNT(*) FROM evidence WHERE source_type='rule' AND source_language='zh' AND rule_number IS NOT NULL GROUP BY 1 HAVING COUNT(*)>1").fetchall()
print('zh dup rule_number:', len(dup), dup[:5])
dup = c.execute("SELECT rule_number, COUNT(*) FROM evidence WHERE source_type='rule' AND source_language='en' AND rule_number IS NOT NULL GROUP BY 1 HAVING COUNT(*)>1").fetchall()
print('en dup rule_number:', len(dup), dup[:5])

print()
print('=== FAQ rows w/ card_ids AND topic: would topic double-assign? ===')
n = c.execute("SELECT COUNT(*) FROM evidence WHERE source_type IN ('faq','official_explanation') AND topic IS NOT NULL AND topic != 'front_matter' AND card_ids IS NOT NULL AND card_ids NOT IN ('[]','null')").fetchone()[0]
print('cards+topic rows:', n)

print()
print('=== en topics sample (for slugging) ===')
for row in c.execute("SELECT DISTINCT topic FROM evidence WHERE source_language='en' AND source_type IN ('official_explanation','faq') AND topic IS NOT NULL LIMIT 15"):
    print(row)

print()
print('=== zh topics sample ===')
for row in c.execute("SELECT DISTINCT topic FROM evidence WHERE source_language='zh' AND source_type='faq' AND topic IS NOT NULL LIMIT 15"):
    print(row)

print()
print('=== rule 735.1.c check (the FAQ-revised rule) ===')
for row in c.execute("SELECT evidence_id, source_language, rule_number FROM evidence WHERE rule_number LIKE '735.1%' AND source_type='rule'"):
    print(row)
print('--- 809.1 rows')
for row in c.execute("SELECT evidence_id, source_language, rule_number FROM evidence WHERE rule_number LIKE '809.1%' AND source_type='rule'"):
    print(row)
