# -*- coding: utf-8 -*-
"""Stage 2D finalize: fix processing_tasks status, update sources.notes, progress.json."""
import json, sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

con = sqlite3.connect(r"workspace/rules_work.db")
SIDS = ["source_001","source_005","source_006","source_007","source_008","source_011",
        "source_012","source_014","source_016","source_019"]

tot = 0
for sid in SIDS:
    num = sid.split("_")[1]
    cnt, nrev = con.execute(
        "SELECT COUNT(*), SUM(CASE WHEN notes LIKE '%\"needs_review\": true%' THEN 1 ELSE 0 END) "
        "FROM evidence WHERE source_id=? AND notes LIKE '%stage2d faq%' "
        "AND (topic IS NULL OR topic<>'front_matter')",
        (sid,)).fetchone()
    first_id, last_id = con.execute(
        "SELECT MIN(evidence_id), MAX(evidence_id) FROM evidence WHERE source_id=? "
        "AND notes LIKE '%stage2d faq%'", (sid,)).fetchone()
    tot += cnt
    con.execute(
        "UPDATE processing_tasks SET status='completed',"
        " notes=COALESCE(notes,'') || ? WHERE task_id LIKE ?",
        (f" | Stage2D: extracted {cnt} items + 1 front_matter ({first_id}..{last_id};"
         f" needs_review={nrev or 0})", f"task_{num}%"))
    con.execute(
        "UPDATE sources SET notes=TRIM(COALESCE(notes,'') || ?) WHERE source_id=?",
        (f" | Stage2D: extracted {cnt} FAQ/OE items ({first_id}..{last_id}),"
         f" needs_review={nrev or 0}", sid))
    print(f"{sid}: task_*_{num} completed, items={cnt}, ids={first_id}..{last_id}")
con.commit()
print("tasks now pending:",
      con.execute("SELECT COUNT(*) FROM processing_tasks WHERE status='pending'").fetchone()[0])
print("total 2D items:", tot)
con.close()

# progress.json
pj = json.load(open(r"workspace/progress.json", encoding="utf-8"))
pj["current_stage"] = "Stage 2D COMPLETE -> next: Stage 3 (Entity Resolution; awaiting instruction)"
pj["stages"]["stage_2d"] = {
    "status": "completed",
    "description": ("FAQ / Ruling / Official Explanation Extraction completed: 595 items + 10 "
                    "front_matter from 10 docs (zh 327 items: 001=50, 005=47, 006=93, 007=23, "
                    "008=80, 011=34; en 268 items: 012=86, 014=45, 016=75, 019=62); "
                    "classification example_only=193 rule_interpretation=270 exception=5 "
                    "rule_change_candidate=127; 4 needs_review; MR-2D-0001..0015; "
                    "report: workspace/reports/stage2d_faq_extraction.md")
}
pj["last_updated"] = "2026-09-20"
json.dump(pj, open(r"workspace/progress.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("progress.json updated")
