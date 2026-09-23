"""Stage 3 final confirmation: tasks + coverage + state files."""
import sqlite3
import json

DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()
out = {}

c.execute("SELECT task_id, status FROM processing_tasks WHERE task_id LIKE 'task_3_%' ORDER BY task_id")
out["tasks"] = [dict(r) for r in c.fetchall()]

c.execute("SELECT substr(alignment_id,1,6) p, relation, COUNT(*) n FROM alignments GROUP BY p, relation ORDER BY p")
out["alignments"] = [dict(r) for r in c.fetchall()]

c.execute("""SELECT COUNT(*) FROM evidence e WHERE source_type='rule'
             AND NOT EXISTS (SELECT 1 FROM alignments a WHERE a.evidence_a=e.evidence_id OR a.evidence_b=e.evidence_id)""")
out["core_rules_unpaired"] = c.fetchone()[0]
c.execute("""SELECT COUNT(*) FROM evidence e WHERE source_type='errata'
             AND notes NOT LIKE '%stage3_alignment%'
             AND NOT EXISTS (SELECT 1 FROM alignments a WHERE a.evidence_a=e.evidence_id OR a.evidence_b=e.evidence_id)""")
out["errata_unresolved"] = c.fetchone()[0]
c.execute("""SELECT COUNT(*) FROM evidence WHERE source_type IN ('faq','official_explanation')
             AND notes NOT LIKE '%stage3_alignment%'""")
out["faq_oe_untagged"] = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM manual_review WHERE item_id LIKE 'MR-2%' AND issue_description NOT LIKE '%关闭%' AND issue_description NOT LIKE '%结案%' AND issue_description NOT LIKE '%resolved%' AND issue_description NOT LIKE '%裁定%'")
out["stage2_mr_possibly_open"] = c.fetchone()[0]

print(json.dumps(out, ensure_ascii=False, indent=1))
conn.close()
