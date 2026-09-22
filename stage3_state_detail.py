"""Stage 3 detailed state: manual_review new rows, alignment counts by task, entity-resolution artifacts."""
import sqlite3
import json
import os

DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
REP = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\reports"

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()
out = {}

# manual_review schema first (status col name may differ)
c.execute("PRAGMA table_info(manual_review)")
mr_cols = [r["name"] for r in c.fetchall()]
out["mr_cols"] = mr_cols
status_col = "status" if "status" in mr_cols else None
if status_col:
    c.execute("SELECT status, COUNT(*) n FROM manual_review GROUP BY status")
    out["mr_by_status"] = [dict(r) for r in c.fetchall()]
c.execute("SELECT substr(item_id,1,8) prefix, COUNT(*) n FROM manual_review GROUP BY prefix ORDER BY prefix")
out["mr_by_prefix"] = [dict(r) for r in c.fetchall()]

# recent MR rows (added during stage 3?)
c.execute("""SELECT item_id, substr(issue_description,1,100) d, source_a, source_b
             FROM manual_review ORDER BY rowid DESC LIMIT 15""")
out["mr_recent"] = [dict(r) for r in c.fetchall()]

# alignments by id prefix
c.execute("SELECT substr(alignment_id,1,8) prefix, COUNT(*) n FROM alignments GROUP BY prefix")
out["align_by_prefix"] = [dict(r) for r in c.fetchall()]

# stage-3 task rows full notes
c.execute("SELECT task_id, status, notes FROM processing_tasks WHERE task_id LIKE 'task_3_%' ORDER BY task_id")
out["stage3_tasks"] = [dict(r) for r in c.fetchall()]

# entity resolution artifacts: card_ids formats in evidence
c.execute("""SELECT card_ids FROM evidence
             WHERE source_type IN ('errata','faq','official_explanation')
               AND card_ids IS NOT NULL AND card_ids != '' LIMIT 5""")
out["cardids_sample"] = [r[0] for r in c.fetchall()]

# any evidence rows tagged by stage3 entity pass
c.execute("""SELECT COUNT(*) FROM evidence WHERE notes LIKE '%entity%' OR notes LIKE '%card_key%'""")
out["notes_entity_tag"] = c.fetchone()[0]

# alignments table schema
c.execute("PRAGMA table_info(alignments)")
out["align_schema"] = [(r["name"], r["type"]) for r in c.fetchall()]

# reports dir listing
out["reports"] = sorted(os.listdir(REP))

print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
conn.close()
