# -*- coding: utf-8 -*-
"""Stage 2A finalize: verify fixed state, sync processing_tasks.json."""
import sqlite3, json, datetime, os

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WS = os.path.join(BASE, "workspace")
con = sqlite3.connect(os.path.join(WS, "rules_work.db"))
cur = con.cursor()

checks = {}
checks["section_samples"] = [list(r) for r in cur.execute(
    "SELECT rule_number, topic, section FROM evidence WHERE source_id='source_009' AND rule_number IN ('102','199','200','201','300','356','400','700','821','829')")]
checks["notes_200_400"] = [list(r) for r in cur.execute(
    "SELECT rule_number, notes FROM evidence WHERE source_id='source_009' AND rule_number IN ('200','400')")]
checks["task_status"] = [list(r) for r in cur.execute(
    "SELECT status, COUNT(*) FROM processing_tasks GROUP BY status")]
checks["tasks_009_chunks"] = [list(r) for r in cur.execute(
    "SELECT task_id, page_start, page_end, status FROM processing_tasks WHERE source_id='source_009' ORDER BY task_id")]
checks["front_matter"] = list(cur.execute(
    "SELECT original_text FROM evidence WHERE evidence_id='EV-CN-CR-0000'").fetchone())
checks["evidence_009"] = cur.execute("SELECT COUNT(*) FROM evidence WHERE source_id='source_009'").fetchone()[0]
checks["semantic_cols_all_null"] = cur.execute(
    "SELECT COUNT(*) FROM evidence WHERE source_id='source_009' AND (trigger IS NOT NULL OR precondition IS NOT NULL OR effect IS NOT NULL OR restriction IS NOT NULL OR exception IS NOT NULL OR example IS NOT NULL OR normalized_summary IS NOT NULL)").fetchone()[0]

# sync processing_tasks.json from DB
rows = cur.execute(
    "SELECT task_id, source_id, page_start, page_end, section, status, assigned_role, notes FROM processing_tasks ORDER BY task_id").fetchall()
tasks = [dict(zip(["task_id", "source_id", "page_start", "page_end", "section", "status", "assigned_role", "notes"], r)) for r in rows]
summary = {}
for t in tasks:
    summary[t["status"]] = summary.get(t["status"], 0) + 1
with open(os.path.join(WS, "processing_tasks.json"), "w", encoding="utf-8") as f:
    json.dump({"tasks": tasks, "last_updated": datetime.datetime.now().isoformat(),
               "total_count": len(tasks), "status_summary": summary}, f, ensure_ascii=False, indent=2)
checks["json_synced_tasks"] = len(tasks)
con.close()
print(json.dumps(checks, ensure_ascii=False, indent=2))
