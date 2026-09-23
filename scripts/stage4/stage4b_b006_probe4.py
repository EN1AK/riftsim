# -*- coding: utf-8 -*-
"""Probe 4: needs_verification storage, attach format detail, tier-1 REC detail."""
import json, sqlite3

con = sqlite3.connect("workspace/rules_work.db")
con.row_factory = sqlite3.Row
out = {}

out["nv_values"] = [dict(r) for r in con.execute(
    "SELECT needs_verification, COUNT(*) n FROM rules GROUP BY 1")]

# tier-1 attach format (one FAQ-only R-CARD fully)
row = con.execute("""
    SELECT r.* FROM rules r JOIN reconciliations re ON re.rule_id=r.rule_id
    WHERE re.status='reconciled_tier1' AND r.rule_id LIKE 'R-CARD%'
      AND r.official_interpretation IS NOT NULL LIMIT 1""").fetchone()
out["t1_attach_rule"] = dict(row) if row else None

row2 = con.execute("""
    SELECT * FROM reconciliations WHERE status='reconciled_tier1'
      AND rule_id LIKE 'R-CARD%' LIMIT 2""").fetchall()
out["t1_rec_rows"] = [dict(r) for r in row2]

# how is authority tier rendered in attached text (judge-community vs official)?
out["tiers_in_oi"] = [r[0][:90] for r in con.execute("""
    SELECT DISTINCT official_interpretation FROM rules
    WHERE official_interpretation LIKE '[%' AND official_interpretation IS NOT NULL
    LIMIT 6""")]

with open("workspace/checkpoints/stage4b_b006_probe4.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1, default=str)
print("nv_values:", out["nv_values"])
print("tiers:", *out["tiers_in_oi"], sep="\n  ")
