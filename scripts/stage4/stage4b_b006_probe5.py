# -*- coding: utf-8 -*-
"""Probe 5: MR-2D-0005 fold-in preconditions + REC id collision check."""
import json, sqlite3

con = sqlite3.connect("workspace/rules_work.db")
con.row_factory = sqlite3.Row
out = {}

cards = ["R-CARD-OGN-131", "R-CARD-OGN-251", "R-CARD-UNL-097", "R-CARD-UNL-177"]
out["watch_cards"] = [dict(r) for r in con.execute(f"""
    SELECT rule_id, status, needs_verification,
           substr(official_interpretation,1,150) oi
    FROM rules WHERE rule_id IN ({','.join('?'*len(cards))})""", cards)]
out["faq0260_links"] = [dict(r) for r in con.execute("""
    SELECT rule_id, evidence_id, relationship FROM rule_evidence
    WHERE evidence_id='EV-CN-FAQ-0260'""")]
out["t3_collisions"] = con.execute(
    "SELECT COUNT(*) FROM reconciliations WHERE reconciliation_id LIKE 'REC-4B-T3-%'").fetchone()[0]
out["chg_t3_collisions"] = con.execute(
    "SELECT COUNT(*) FROM changes WHERE change_id LIKE 'CHG-4B-T3-%'").fetchone()[0]
out["existing_rec_multi"] = [dict(r) for r in con.execute("""
    SELECT rule_id, COUNT(*) n FROM reconciliations
    WHERE rule_id LIKE 'R-CARD%' GROUP BY 1 HAVING n > 1 LIMIT 5""")]
# does any rule already have >1 REC rows (precedent for second REC row)?
out["rules_with_multi_rec"] = con.execute(
    "SELECT COUNT(*) FROM (SELECT rule_id FROM reconciliations GROUP BY rule_id HAVING COUNT(*)>1)").fetchone()[0]
# source_019 doc name
out["s019_doc"] = dict(con.execute(
    "SELECT source_id, source_document FROM sources WHERE source_id='source_019'").fetchone())
out["s005_doc"] = dict(con.execute(
    "SELECT source_id, source_document FROM sources WHERE source_id='source_005'").fetchone())
# evidence faq fields non-null check for the 156 interp entries on pending
out["interp_missing_qa"] = con.execute("""
    SELECT COUNT(*) FROM rule_evidence re JOIN evidence e ON e.evidence_id=re.evidence_id
    WHERE re.relationship='faq:rule_interpretation'
      AND re.rule_id IN (SELECT rule_id FROM rules WHERE status='pending_reconciliation')
      AND (e.faq_question IS NULL)""").fetchone()[0]
print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
