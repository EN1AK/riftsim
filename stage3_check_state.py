"""Stage 3: check actual DB state vs README (alignments/manual_review/tasks already present?)."""
import sqlite3
import json

DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

out = {}

# alignments breakdown
c.execute("SELECT relation, COUNT(*) n FROM alignments GROUP BY relation")
out["alignments_by_relation"] = [dict(r) for r in c.fetchall()]
c.execute("SELECT * FROM alignments LIMIT 3")
out["alignments_sample"] = [dict(r) for r in c.fetchall()]

# manual_review breakdown (schema: item_id, rule_id, issue_description, ...)
c.execute("SELECT rule_id, COUNT(*) n FROM manual_review GROUP BY rule_id ORDER BY n DESC LIMIT 30")
out["manual_review_by_rule_id"] = [dict(r) for r in c.fetchall()]
c.execute("SELECT * FROM manual_review LIMIT 5")
out["manual_review_sample"] = [{k: (str(v)[:120] if v is not None else None) for k, v in dict(r).items()} for r in c.fetchall()]

# processing_tasks beyond the 43 known
c.execute("SELECT task_id, source_id, status, substr(notes,1,120) notes FROM processing_tasks ORDER BY rowid DESC LIMIT 12")
out["recent_tasks"] = [dict(r) for r in c.fetchall()]
c.execute("SELECT source_id, status, COUNT(*) n FROM processing_tasks GROUP BY source_id, status")
out["tasks_by_source_status"] = [dict(r) for r in c.fetchall()]

# evidence: check rule_number pairing readiness (zh vs en core rules)
c.execute("""SELECT COUNT(*) FROM evidence
             WHERE source_type='rule' AND source_language='zh' AND rule_number IS NOT NULL AND rule_number != ''""")
out["zh_rules_with_number"] = c.fetchone()[0]
c.execute("""SELECT COUNT(*) FROM evidence
             WHERE source_type='rule' AND source_language='en' AND rule_number IS NOT NULL AND rule_number != ''""")
out["en_rules_with_number"] = c.fetchone()[0]

# card_ids coverage on errata/faq
c.execute("""SELECT source_type, COUNT(*) total,
             SUM(CASE WHEN card_ids IS NOT NULL AND card_ids != '' THEN 1 ELSE 0 END) with_cards
             FROM evidence WHERE source_type IN ('errata','faq','official_explanation')
             GROUP BY source_type""")
out["cardid_coverage"] = [dict(r) for r in c.fetchall()]

print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
conn.close()
