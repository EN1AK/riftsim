# -*- coding: utf-8 -*-
"""Probe 3: statuses, attach format, tier-1 REC format, RCC per-rule source mix."""
import json, sqlite3
from collections import Counter, defaultdict

con = sqlite3.connect("workspace/rules_work.db")
con.row_factory = sqlite3.Row
out = {}

out["rule_status_counts"] = [dict(r) for r in con.execute(
    "SELECT status, COUNT(*) n, SUM(CASE WHEN needs_verification THEN 1 ELSE 0 END) nv FROM rules GROUP BY 1")]
out["rec_status_counts"] = [dict(r) for r in con.execute(
    "SELECT status, COUNT(*) n FROM reconciliations GROUP BY 1")]

# front-matter rules already reconciled?
out["cr_front"] = [dict(r) for r in con.execute(
    "SELECT rule_id, topic, status, needs_verification, substr(proposed_canonical_rule,1,200) pcr FROM rules WHERE rule_id LIKE '%FRONT%'")]
out["cr_front_rec"] = [dict(r) for r in con.execute(
    "SELECT * FROM reconciliations WHERE rule_id LIKE '%FRONT%'")]

# attach format on a FAQ-only R-CARD (B002)
out["attach_sample"] = [dict(r) for r in con.execute("""
    SELECT rule_id, status, needs_verification,
           substr(official_interpretation,1,600) AS oi, substr(example,1,300) AS ex
    FROM rules WHERE rule_id LIKE 'R-CARD%' AND status='reconciled'
      AND official_interpretation IS NOT NULL
      AND rule_id IN (SELECT rule_id FROM reconciliations WHERE reconciliation_id LIKE 'REC-4B-T1-%')
    LIMIT 1""")]
out["rec_t1_sample"] = [dict(r) for r in con.execute(
    "SELECT * FROM reconciliations WHERE reconciliation_id LIKE 'REC-4B-T1-%' LIMIT 1")]

# RCC per pending rule: source mix
mix = defaultdict(set)
cnt = defaultdict(int)
for r in con.execute("""
    SELECT re.rule_id, e.source_id FROM rule_evidence re
    JOIN evidence e ON e.evidence_id=re.evidence_id
    WHERE re.relationship='faq:rule_change_candidate'
      AND re.rule_id IN (SELECT rule_id FROM rules WHERE status='pending_reconciliation')"""):
    mix[r["rule_id"]].add(r["source_id"]); cnt[r["rule_id"]] += 1
out["rcc_rules_mix"] = {k: sorted(v) for k, v in sorted(mix.items())}
out["rcc_rules_total"] = len(mix)
out["rcc_link_total_pending"] = sum(cnt.values())

# interp links per pending rule count
ic = Counter()
for r in con.execute("""
    SELECT re.rule_id FROM rule_evidence re
    WHERE re.relationship='faq:rule_interpretation'
      AND re.rule_id IN (SELECT rule_id FROM rules WHERE status='pending_reconciliation')"""):
    ic[r["rule_id"]] += 1
out["interp_per_pending"] = dict(ic)

# pending rules with NEITHER rcc NOR interp (only front_matter?)
out["pending_linkless"] = [r["rule_id"] for r in con.execute("""
    SELECT rule_id FROM rules WHERE status='pending_reconciliation'
      AND rule_id NOT IN (SELECT rule_id FROM rule_evidence
                          WHERE relationship != 'front_matter')""")]

# authority tier mapping used in B002: check how tier recorded in attach prefix
out["tier_sample"] = [dict(r) for r in con.execute("""
    SELECT DISTINCT substr(official_interpretation,1,120) AS p
    FROM rules WHERE official_interpretation LIKE '[%' LIMIT 3""")]

print(json.dumps(out["rule_status_counts"], ensure_ascii=False))
print(json.dumps(out["rec_status_counts"], ensure_ascii=False))
print("cr_front:", json.dumps(out["cr_front"], ensure_ascii=False))
print("cr_front_rec:", json.dumps(out["cr_front_rec"], ensure_ascii=False)[:800])
print("rcc_rules_total:", out["rcc_rules_total"], "links:", out["rcc_link_total_pending"])
print("pending_linkless:", out["pending_linkless"])
with open("workspace/checkpoints/stage4b_b006_probe3.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1, default=str)
print("dumped")
