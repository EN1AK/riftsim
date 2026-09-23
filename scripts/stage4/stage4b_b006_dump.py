"""Stage 4B-B006 probe: dump pending rules + unresolved RCC links + evidence context.

Read-only. Writes workspace/checkpoints/stage4b_b006_probe.json for inspection.
"""
import json
import sqlite3
from collections import defaultdict

DB = "workspace/rules_work.db"
OUT = "workspace/checkpoints/stage4b_b006_probe.json"

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()

probe = {}

# 1. pending rules by bucket
cur.execute("""
SELECT CASE
  WHEN rule_id LIKE 'R-TOPIC-CN%' THEN 'R-TOPIC-CN'
  WHEN rule_id LIKE 'R-TOPIC-EN%' THEN 'R-TOPIC-EN'
  WHEN rule_id LIKE 'R-CARD%' THEN 'R-CARD'
  WHEN rule_id LIKE 'R-MISC%' THEN 'R-MISC'
  ELSE rule_id END AS bucket, COUNT(*) n
FROM rules WHERE status='pending_reconciliation' GROUP BY bucket
""")
probe["pending_buckets"] = {r["bucket"]: r["n"] for r in cur.fetchall()}

# 2. RCC links overall: which are already adjudicated (B004/B005 left notes?) vs pending.
#    Identification: relationship='faq:rule_change_candidate'. Resolved ones got notes updated.
cur.execute("""
SELECT re.rule_id, re.evidence_id, re.notes, e.source_id
FROM rule_evidence re JOIN evidence e ON e.evidence_id = re.evidence_id
WHERE re.relationship='faq:rule_change_candidate'
""")
rows = cur.fetchall()
probe["rcc_total"] = len(rows)
by_source = defaultdict(lambda: {"total": 0, "resolved_markers": 0, "pending": 0, "pending_items": []})
resolved_cnt = 0
pending_items = []
for r in rows:
    src = r["source_id"]
    by_source[src]["total"] += 1
    notes = r["notes"] or ""
    if notes:  # any annotation = treated previously
        by_source[src]["resolved_markers"] += 1
        resolved_cnt += 1
    else:
        by_source[src]["pending"] += 1
        pending_items.append({"rule_id": r["rule_id"], "evidence_id": r["evidence_id"], "source_id": src})
probe["rcc_by_source"] = {k: {kk: vv for kk, vv in v.items() if kk != "pending_items"} for k, v in by_source.items()}
probe["rcc_pending_count"] = len(pending_items)
probe["rcc_pending_by_rule_bucket"] = defaultdict(int)
bmap = defaultdict(int)
for it in pending_items:
    rid = it["rule_id"]
    if rid.startswith("R-TOPIC-CN"):
        b = "R-TOPIC-CN"
    elif rid.startswith("R-TOPIC-EN"):
        b = "R-TOPIC-EN"
    elif rid.startswith("R-CARD"):
        b = "R-CARD"
    elif rid.startswith("R-MISC"):
        b = "R-MISC"
    elif rid.startswith("R-CR"):
        b = "R-CR"
    else:
        b = rid
    bmap[b] += 1
probe["rcc_pending_by_rule_bucket"] = dict(bmap)

# 3. pending items detail
probe["pending_items"] = pending_items

# 4. For each pending rule: full rule row + all rule_evidence links w/ evidence summary
cur.execute("SELECT * FROM rules WHERE status='pending_reconciliation'")
pending_rules = [dict(r) for r in cur.fetchall()]
probe["pending_rule_ids"] = [r["rule_id"] for r in pending_rules]

rule_links = {}
for r in pending_rules:
    rid = r["rule_id"]
    cur.execute("""
    SELECT re.relationship, re.confidence, re.notes, e.evidence_id, e.source_id, e.source_type,
           e.topic, e.rule_id_candidate, e.target_rule_candidate, e.faq_classification,
           e.faq_question, e.faq_answer,
           substr(coalesce(e.original_text,''),1,400) AS original_head,
           e.original_text AS original_full,
           e.corrected_fragment
    FROM rule_evidence re JOIN evidence e ON e.evidence_id = re.evidence_id
    WHERE re.rule_id=? ORDER BY re.relationship, e.evidence_id
    """, (rid,))
    rule_links[rid] = [dict(x) for x in cur.fetchall()]
probe["pending_rules"] = [{"rule_row": {k: v for k, v in r.items() if k in
    ("rule_id", "topic", "proposed_canonical_rule", "status", "needs_verification")},
    "links": rule_links[r["rule_id"]]} for r in pending_rules]

# 5. R-CARD pending RCC items: those rules already reconciled; dump their current rule row
rcard_ids = sorted({it["rule_id"] for it in pending_items if it["rule_id"].startswith("R-CARD")})
rcard_info = []
for rid in rcard_ids:
    cur.execute("SELECT rule_id, topic, status, needs_verification, proposed_canonical_rule FROM rules WHERE rule_id=?", (rid,))
    row = cur.fetchone()
    rcard_info.append(dict(row))
probe["rcard_rules_with_pending_rcc"] = rcard_info

# 6. sources authority reference (005/007/011 zh faq, 012/014/016/019 en)
cur.execute("SELECT source_id, source_document, source_type, language, version, date, effective_date, date_confidence, notes FROM sources WHERE source_id IN ('source_005','source_007','source_011','source_012','source_014','source_016','source_019','source_008','source_001','source_006','source_009','source_018')")
probe["sources_ref"] = [dict(r) for r in cur.fetchall()]

# 7. existing changes/rec prefix counters for id allocation
cur.execute("SELECT COUNT(*) n FROM changes WHERE change_id LIKE 'CHG-4B-B006-%'")
probe["existing_b006_changes"] = cur.fetchone()["n"]
cur.execute("SELECT COUNT(*) n FROM reconciliations WHERE reconciliation_id LIKE 'REC-4B-B006-%'")
probe["existing_b006_recs"] = cur.fetchone()["n"]

# 8. MR-2D-0005 watch cards
cur.execute("SELECT * FROM manual_review WHERE item_id IN ('MR-2D-0005','MR-2D-0010')")
probe["mr_watch"] = [dict(r) for r in cur.fetchall()]

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(probe, f, ensure_ascii=False, indent=2)

print("pending_buckets:", probe["pending_buckets"])
print("rcc_total:", probe["rcc_total"], "pending:", probe["rcc_pending_count"],
      "by_bucket:", probe["rcc_pending_by_rule_bucket"])
print("rcc_by_source:", json.dumps(probe["rcc_by_source"], ensure_ascii=False))
print("rcard_pending_rcc:", [r["rule_id"] for r in rcard_info])
print("existing_b006: chg=%d rec=%d" % (probe["existing_b006_changes"], probe["existing_b006_recs"]))
print("dump ->", OUT)
