# -*- coding: utf-8 -*-
import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
db = sqlite3.connect('workspace/final/rules.db')

def full(rid, cap=2000):
    r = db.execute("SELECT rule_id, topic, proposed_canonical_rule, official_interpretation, exception FROM rules WHERE rule_id=?", (rid,)).fetchone()
    if not r:
        return
    print('==== %s | %s ====' % (rid, (r[1] or '')[:70]))
    print(' can:', (r[2] or '(null)')[:cap])
    if r[3]:
        print(' oi :', r[3][:cap])
    if r[4]:
        print(' exc:', r[4][:300])
    print()

full('R-CARD-VEN-152', 3000)

print('== VEN-152 来源 ==')
for s in db.execute("SELECT relationship, evidence_id FROM rule_sources WHERE rule_id='R-CARD-VEN-152'"):
    print(' ', s)
print()

def dump(pred, cap=600):
    for rid, topic, can in db.execute("SELECT rule_id, topic, proposed_canonical_rule FROM rules WHERE %s ORDER BY rule_id" % pred):
        print('==== %s | %s ====' % (rid, (topic or '')[:55]))
        print((can or '(null)')[:cap]); print()

print('== 356 必选额外费用 ==')
dump("rule_id LIKE 'R-CR-356%'")
print('== 750-755 Making New Choices ==')
dump("rule_id LIKE 'R-CR-750%' OR rule_id LIKE 'R-CR-751%' OR rule_id LIKE 'R-CR-752%' OR rule_id LIKE 'R-CR-753%' OR rule_id LIKE 'R-CR-754%' OR rule_id LIKE 'R-CR-755%'")
