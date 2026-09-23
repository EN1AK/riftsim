"""Stage 3 batch 3-ER pre-check: errata evidence fields + pairing inputs."""
import sqlite3
import json

DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()
out = {}

c.execute("PRAGMA table_info(evidence)")
out["evidence_cols"] = [r["name"] for r in c.fetchall()]

# errata rows summary by source
c.execute("""SELECT source_id, source_language, COUNT(*) n,
             SUM(CASE WHEN card_ids IS NOT NULL AND card_ids != '' THEN 1 ELSE 0 END) with_cardids
             FROM evidence WHERE source_type='errata'
             GROUP BY source_id, source_language ORDER BY source_id""")
out["errata_by_source"] = [dict(r) for r in c.fetchall()]

# sample zh errata
c.execute("""SELECT evidence_id, source_id, page, rule_number, target_rule_candidate,
             modification_type, card_ids, related_cards,
             substr(original_text,1,200) original_text,
             substr(normalized_summary,1,150) normalized_summary,
             substr(notes,1,150) notes
             FROM evidence WHERE source_type='errata' AND source_language='zh' LIMIT 5""")
out["zh_errata_sample"] = [dict(r) for r in c.fetchall()]

# sample en errata
c.execute("""SELECT evidence_id, source_id, page, rule_number, target_rule_candidate,
             modification_type, card_ids, related_cards,
             substr(original_text,1,200) original_text,
             substr(normalized_summary,1,150) normalized_summary,
             substr(notes,1,150) notes
             FROM evidence WHERE source_type='errata' AND source_language='en' LIMIT 5""")
out["en_errata_sample"] = [dict(r) for r in c.fetchall()]

# front_matter errata rows (no card_ids)
c.execute("""SELECT evidence_id, source_id, substr(original_text,1,150) t
             FROM evidence WHERE source_type='errata' AND (card_ids IS NULL OR card_ids='')""")
out["errata_front_matter"] = [dict(r) for r in c.fetchall()]

# distinct modification_type
c.execute("SELECT modification_type, COUNT(*) n FROM evidence WHERE source_type='errata' GROUP BY modification_type")
out["mod_types"] = [dict(r) for r in c.fetchall()]

# date/version info for errata sources (pairing context)
c.execute("""SELECT source_id, source_document, language, date, effective_date, version, possible_counterpart
             FROM sources WHERE source_type='errata' ORDER BY source_id""")
out["errata_sources"] = [dict(r) for r in c.fetchall()]

print(json.dumps(out, ensure_ascii=False, indent=2))
conn.close()
