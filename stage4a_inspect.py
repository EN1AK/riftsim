import sqlite3

db = sqlite3.connect(r'workspace/rules_work.db')
c = db.cursor()

tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
for name in tables:
    print('=== TABLE', name)
    for row in c.execute(f'PRAGMA table_info({name})'):
        print('   ', row[1], row[2])

print()
print('=== evidence by source_type ===')
for row in c.execute("SELECT source_type, COUNT(*) FROM evidence GROUP BY source_type"):
    print(row)

print()
print('=== evidence rule_id_candidate sample ===')
for row in c.execute("SELECT evidence_id, rule_id_candidate, rule_number FROM evidence WHERE source_type='rule' LIMIT 5"):
    print(row)

print()
print('=== evidence faq sample ===')
for row in c.execute("SELECT evidence_id, rule_id_candidate, faq_classification FROM evidence WHERE source_type IN ('faq','official_explanation') LIMIT 5"):
    print(row)

print()
print('=== errata sample ===')
for row in c.execute("SELECT evidence_id, target_rule_candidate, card_ids FROM evidence WHERE source_type='errata' LIMIT 5"):
    print(row)

print()
print('=== alignments sample ===')
for row in c.execute("SELECT * FROM alignments LIMIT 3"):
    print(row)
