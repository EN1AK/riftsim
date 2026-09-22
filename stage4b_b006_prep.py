"""4B-B006 prep: reference points for main script (read-only)."""
import sqlite3, json

DB = "workspace/rules_work.db"
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
c = con.cursor()
out = {}

# 1. R-CR-FRONT precedent
c.execute("SELECT * FROM rules WHERE rule_id='R-CR-FRONT'")
r = dict(c.fetchone())
r["proposed_canonical_rule"] = (r["proposed_canonical_rule"] or "")[:300]
for k in ("official_interpretation","example","exception"):
    r[k] = (r[k] or "")[:200]
out["cr_front_rule"] = r
c.execute("SELECT * FROM reconciliations WHERE rule_id='R-CR-FRONT'")
out["cr_front_rec"] = [dict(x) for x in c.fetchall()]

# 2. CHG-4B-T1F sample (full)
c.execute("SELECT * FROM changes WHERE change_id LIKE 'CHG-4B-T1F-%' LIMIT 2")
out["chg_t1f_sample"] = []
for x in c.fetchall():
    d = dict(x)
    for k in ("original_content","new_content"):
        d[k] = (d[k] or "")[:400]
    out["chg_t1f_sample"].append(d)

# 2b. CHG-4B-T2ER sample (structure of applied errata change rows)
c.execute("SELECT * FROM changes WHERE change_id LIKE 'CHG-4B-T2ER-%' LIMIT 1")
out["chg_t2er_sample"] = []
for x in c.fetchall():
    d = dict(x)
    for k in ("original_content","new_content"):
        d[k] = (d[k] or "")[:300]
    out["chg_t2er_sample"].append(d)

# 3. watch cards (MR-2D-0005): find rule ids
c.execute("SELECT rule_id, status, needs_verification FROM rules WHERE rule_id IN ('R-CARD-OGN-131','R-CARD-OGN-251','R-CARD-UNL-097','R-CARD-UNL-177','R-CARD-UNL-97')")
out["watch_cards_direct"] = [dict(x) for x in c.fetchall()]
c.execute("SELECT DISTINCT rule_id FROM rule_evidence WHERE rule_id LIKE 'R-CARD-%' AND evidence_id='EV-CN-FAQ-0260'")
out["watch_cards_via_evidence"] = [x[0] for x in c.fetchall()]
c.execute("SELECT evidence_id, card_ids, notes FROM evidence WHERE evidence_id='EV-CN-FAQ-0260'")
out["faq0260"] = [dict(x) for x in c.fetchall()]

# 4. the 11 (or so) RCC links on reconciled R-CARD rules
c.execute("""
SELECT re.rule_id, re.evidence_id, e.source_id, r.status, r.needs_verification,
       substr(COALESCE(e.faq_question, e.original_text,''),1,150) q
FROM rule_evidence re JOIN evidence e ON e.evidence_id=re.evidence_id
JOIN rules r ON r.rule_id=re.rule_id
WHERE re.relationship='faq:rule_change_candidate' AND r.status='reconciled'
ORDER BY e.source_id, re.evidence_id
""")
out["rcc_on_reconciled"] = [dict(x) for x in c.fetchall()]

# 5. front_matter links on pending rules
c.execute("""
SELECT re.rule_id, re.evidence_id, e.source_id, substr(COALESCE(e.original_text,''),1,120) t
FROM rule_evidence re JOIN evidence e ON e.evidence_id=re.evidence_id
WHERE re.relationship='front_matter' AND re.rule_id IN ('R-ER-FRONT','R-FAQ-FRONT','R-MISC-source_011','R-MISC-source_012','R-MISC-source_014','R-MISC-source_016','R-MISC-source_019')
ORDER BY re.rule_id, re.evidence_id
""")
out["front_links"] = [dict(x) for x in c.fetchall()]

# 6. sources for changes rows
c.execute("SELECT source_id, source_document, source_type, language, date, effective_date, date_confidence FROM sources WHERE source_id IN ('source_005','source_011','source_012','source_014','source_016','source_019')")
out["sources_sub"] = [dict(x) for x in c.fetchall()]

# 7. do any pending rules have exception/example-only links? (expect none)
c.execute("""
SELECT re.relationship, COUNT(*) n FROM rule_evidence re
WHERE re.rule_id IN (SELECT rule_id FROM rules WHERE status='pending_reconciliation')
GROUP BY re.relationship
""")
out["pending_rel_final"] = {x[0]: x[1] for x in c.fetchall()}

# 8. R-TOPIC-EN-37 style: how many pending rules carry ONLY interp (no rcc)?
c.execute("""
SELECT r.rule_id,
  SUM(CASE WHEN re.relationship='faq:rule_change_candidate' THEN 1 ELSE 0 END) rcc,
  SUM(CASE WHEN re.relationship='faq:rule_interpretation' THEN 1 ELSE 0 END) interp,
  SUM(CASE WHEN re.relationship='front_matter' THEN 1 ELSE 0 END) fm
FROM rules r LEFT JOIN rule_evidence re ON re.rule_id=r.rule_id
WHERE r.status='pending_reconciliation'
GROUP BY r.rule_id
""")
rows = [dict(x) for x in c.fetchall()]
out["pending_shape"] = {"rules_with_rcc": sum(1 for x in rows if x["rcc"]),
                        "rules_only_interp": sum(1 for x in rows if not x["rcc"] and x["interp"]),
                        "rules_only_fm": sum(1 for x in rows if not x["rcc"] and not x["interp"] and x["fm"]),
                        "rules_empty": sum(1 for x in rows if not x["rcc"] and not x["interp"] and not x["fm"])}
out["empty_rules"] = [x["rule_id"] for x in rows if not x["rcc"] and not x["interp"] and not x["fm"]]

with open("workspace/checkpoints/stage4b_b006_prep.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print("cr_front status/canonical:", out["cr_front_rule"]["status"], "|", (out["cr_front_rule"]["proposed_canonical_rule"] or "")[:120],
      "| nv:", out["cr_front_rule"]["needs_verification"])
print("cr_front rec:", json.dumps(out["cr_front_rec"], ensure_ascii=False)[:300])
print("chg_t1f:", json.dumps(out["chg_t1f_sample"], ensure_ascii=False)[:600])
print("chg_t2er:", json.dumps(out["chg_t2er_sample"], ensure_ascii=False)[:600])
print("watch direct:", out["watch_cards_direct"])
print("watch via ev:", out["watch_cards_via_evidence"])
print("faq0260:", json.dumps(out["faq0260"], ensure_ascii=False)[:300])
print("rcc_on_reconciled:", [(x["rule_id"], x["evidence_id"], x["source_id"]) for x in out["rcc_on_reconciled"]])
print("front_links:", [(x["rule_id"], x["evidence_id"], x["source_id"]) for x in out["front_links"]])
print("sources_sub:", json.dumps(out["sources_sub"], ensure_ascii=False))
print("pending_rel_final:", out["pending_rel_final"])
print("pending_shape:", out["pending_shape"], "empty:", out["empty_rules"])
