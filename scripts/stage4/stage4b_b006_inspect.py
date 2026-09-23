"""4B-B006 recon: dump pending rules + RCC link distribution into checkpoint json (no chat dump)."""
import sqlite3, json, collections

DB = "workspace/rules_work.db"
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
c = con.cursor()

out = {}

# 1. rule status counts
c.execute("SELECT status, COUNT(*) n FROM rules GROUP BY status")
out["rule_status"] = {r["status"]: r["n"] for r in c.fetchall()}

# 2. pending rules by bucket prefix
c.execute("SELECT rule_id, topic, needs_verification FROM rules WHERE status='pending_reconciliation' ORDER BY rule_id")
pending = [dict(r) for r in c.fetchall()]
out["pending_count"] = len(pending)
buckets = collections.Counter()
for r in pending:
    rid = r["rule_id"]
    if rid.startswith("R-TOPIC-CN"): buckets["R-TOPIC-CN"] += 1
    elif rid.startswith("R-TOPIC-EN"): buckets["R-TOPIC-EN"] += 1
    elif rid.startswith("R-MISC"): buckets["R-MISC"] += 1
    else: buckets[rid] += 1
out["pending_buckets"] = dict(buckets)

# 3. evidence links per pending rule (relationship distribution, source distribution)
c.execute("""
SELECT re.rule_id, re.evidence_id, re.relationship, re.notes, e.source_id, e.source_type,
       e.faq_classification, e.section, e.rule_id_candidate
FROM rule_evidence re JOIN evidence e ON e.evidence_id = re.evidence_id
WHERE re.rule_id IN (SELECT rule_id FROM rules WHERE status='pending_reconciliation')
ORDER BY re.rule_id, re.evidence_id
""")
links = [dict(r) for r in c.fetchall()]
out["pending_links_total"] = len(links)
rel_dist = collections.Counter(l["relationship"] for l in links)
out["pending_relationship_dist"] = dict(rel_dist)
src_dist = collections.Counter(l["source_id"] for l in links)
out["pending_source_dist"] = dict(sorted(src_dist.items()))

rcc = [l for l in links if l["relationship"] == "faq:rule_change_candidate"]
out["rcc_count"] = len(rcc)
rcc_src = collections.Counter(l["source_id"] for l in rcc)
out["rcc_source_dist"] = dict(sorted(rcc_src.items()))
rcc_bucket = collections.Counter()
for l in rcc:
    rid = l["rule_id"]
    if rid.startswith("R-TOPIC-CN"): rcc_bucket["R-TOPIC-CN"] += 1
    elif rid.startswith("R-TOPIC-EN"): rcc_bucket["R-TOPIC-EN"] += 1
    elif rid.startswith("R-MISC"): rcc_bucket["R-MISC"] += 1
    elif rid.startswith("R-CARD"): rcc_bucket["R-CARD"] += 1
    elif rid.startswith("R-CR"): rcc_bucket["R-CR"] += 1
    else: rcc_bucket[rid] += 1
out["rcc_rule_bucket_dist"] = dict(sorted(rcc_bucket.items()))

# 4. per-rule detail: rule_id -> list of links
per_rule = collections.defaultdict(list)
for l in links:
    per_rule[l["rule_id"]].append({
        "evidence_id": l["evidence_id"], "relationship": l["relationship"],
        "source_id": l["source_id"], "source_type": l["source_type"],
        "faq_classification": l["faq_classification"],
        "section": l["section"], "rule_id_candidate": l["rule_id_candidate"],
    })
out["per_rule_links"] = {r["rule_id"]: per_rule.get(r["rule_id"], []) for r in pending}
out["pending_rules"] = pending

# 5. RCC evidence details (need faq question/answer summary + dates to adjudicate)
c.execute("""
SELECT re.rule_id, re.evidence_id, e.source_id, e.source_document, e.date,
       e.section, e.rule_id_candidate, e.card_ids,
       substr(COALESCE(e.faq_question,''),1,300) fq,
       substr(COALESCE(e.faq_answer,''),1,500) fa,
       substr(COALESCE(e.original_text,''),1,600) ot
FROM rule_evidence re JOIN evidence e ON e.evidence_id = re.evidence_id
WHERE re.relationship='faq:rule_change_candidate'
  AND re.rule_id IN (SELECT rule_id FROM rules WHERE status='pending_reconciliation')
ORDER BY e.source_id, re.evidence_id
""")
out["rcc_details"] = [dict(r) for r in c.fetchall()]

# 6. also: RCC links on NON-pending rules (should be 0 per B005 note: 12 remaining on reconciled? check)
c.execute("""
SELECT re.rule_id, r.status, e.source_id
FROM rule_evidence re JOIN evidence e ON e.evidence_id = re.evidence_id
JOIN rules r ON r.rule_id = re.rule_id
WHERE re.relationship='faq:rule_change_candidate'
""")
all_rcc = [dict(r) for r in c.fetchall()]
out["all_rcc_total"] = len(all_rcc)
out["all_rcc_by_rule_status"] = dict(collections.Counter(f'{r["status"]}' for r in all_rcc))

# 7. sources dates for authority adjudication
c.execute("SELECT source_id, source_document, source_type, language, date, effective_date, date_confidence FROM sources ORDER BY source_id")
out["sources"] = [dict(r) for r in c.fetchall()]

with open("workspace/checkpoints/stage4b_b006_recon.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print("pending:", out["pending_count"], out["pending_buckets"])
print("links:", out["pending_links_total"], out["pending_relationship_dist"])
print("rcc on pending:", out["rcc_count"], "src:", out["rcc_source_dist"], "bucket:", out["rcc_rule_bucket_dist"])
print("all rcc:", out["all_rcc_total"], out["all_rcc_by_rule_status"])
print("pending src dist:", out["pending_source_dist"])
