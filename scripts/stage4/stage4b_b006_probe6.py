# -*- coding: utf-8 -*-
"""Probe 6: interp entries missing Q on pending; per-source/tier check; watch-card example columns."""
import json, sqlite3

con = sqlite3.connect("workspace/rules_work.db")
con.row_factory = sqlite3.Row
out = {}

out["missing_q_sample"] = [dict(r) for r in con.execute("""
    SELECT e.evidence_id, e.source_id, substr(e.faq_question,1,120) q,
           substr(e.faq_answer,1,120) a, substr(e.original_text,1,160) ot
    FROM rule_evidence re JOIN evidence e ON e.evidence_id=re.evidence_id
    WHERE re.relationship='faq:rule_interpretation'
      AND re.rule_id IN (SELECT rule_id FROM rules WHERE status='pending_reconciliation')
      AND e.faq_question IS NULL LIMIT 6""")]

out["interp_by_source"] = [dict(r) for r in con.execute("""
    SELECT e.source_id, COUNT(*) n FROM rule_evidence re
    JOIN evidence e ON e.evidence_id=re.evidence_id
    WHERE re.relationship='faq:rule_interpretation'
      AND re.rule_id IN (SELECT rule_id FROM rules WHERE status='pending_reconciliation')
    GROUP BY 1""")]

out["watch_example_cols"] = [dict(r) for r in con.execute("""
    SELECT rule_id, substr(example,1,120) ex, substr(exception,1,80) exc
    FROM rules WHERE rule_id IN ('R-CARD-OGN-131','R-CARD-OGN-251','R-CARD-UNL-097','R-CARD-UNL-177')""")]

# existing CHG row sample for format convention
out["chg_sample"] = [dict(r) for r in con.execute(
    "SELECT * FROM changes WHERE change_id='CHG-4B-T1F-0001'")]

# count RCC links on pending with 019
out["rcc019_pending"] = [dict(r) for r in con.execute("""
    SELECT re.rule_id, e.evidence_id FROM rule_evidence re
    JOIN evidence e ON e.evidence_id=re.evidence_id
    WHERE re.relationship='faq:rule_change_candidate' AND e.source_id='source_019'
      AND re.rule_id IN (SELECT rule_id FROM rules WHERE status='pending_reconciliation')
    ORDER BY 1,2""")]

print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
