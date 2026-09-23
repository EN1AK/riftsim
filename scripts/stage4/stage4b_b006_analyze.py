"""4B-B006 analysis: MR-2D-0005/0010 + compact RCC summary + sample entries (no full dump)."""
import sqlite3, json, collections

DB = "workspace/rules_work.db"
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
c = con.cursor()
out = {}

# manual_review schema check first
c.execute("PRAGMA table_info(manual_review)")
out["mr_schema"] = [r["name"] for r in c.fetchall()]
mr_pk = out["mr_schema"][0]

# MR rows
c.execute(f"SELECT * FROM manual_review WHERE {mr_pk} IN ('MR-2D-0005','MR-2D-0010')")
out["mr"] = [dict(r) for r in c.fetchall()]

# R-MISC rules and their content
c.execute("SELECT rule_id, topic FROM rules WHERE rule_id LIKE 'R-MISC%' OR rule_id IN ('R-ER-FRONT','R-FAQ-FRONT')")
out["misc_front_rules"] = [dict(r) for r in c.fetchall()]

# R-TOPIC examples
c.execute("SELECT rule_id, topic FROM rules WHERE status='pending_reconciliation' AND rule_id LIKE 'R-TOPIC%' ORDER BY rule_id LIMIT 8")
out["topic_samples"] = [dict(r) for r in c.fetchall()]

# RCC by source x rule bucket matrix
c.execute("""
SELECT e.source_id, r.rule_id FROM rule_evidence re
JOIN evidence e ON e.evidence_id=re.evidence_id JOIN rules r ON r.rule_id=re.rule_id
WHERE re.relationship='faq:rule_change_candidate' AND r.status='pending_reconciliation'
""")
m = collections.Counter()
for r in c.fetchall():
    rid = r["rule_id"]
    b = rid if (rid.startswith("R-MISC") or "FRONT" in rid) else ("R-TOPIC-CN" if "-CN" in rid else "R-TOPIC-EN")
    m[f'{r["source_id"]}|{b}'] += 1
out["rcc_matrix"] = dict(sorted(m.items()))

# source_019 RCC full text (31 items to APPLY) - need question+answer complete
c.execute("""
SELECT re.rule_id, re.evidence_id, e.section, e.faq_question, e.faq_answer
FROM rule_evidence re JOIN evidence e ON e.evidence_id=re.evidence_id
WHERE re.relationship='faq:rule_change_candidate' AND e.source_id='source_019'
ORDER BY re.evidence_id
""")
c019 = [dict(r) for r in c.fetchall()]
out["rcc_019"] = c019

# count check: how big are the 019 texts
out["rcc_019_sizes"] = [len((r["faq_question"] or "")) + len((r["faq_answer"] or "")) for r in c019]

# source_012/014/016 + 005 RCC: truncated preview (incorporated-check)
c.execute("""
SELECT re.rule_id, re.evidence_id, e.source_id, e.section,
       substr(COALESCE(e.faq_question, e.original_text,''),1,200) q,
       substr(COALESCE(e.faq_answer,''),1,200) a
FROM rule_evidence re JOIN evidence e ON e.evidence_id=re.evidence_id
WHERE re.relationship='faq:rule_change_candidate' AND e.source_id IN ('source_005','source_012','source_014','source_016')
  AND re.rule_id IN (SELECT rule_id FROM rules WHERE status='pending_reconciliation')
ORDER BY e.source_id, re.evidence_id
""")
out["rcc_precore_preview"] = [dict(r) for r in c.fetchall()]

with open("workspace/checkpoints/stage4b_b006_analysis.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print("mr schema:", out["mr_schema"])
print("mr rows:", len(out["mr"]))
for r in out["mr"]:
    print(json.dumps(r, ensure_ascii=False)[:400])
print("misc/front:", [(r["rule_id"], str(r["topic"])[:60]) for r in out["misc_front_rules"]])
print("topic samples:", out["topic_samples"])
print("rcc matrix:", out["rcc_matrix"])
print("019 count:", len(c019), "sizes:", out["rcc_019_sizes"])
