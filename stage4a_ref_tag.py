# Tag explicit-ref links from pre-renumbering judge-FAQ sources for 4B verification.
import sqlite3

db = sqlite3.connect(r'workspace/rules_work.db')
c = db.cursor()

OLD = ('source_001', 'source_005', 'source_006', 'source_007', 'source_008')
ph = ','.join('?' * len(OLD))
n = c.execute(
    f"UPDATE rule_evidence SET notes = notes || ' | VERIFICATION FLAG 4B: citing source predates 2026-07 "
    f"core-rules renumbering; matched number may denote a different rule (confirmed-stale cases: MR-4A-0001..0006)' "
    f"WHERE notes LIKE '%explicit rule-number reference%' AND evidence_id IN "
    f"(SELECT evidence_id FROM evidence WHERE source_id IN ({ph}))", OLD).rowcount
db.commit()
print('tagged links:', n)

# sanity: count by source
for row in c.execute(
    "SELECT e.source_id, COUNT(*) FROM rule_evidence re JOIN evidence e ON e.evidence_id=re.evidence_id "
    "WHERE re.notes LIKE '%VERIFICATION FLAG 4B%' GROUP BY 1"):
    print(row)
