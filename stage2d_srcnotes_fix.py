import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")
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
    parts = []
    if sid in KEEP:
        parts.append(KEEP[sid])
    parts.append(f"Stage2D: extracted {cnt} FAQ/OE items ({lo}..{hi}), needs_review={nrev}")
    con.execute("UPDATE sources SET notes=? WHERE source_id=?", (" | ".join(parts), sid))
con.commit()
for r in con.execute("SELECT source_id, notes FROM sources WHERE notes LIKE '%Stage2D: extracted%' ORDER BY source_id"):
    print(r[0], "|", r[1])
con.close()
