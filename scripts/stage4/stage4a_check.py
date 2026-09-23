"""Stage 4A design validation: gather remaining facts in one small-output run."""
import sqlite3, json, collections

DB = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db'
db = sqlite3.connect(DB)
cur = db.cursor()

cn = set(r[0] for r in cur.execute("SELECT rule_number FROM evidence WHERE evidence_id LIKE 'EV-CN-CR%' AND rule_number IS NOT NULL"))
en = set(r[0] for r in cur.execute("SELECT rule_number FROM evidence WHERE evidence_id LIKE 'EV-EN-CR%' AND rule_number IS NOT NULL"))
print('CN rule_numbers:', len(cn), 'EN:', len(en), 'identical:', cn == en)
if cn != en:
    print('cn-only:', sorted(cn - en)[:10]); print('en-only:', sorted(en - cn)[:10])

print('\n=== ER topics / card_ids emptiness / front matter ===')
print(list(cur.execute("SELECT DISTINCT topic FROM evidence WHERE evidence_id LIKE 'EV-CN-ER%' OR evidence_id LIKE 'EV-EN-ER%'")))
print('ER card_ids empty:', cur.execute("SELECT COUNT(*) FROM evidence WHERE (evidence_id LIKE 'EV-CN-ER%' OR evidence_id LIKE 'EV-EN-ER%') AND (card_ids IS NULL OR card_ids IN ('','[]'))").fetchone()[0])
print('ER front_matter-ish rows:', list(cur.execute("SELECT evidence_id, topic, card_ids, substr(original_text,1,50) FROM evidence WHERE (evidence_id LIKE 'EV-CN-ER%' OR evidence_id LIKE 'EV-EN-ER%') AND topic != 'card_errata'")))

print('\n=== special FAQ notes ===')
for eid in ['EV-CN-FAQ-0055', 'EV-CN-FAQ-0089', 'EV-CN-FAQ-0090', 'EV-CN-FAQ-0307', 'EV-CN-FAQ-0308']:
    row = cur.execute('SELECT evidence_id, rule_id_candidate, notes FROM evidence WHERE evidence_id=?', (eid,)).fetchone()
    print(row)

print('\n=== FAQ ref+cards overlap ===')
print(cur.execute("""SELECT COUNT(*) FROM evidence WHERE (evidence_id LIKE 'EV-CN-FAQ%' OR evidence_id LIKE 'EV-EN-OE%')
    AND rule_id_candidate IS NOT NULL AND rule_id_candidate != ''
    AND card_ids IS NOT NULL AND card_ids NOT IN ('','[]')""").fetchone()[0])

print('\n=== manual_review MR-3-CR sample ===')
for row in cur.execute("SELECT * FROM manual_review WHERE item_id LIKE 'MR-3-CR%' LIMIT 2"):
    print(row)
print('MR-3-CR rule_id populated:', cur.execute("SELECT COUNT(*) FROM manual_review WHERE item_id LIKE 'MR-3-CR%' AND rule_id IS NOT NULL AND rule_id != ''").fetchone()[0])
print('MR other prefixes:', list(cur.execute("SELECT DISTINCT substr(item_id,1,8) p, COUNT(*) FROM manual_review GROUP BY p")))

print('\n=== FAQ 32 rule-ref resolution ===')
def ancestors(rn):
    parts = rn.split('.')
    for i in range(len(parts) - 1, 0, -1):
        yield '.'.join(parts[:i])
unres = []
for eid, ref in cur.execute("""SELECT evidence_id, rule_id_candidate FROM evidence
    WHERE (evidence_id LIKE 'EV-CN-FAQ%' OR evidence_id LIKE 'EV-EN-OE%')
      AND rule_id_candidate IS NOT NULL AND rule_id_candidate != ''"""):
    if ref in cn:
        kind = 'exact'; tgt = ref
    else:
        tgt = next((a for a in ancestors(ref) if a in cn), None)
        kind = 'ancestor' if tgt else 'UNRESOLVED'
    print(eid, ref, '->', tgt, kind)
    if not tgt: unres.append((eid, ref))
print('unresolved:', unres)

print('\n=== cards_bilingual.db schema ===')
cdb = sqlite3.connect(r'c:\Users\Mortis\Desktop\Workspace\riftsim\cards_bilingual.db')
ccur = cdb.cursor()
print([r for r in ccur.execute("SELECT name FROM sqlite_master WHERE type='table'")])
for row in ccur.execute('PRAGMA table_info(cards)'):
    print(row)
print(ccur.execute("SELECT * FROM cards LIMIT 1").fetchone())
cdb.close()
db.close()
