# -*- coding: utf-8 -*-
"""Register task_4b_06 as completed in processing_tasks (idempotent)."""
import json, sqlite3
con = sqlite3.connect("workspace/rules_work.db")
con.row_factory = sqlite3.Row

cols = [c[1] for c in con.execute("PRAGMA table_info(processing_tasks)")]
sample = dict(con.execute("SELECT * FROM processing_tasks WHERE task_id='task_4b_05'").fetchone())
print("cols:", cols)
print("sample task_4b_05:", json.dumps(sample, ensure_ascii=False))

row = {k: None for k in cols}
if "task_id" in cols: row["task_id"] = "task_4b_06"
if "stage" in cols: row["stage"] = "4B"
if "substage" in cols: row["substage"] = "tier3_topic_misc_front_rcc"
if "source_id" in cols: row["source_id"] = None
if "batch_id" in cols: row["batch_id"] = "4B-B006"
if "status" in cols: row["status"] = "completed"
if "started_at" in cols: row["started_at"] = "2026-09-22"
if "completed_at" in cols: row["completed_at"] = "2026-09-22"
if "attempt_count" in cols: row["attempt_count"] = 1
if "checkpoint_ref" in cols: row["checkpoint_ref"] = "workspace/checkpoints/stage4b_b006_checkpoint.json"
if "notes" in cols: row["notes"] = ("88 pending rules reconciled (81 R-TOPIC / 5 R-MISC / 2 front); "
    "128 RCC links adjudicated: 37 source_019 applied (CHG rows), 90 transitional not-applied, "
    "1 incorporated (EV-CN-FAQ-0055->809.1.c); 11 R-CARD RCC links on reconciled cards + 4 MR-2D-0005 watch cards folded in; "
    "report workspace/reports/stage4b_b006_topic_misc_front.md; script stage4b_b006_reconcile.py")
if "assigned_role" in cols: row["assigned_role"] = None
if "page_start" in cols: row["page_start"] = None
if "page_end" in cols: row["page_end"] = None
if "section" in cols: row["section"] = None
if "item_id" in cols: row["item_id"] = None
if "failure_reason" in cols: row["failure_reason"] = None

# match 4b_0x row conventions (section=substage, source_id='multi', assigned_role='agent')
row2 = {"task_id": "task_4b_06", "source_id": "multi", "page_start": None, "page_end": None,
        "section": "stage4b_tier3_topic_misc_front_rcc", "status": "completed",
        "assigned_role": "agent",
        "notes": json.dumps({"rules_reconciled": 88, "interp_attached": 156, "rcc_total": 128,
            "rcc_applied_019": 37, "rcc_transitional": 90, "rcc_incorporated": 1,
            "changes_written": 38, "rec_rows": 100, "card_rcc_rules": 8, "watch_cards": 4,
            "nv_true_added": 58, "errors": 0,
            "warnings": ["EV-CN-FAQ-0260 not linked to R-CARD-OGN-251"]}, ensure_ascii=False)}
con.execute("DELETE FROM processing_tasks WHERE task_id='task_4b_06'")
con.execute("INSERT INTO processing_tasks({}) VALUES({})".format(
    ",".join(cols), ",".join("?" * len(cols))), [row2[c] for c in cols])
con.commit()
n = con.execute("SELECT COUNT(*) FROM processing_tasks WHERE task_id='task_4b_06' AND status='completed'").fetchone()[0]
print("inserted:", n)
