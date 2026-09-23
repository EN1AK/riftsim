"""Stage 3 3-FAQ pre-inspect: FAQ/OE sources + evidence fields for pairing strategy."""
import sqlite3
import json

DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()
out = {}

c.execute("""SELECT source_id, source_document, source_type, language, date, effective_date,
                    version, supersedes, possible_counterpart, substr(notes,1,200) notes
             FROM sources WHERE source_type IN ('faq','official_explanation') ORDER BY source_id""")
out["faq_sources"] = [dict(r) for r in c.fetchall()]

# evidence counts per source (excluding front_matter = no faq_question)
c.execute("""SELECT source_id, source_language, COUNT(*) n,
                    SUM(CASE WHEN faq_question IS NULL OR faq_question='' THEN 1 ELSE 0 END) no_question,
                    SUM(CASE WHEN card_ids IS NOT NULL AND card_ids!='' THEN 1 ELSE 0 END) with_cards,
                    SUM(CASE WHEN rule_id_candidate IS NOT NULL AND rule_id_candidate!='' THEN 1 ELSE 0 END) with_rulecand
             FROM evidence WHERE source_type IN ('faq','official_explanation')
             GROUP BY source_id, source_language ORDER BY source_id""")
out["faq_evidence"] = [dict(r) for r in c.fetchall()]

# faq_classification distribution per source
c.execute("""SELECT source_id, faq_classification, COUNT(*) n FROM evidence
             WHERE source_type IN ('faq','official_explanation')
             GROUP BY source_id, faq_classification ORDER BY source_id, n DESC""")
out["faq_class"] = [dict(r) for r in c.fetchall()]

# rule_id_candidate samples (may link zh/en via rule numbers)
c.execute("""SELECT evidence_id, source_id, substr(faq_question,1,80) q, rule_id_candidate, related_cards
             FROM evidence WHERE source_type IN ('faq','official_explanation')
               AND rule_id_candidate IS NOT NULL AND rule_id_candidate!='' LIMIT 12""")
out["rulecand_sample"] = [dict(r) for r in c.fetchall()]

# supersession tags
c.execute("""SELECT evidence_id, source_id, substr(notes,1,120) n FROM evidence
             WHERE source_type IN ('faq','official_explanation')
               AND (notes LIKE '%superseded%' OR notes LIKE '%supersedes%') LIMIT 15""")
out["supersession_rows"] = [dict(r) for r in c.fetchall()]
c.execute("""SELECT COUNT(*) FROM evidence WHERE source_type IN ('faq','official_explanation')
               AND (notes LIKE '%superseded%' OR notes LIKE '%supersedes%')""")
out["supersession_n"] = c.fetchone()[0]

print(json.dumps(out, ensure_ascii=False, indent=1))
conn.close()
