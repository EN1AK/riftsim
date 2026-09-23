import sqlite3, json

db = sqlite3.connect(r'workspace/rules_work.db')
c = db.cursor()

print('=== FAQ w/ rule_number-like references in original_text ===')
import re
pat = re.compile(r'\b\d{3}(?:\.\d+[a-z]?)*\b')
rows = c.execute("SELECT evidence_id, source_language, faq_question, faq_answer, card_ids, related_cards FROM evidence WHERE source_type IN ('faq','official_explanation')").fetchall()
print('total faq/oe rows:', len(rows))
import sys
io = sys.stdout
ref_count = 0
card_count = 0
both = 0
neither_rows = []
for eid, lang, q, a, cids, rcards in rows:
    text = (q or '') + ' ' + (a or '')
    # rule number like 735.1.c / 809.1
    refs = re.findall(r'(?<![\d.])\d{3}(?:\.\d+[a-z]?)+(?![\d.])', text)
    has_cards = bool(cids and cids not in ('[]', 'null'))
    if refs:
        ref_count += 1
    if has_cards:
        card_count += 1
    if refs and has_cards:
        both += 1
    if not refs and not has_cards:
        neither_rows.append(eid)
print('with rule refs:', ref_count)
print('with cards:', card_count)
print('both:', both)
print('neither:', len(neither_rows))
print('neither sample:', neither_rows[:20])

print()
print('=== card_ids coverage errata ===')
rows = c.execute("SELECT evidence_id, card_ids FROM evidence WHERE source_type='errata'").fetchall()
nocard = [e for e, cids in rows if not cids or cids in ('[]','null')]
print('errata rows:', len(rows), 'no card_ids:', len(nocard), nocard[:10])

print()
print('=== distinct cards in errata ===')
cards = set()
for e, cids in rows:
    if cids and cids not in ('[]','null'):
        for k in json.loads(cids):
            cards.add(k)
print('distinct errata cards:', len(cards))

print()
print('=== distinct cards in faq/oe ===')
fcards = set()
norule_nocard_text = 0
rows2 = c.execute("SELECT evidence_id, card_ids FROM evidence WHERE source_type IN ('faq','official_explanation')").fetchall()
for e, cids in rows2:
    if cids and cids not in ('[]','null'):
        for k in json.loads(cids):
            fcards.add(k)
print('distinct faq cards:', len(fcards), '| overlap with errata cards:', len(fcards & cards))

print()
print('=== rule_number format check core rules ===')
import collections
samples = c.execute("SELECT rule_number FROM evidence WHERE source_type='rule' AND source_language='zh' AND rule_number IS NOT NULL ORDER BY evidence_id LIMIT 10").fetchall()
print([s[0] for s in samples])
last = c.execute("SELECT rule_number FROM evidence WHERE source_type='rule' AND source_language='zh' AND rule_number IS NOT NULL ORDER BY evidence_id DESC LIMIT 5").fetchall()
print([s[0] for s in last])
# any NULL rule_number among rule evidence?
nullcnt = c.execute("SELECT COUNT(*) FROM evidence WHERE source_type='rule' AND rule_number IS NULL").fetchone()[0]
print('rule rows w/ NULL rule_number:', nullcnt)
