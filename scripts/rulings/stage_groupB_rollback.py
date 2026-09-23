import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")
for rid in ("EV-CN-ER-0081", "EV-CN-ER-0082"):
    r = con.execute("SELECT source_id, target_rule_candidate, notes FROM evidence WHERE evidence_id=?", (rid,)).fetchone()
    print(rid, r[0], r[1], "| tag present:", "zh_only_translation" in (r[2] or ""))
    if "zh_only_translation" in (r[2] or ""):
        import re
        new = re.sub(r" \| zh_only_translation \(ruled 2026-09-20[^|]*?(?=\s*\||$)", "", r[2])
        con.execute("UPDATE evidence SET notes=? WHERE evidence_id=?", (new, rid))
        print("   -> rolled back")
con.execute(
    "UPDATE manual_review SET issue_description=issue_description || ? WHERE item_id='MR-2C-0004' AND issue_description NOT LIKE '%0081%'",
    ("（补注：EV-CN-ER-0081/0082 为 source_010 破限勘误的德莱文/帝王神坛，按系列归属不在本裁定范围内，未标 zh_only。）",))
con.commit()
print("verify after rollback:")
for rid in ("EV-CN-ER-0051", "EV-CN-ER-0055", "EV-CN-ER-0081", "EV-CN-ER-0082"):
    r = con.execute("SELECT source_id, 'zh_only' IN (SELECT 'zh_only' ) FROM evidence WHERE evidence_id=?", (rid,)).fetchone()
    n = con.execute("SELECT notes FROM evidence WHERE evidence_id=?", (rid,)).fetchone()[0]
    print(rid, "tagged:", "zh_only_translation" in (n or ""))
con.close()
