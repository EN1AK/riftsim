# -*- coding: utf-8 -*-
"""Probe 2: RCC links on R-CARD rules, attach-format sample from B002, source metadata."""
import json, sqlite3
from collections import Counter

con = sqlite3.connect("workspace/rules_work.db")
con.row_factory = sqlite3.Row
out = {}

# 1) RCC links NOT on pending rules (the 11 on R-CARD)
out["rcc_on_card"] = [dict(r) for r in con.execute("""
    SELECT re.rule_id, re.evidence_id, e.source_id, e.topic,
           substr(e.normalized_summary,1,160) AS snip, r.status
    FROM rule_evidence re JOIN evidence e ON e.evidence_id = re.evidence_id
    JOIN rules r ON r.rule_id = re.rule_id
    WHERE re.relationship = 'faq:rule_change_candidate'
      AND re.rule_id NOT IN (SELECT rule_id FROM rules WHERE status='pending_reconciliation')
    ORDER BY re.rule_id""")]

# total RCC links count sanity
out["rcc_total"] = con.execute(
    "SELECT COUNT(*) FROM rule_evidence WHERE relationship='faq:rule_change_candidate'").fetchone()[0]

# 2) B002 attach format sample: a reconciled FAQ-only R-CARD + a flagged one
out["attach_sample"] = [dict(r) for r in con.execute("""
    SELECT rule_id, status, needs_verification,
           substr(official_interpretation,1,400) AS oi,
           substr(example,1,300) AS ex, substr(exception,1,200) AS exc
    FROM rules WHERE rule_id LIKE 'R-CARD%' AND status='reconciled'
      AND official_interpretation IS NOT NULL LIMIT 2""")]

# 3) B002 reconciliation row for a FAQ-only R-CARD
out["rec_t1_sample"] = [dict(r) for r in con.execute("""
    SELECT * FROM reconciliations WHERE reconciliation_id LIKE 'REC-4B-T1-%' LIMIT 2""")]

# 4) source metadata for 005/012/014/016/019
out["sources"] = [dict(r) for r in con.execute("""
    SELECT source_id, source_type, language, version, date, effective_date, date_confidence,
           substr(notes,1,200) AS notes
    FROM sources WHERE source_id IN ('source_005','source_012','source_014','source_016','source_019')""")]

# 5) faq:rule_interpretation links on pending rules by source
out["interp_on_pending_by_source"] = [dict(r) for r in con.execute("""
    SELECT e.source_id, re.rule_id, COUNT(*) n
    FROM rule_evidence re JOIN evidence e ON e.evidence_id=re.evidence_id
    WHERE re.relationship='faq:rule_interpretation'
      AND re.rule_id IN (SELECT rule_id FROM rules WHERE status='pending_reconciliation')
    GROUP BY 1,2 ORDER BY 1,2""")]

# 6) classification distribution among the 156 interp links on pending
out["class_on_pending"] = [dict(r) for r in con.execute("""
    SELECT e.faq_classification, COUNT(*) n
    FROM rule_evidence re JOIN evidence e ON e.evidence_id=re.evidence_id
    WHERE re.rule_id IN (SELECT rule_id FROM rules WHERE status='pending_reconciliation')
      AND re.relationship NOT IN ('front_matter')
    GROUP BY 1""")]

# 7) front-matter links on the two front rules
out["front_links"] = [dict(r) for r in con.execute("""
    SELECT rule_id, evidence_id, relationship FROM rule_evidence
    WHERE rule_id IN ('R-ER-FRONT','R-FAQ-FRONT')""")]

# 8) 019 source_019 items on R-TOPIC/R-MISC: do any reference specific core rule numbers?
out["s019_rcc_full"] = [dict(r) for r in con.execute("""
    SELECT re.rule_id, e.evidence_id, e.topic, substr(e.faq_question,1,220) q,
           substr(e.faq_answer,1,260) a, e.notes
    FROM rule_evidence re JOIN evidence e ON e.evidence_id=re.evidence_id
    WHERE re.relationship='faq:rule_change_candidate' AND e.source_id='source_019'
    ORDER BY e.evidence_id""")]

with open("workspace/checkpoints/stage4b_b006_probe2.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1, default=str)
print("rcc_total:", out["rcc_total"])
print("rcc_on_card count:", len(out["rcc_on_card"]))
for r in out["rcc_on_card"]:
    print(r["rule_id"], r["evidence_id"], r["source_id"], r["status"], r["snip"][:80])
print("---sources---")
for s in out["sources"]:
    print(s["source_id"], s["source_type"], s["language"], s["date"], s["effective_date"], s["date_confidence"])
print("---class_on_pending---", out["class_on_pending"])
print("---front_links---", out["front_links"])
