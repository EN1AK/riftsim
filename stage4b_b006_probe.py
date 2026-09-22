# -*- coding: utf-8 -*-
"""Probe pending 4B-B006 rules + RCC links. Read-only; dumps JSON to stdout path."""
import json, sqlite3, sys
from collections import Counter, defaultdict

DB = "workspace/rules_work.db"
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row

out = {}

# rules table columns first
out["rules_cols"] = [c[1] for c in con.execute("PRAGMA table_info(rules)")]

# 1) pending rules
pend = [dict(r) for r in con.execute(
    "SELECT * FROM rules WHERE status='pending_reconciliation' ORDER BY rule_id")]
out["pending_count"] = len(pend)
out["pending_by_prefix"] = dict(Counter(r["rule_id"].split("-")[1] for r in pend))
keep = [k for k in ("rule_id", "canonical_topic", "topic", "proposed_canonical_rule",
                    "status", "needs_verification", "notes") if k in out["rules_cols"]]
out["pending_rules"] = [{k: r[k] for k in keep} for r in pend]

# 2) RCC links overall on pending rules
rcc = [dict(r) for r in con.execute("""
    SELECT re.rule_id, re.evidence_id, re.relationship, e.source_id, e.faq_classification,
           e.topic, e.rule_number, substr(e.normalized_summary,1,120) AS snip
    FROM rule_evidence re JOIN evidence e ON e.evidence_id = re.evidence_id
    WHERE re.relationship = 'faq:rule_change_candidate'
      AND re.rule_id IN (SELECT rule_id FROM rules WHERE status='pending_reconciliation')
    ORDER BY re.rule_id, re.evidence_id""")]
out["rcc_on_pending"] = rcc
out["rcc_by_source"] = dict(Counter(r["source_id"] for r in rcc))
out["rcc_by_rule_prefix"] = dict(Counter(r["rule_id"].rsplit("-", 1)[0] for r in rcc))

# 3) all evidence links on pending rules, counted by relationship
links = [dict(r) for r in con.execute("""
    SELECT re.rule_id, re.relationship, COUNT(*) AS n
    FROM rule_evidence re
    WHERE re.rule_id IN (SELECT rule_id FROM rules WHERE status='pending_reconciliation')
    GROUP BY 1, 2 ORDER BY 1, 2""")]
out["link_types_on_pending"] = links

# 4) which R-TOPIC/R-MISC rules have NON-front-matter, non-RCC evidence?
ev = [dict(r) for r in con.execute("""
    SELECT re.rule_id, re.relationship, re.evidence_id, e.source_id, e.faq_classification
    FROM rule_evidence re JOIN evidence e ON e.evidence_id = re.evidence_id
    WHERE re.rule_id IN (SELECT rule_id FROM rules WHERE status='pending_reconciliation')
      AND re.relationship NOT IN ('front_matter', 'faq:rule_change_candidate')
    ORDER BY re.rule_id""")]
out["other_links"] = ev
out["other_links_by_rel"] = dict(Counter(x["relationship"] for x in ev))

# 5) RCC evidence full rows (need original question/answer snippets for adjudication)
rcc_ev = [dict(r) for r in con.execute("""
    SELECT e.evidence_id, e.source_id, e.topic, e.rule_number,
           substr(e.faq_question,1,200) AS q, substr(e.faq_answer,1,300) AS a,
           substr(e.original_text,1,400) AS ot, e.notes
    FROM evidence e WHERE e.evidence_id IN (
        SELECT DISTINCT evidence_id FROM rule_evidence
        WHERE relationship='faq:rule_change_candidate'
          AND rule_id IN (SELECT rule_id FROM rules WHERE status='pending_reconciliation'))
    ORDER BY e.source_id, e.evidence_id""")]
out["rcc_evidence"] = rcc_ev

# 6) rules columns for reconciliation write pattern (copy from existing reconciled row)
sample = dict(con.execute(
    "SELECT * FROM reconciliations LIMIT 1").fetchone() or {})
out["reconciliations_cols"] = list(sample.keys())
out["reconciliations_cols_info"] = [list(c) for c in con.execute("PRAGMA table_info(reconciliations)")]
out["changes_cols_info"] = [list(c) for c in con.execute("PRAGMA table_info(changes)")]
out["rule_evidence_cols_info"] = [list(c) for c in con.execute("PRAGMA table_info(rule_evidence)")]
out["evidence_cols_info"] = [list(c[:2]) for c in con.execute("PRAGMA table_info(evidence)")]

# 7) MR-2D-0005 watch cards
out["manual_review_cols"] = [c[1] for c in con.execute("PRAGMA table_info(manual_review)")]
mr_id_col = out["manual_review_cols"][0]
out["mr_2d_0005"] = [dict(r) for r in con.execute(
    f"SELECT * FROM manual_review WHERE {mr_id_col}='MR-2D-0005'")]

# 8) sample REC row from B005 (tier-1 flagged) for pattern
out["rec_sample_b005"] = [dict(r) for r in con.execute(
    "SELECT * FROM reconciliations WHERE reconciliation_id LIKE 'REC-4B-T1F-%' LIMIT 1")]

with open("workspace/checkpoints/stage4b_b006_probe.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=str)
print(json.dumps({k: (v if not isinstance(v, list) else f"<{len(v)} rows>") for k, v in out.items()},
                 ensure_ascii=False, indent=2, default=str))
print("rcc_by_source:", out["rcc_by_source"])
print("rcc_by_rule_prefix:", out["rcc_by_rule_prefix"])
print("pending_by_prefix:", out["pending_by_prefix"])
print("other_links_by_rel:", out["other_links_by_rel"])
