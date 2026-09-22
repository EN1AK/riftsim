# Stage 4A fix: remove empty topic clusters + manual_review for unmapped rule refs
import sqlite3, json

db = sqlite3.connect(r'workspace/rules_work.db')
c = db.cursor()

# 1) delete rules without any evidence (empty topic pre-creations)
empty = [r[0] for r in c.execute(
    "SELECT rule_id FROM rules WHERE rule_id NOT IN (SELECT DISTINCT rule_id FROM rule_evidence)")]
c.execute("DELETE FROM rules WHERE rule_id NOT IN (SELECT DISTINCT rule_id FROM rule_evidence)")
db.commit()
print('removed empty clusters:', len(empty), empty)

# 2) manual_review entries for explicit rule refs that no longer exist in current core rules
refs = [
    ('EV-CN-FAQ-0011', '376.3'),
    ('EV-CN-FAQ-0031', '322.2'), ('EV-CN-FAQ-0031', '322.3'),
    ('EV-CN-FAQ-0032', '322.2'), ('EV-CN-FAQ-0032', '322.3'), ('EV-CN-FAQ-0032', '322.8'),
    ('EV-CN-FAQ-0055', '735.1'),
    ('EV-CN-FAQ-0198', '460.2'),
    ('EV-CN-FAQ-0216', '335.3'),
]
by_ev = {}
for eid, ref in refs:
    by_ev.setdefault(eid, []).append(ref)

i = 0
for eid, reflist in sorted(by_ev.items()):
    i += 1
    mid = f'MR-4A-{i:04d}'
    # the rule cluster this faq row was actually assigned to
    rid = c.execute(
        "SELECT rule_id FROM rule_evidence WHERE evidence_id=? LIMIT 1", (eid,)).fetchone()[0]
    c.execute(
        "INSERT INTO manual_review (item_id, rule_id, issue_description, source_a, source_b, "
        "conflicting_points, possible_explanation, cannot_auto_resolve_reason) VALUES (?,?,?,?,?,?,?,?)",
        (mid, rid,
         f"FAQ {eid} explicitly references core rule number(s) {', '.join(reflist)} which do not exist in the current 2026-07 core rules (clustering could not attach the ref)",
         eid, 'source_009/source_018 core rules (2026-07)',
         'referenced rule number absent from current rule-number space',
         'rule numbering changed since the FAQ was written (older rule version), or the ref is shorthand/typo; '
         'known precedent: FAQ 735.1.c was incorporated into 2026-07 rules as 809.1.c (MR-2D-0007)',
         'requires Stage 4B reconciliation: map stale ref to its successor rule or record as historical reference'))
db.commit()
print('manual_review MR-4A entries added:', i)

# 3) re-validation
checks = {
    'evidence_total': c.execute("SELECT COUNT(*) FROM evidence").fetchone()[0],
    'evidence_mapped': c.execute("SELECT COUNT(DISTINCT evidence_id) FROM rule_evidence").fetchone()[0],
    'unmapped': [r[0] for r in c.execute(
        "SELECT evidence_id FROM evidence WHERE evidence_id NOT IN (SELECT DISTINCT evidence_id FROM rule_evidence)")],
    'rules_total': c.execute("SELECT COUNT(*) FROM rules").fetchone()[0],
    'rule_evidence_links': c.execute("SELECT COUNT(*) FROM rule_evidence").fetchone()[0],
    'rules_without_evidence': [r[0] for r in c.execute(
        "SELECT rule_id FROM rules WHERE rule_id NOT IN (SELECT DISTINCT rule_id FROM rule_evidence)")],
    'duplicate_links': c.execute(
        "SELECT COUNT(*) FROM (SELECT rule_id, evidence_id FROM rule_evidence GROUP BY 1,2 HAVING COUNT(*)>1)").fetchone()[0],
}
print(json.dumps(checks, ensure_ascii=False, indent=2))

# 4) distribution snapshot
print('--- rules by prefix ---')
for row in c.execute(
    "SELECT CASE WHEN rule_id LIKE 'R-CR-%' THEN 'R-CR' WHEN rule_id LIKE 'R-CARD-%' THEN 'R-CARD' "
    "WHEN rule_id LIKE 'R-TOPIC-CN%' THEN 'R-TOPIC-CN' WHEN rule_id LIKE 'R-TOPIC-EN%' THEN 'R-TOPIC-EN' "
    "WHEN rule_id LIKE 'R-MISC%' THEN 'R-MISC' ELSE 'R-FRONT' END p, COUNT(*) FROM rules GROUP BY p"):
    print(row)
print('--- links by relationship ---')
for row in c.execute("SELECT relationship, COUNT(*) FROM rule_evidence GROUP BY 1 ORDER BY 2 DESC"):
    print(row)
