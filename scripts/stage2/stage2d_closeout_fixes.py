# -*- coding: utf-8 -*-
"""Close out manual fixes detected in rules_work.db; renumber; sync metadata."""
import json, re, sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

con = sqlite3.connect(r"workspace/rules_work.db")

# 1. verify the three external fixes are final-state correct
checks = {
    "0169 A1 prefix": ("SELECT faq_answer FROM evidence WHERE evidence_id='EV-CN-FAQ-0169'",
                       lambda r: r and r[0] and r[0].lstrip().startswith("A1：")),
    "0247 merged": ("SELECT faq_question FROM evidence WHERE evidence_id='EV-CN-FAQ-0247'",
                    lambda r: r and "1）" in (r[0] or "") and "4）" in (r[0] or "")),
    "0248 deleted": ("SELECT COUNT(*) FROM evidence WHERE evidence_id='EV-CN-FAQ-0248'",
                     lambda r: r and r[0] == 0),
    "0264 stripped": ("SELECT faq_answer FROM evidence WHERE evidence_id='EV-CN-FAQ-0264'",
                      lambda r: r and "中娅沙漏" not in (r[0] or "")),
    "0265 prefixed": ("SELECT faq_question FROM evidence WHERE evidence_id='EV-CN-FAQ-0265'",
                      lambda r: r and (r[0] or "").startswith("我方基地中有【中娅沙漏】。")),
}
for name, (sql, ok) in checks.items():
    r = con.execute(sql).fetchone()
    print(f"check {name}: {'OK' if ok(r) else 'FAIL -> ' + str(r)}")

# 2. close 0263 (structure verified correct in human review)
con.execute(
    "UPDATE evidence SET notes=REPLACE(notes,'\"needs_review\": true','\"needs_review\": false')"
    " || ' | manual_review 2026-09-20: bare Q/A fracture merge verified correct'"
    " WHERE evidence_id='EV-CN-FAQ-0263' AND notes LIKE '%\"needs_review\": true%'")
print("0263 closed:", con.total_changes)

# 3. renumber (idempotent; closes the 0248 hole)
PLANS = [
    ("EV-CN-FAQ", ["source_001","source_005","source_006","source_007","source_008","source_011"]),
    ("EV-EN-OE", ["source_012","source_014","source_016","source_019"]),
]
for pref, sids in PLANS:
    rows = []
    for sid in sids:
        rows += [r[0] for r in con.execute(
            "SELECT evidence_id FROM evidence WHERE source_id=? AND notes LIKE '%stage2d faq%' "
            "ORDER BY evidence_id", (sid,))]
    for i, rid in enumerate(rows, 1):
        new = f"{pref}-{i:04d}"
        if rid != new:
            con.execute("UPDATE evidence SET evidence_id=? WHERE evidence_id=?", (new, rid))
    print(pref, "renumbered:", len(rows))

# annotate the merged-entry note that embedded ids are pre-renumber references
con.execute(
    "UPDATE evidence SET notes=notes || ? WHERE notes LIKE '%manual_fix%'",
    (" (note: evidence ids cited in manual_fix entries are pre-renumber references)",))

# 4. refresh sources.notes with final counts/ranges
KEEP = {
    "source_011": "Stage2A: content verified = 化神争锋系列 官方FAQ",
    "source_012": "Stage2D: reclassified rule->official_explanation (content = Core Rules Patch Notes, same class as source_014/016/019)",
}
for sid in ("source_001","source_005","source_006","source_007","source_008","source_011",
            "source_012","source_014","source_016","source_019"):
    cnt = con.execute(
        "SELECT COUNT(*) FROM evidence WHERE source_id=? AND notes LIKE '%stage2d faq%' "
        "AND (topic IS NULL OR topic<>'front_matter')", (sid,)).fetchone()[0]
    nrev = con.execute(
        "SELECT COUNT(*) FROM evidence WHERE source_id=? AND notes LIKE '%stage2d faq%' "
        "AND (topic IS NULL OR topic<>'front_matter') AND notes LIKE '%\"needs_review\": true%'",
        (sid,)).fetchone()[0]
    lo, hi = con.execute(
        "SELECT MIN(evidence_id), MAX(evidence_id) FROM evidence WHERE source_id=? "
        "AND notes LIKE '%stage2d faq%'", (sid,)).fetchone()
    parts = [KEEP[sid]] if sid in KEEP else []
    parts.append(f"Stage2D: extracted {cnt} FAQ/OE items ({lo}..{hi}), needs_review={nrev}")
    con.execute("UPDATE sources SET notes=? WHERE source_id=?", (" | ".join(parts), sid))

# 5. MR-2D-0014 update with resolution
con.execute(
    "UPDATE manual_review SET issue_description=issue_description || ? WHERE item_id='MR-2D-0014'",
    (" [2026-09-20 复核完成] 4 条已全部人工复核并修复：0248 并入 0247（1)-4) 共享问答合并，"
     "原编号 0248 已删除并重排）、0169 补 A1： 前缀、0264 尾行剥移 0265、0263 结构复核合格；"
     "needs_review 清零。",))

# 6. task notes recount for source_008 (items 80->79)
con.execute(
    "UPDATE processing_tasks SET notes=REPLACE(notes,'extracted 80 items','extracted 79 items "
    "(0248 merged into 0247 post-review)') WHERE task_id LIKE 'task_008%'")
con.commit()

# 7. progress.json totals
pj = json.load(open(r"workspace/progress.json", encoding="utf-8"))
d = pj["stages"]["stage_2d"]["description"]
d = d.replace("595 items + 10", "594 items + 10 (post-review: 0248 merged into 0247)")
d = d.replace("008=80", "008=79")
d = d.replace("4 needs_review", "0 needs_review (4 resolved 2026-09-20)")
pj["stages"]["stage_2d"]["description"] = d
pj["last_updated"] = "2026-09-20"
json.dump(pj, open(r"workspace/progress.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# 8. stats json recount
stats = json.load(open(r"workspace/reports/stage2d_stats.json", encoding="utf-8"))
nrev_total = con.execute(
    "SELECT COUNT(*) FROM evidence WHERE notes LIKE '%stage2d faq%' "
    "AND notes LIKE '%\"needs_review\": true%'").fetchone()[0]
item_total = con.execute(
    "SELECT COUNT(*) FROM evidence WHERE notes LIKE '%stage2d faq%' "
    "AND (topic IS NULL OR topic<>'front_matter')").fetchone()[0]
s8 = con.execute(
    "SELECT COUNT(*) FROM evidence WHERE source_id='source_008' AND notes LIKE '%stage2d faq%' "
    "AND (topic IS NULL OR topic<>'front_matter')").fetchone()[0]
stats["totals"]["items"] = item_total
stats["totals"]["needs_review"] = nrev_total
stats["sources"]["source_008"]["items"] = s8
stats["sources"]["source_008"]["needs_review"] = 0
stats["post_review_note"] = ("2026-09-20: human review resolved all 4 needs_review; "
                             "EV-CN-FAQ-0248 merged into 0247 and deleted; ids renumbered.")
json.dump(stats, open(r"workspace/reports/stage2d_stats.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

print("evidence total:", con.execute("SELECT COUNT(*) FROM evidence").fetchone()[0])
print("stage2d items:", item_total, "needs_review:", nrev_total)
con.close()
print("done")
