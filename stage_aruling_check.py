import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")
for sid in ("source_001","source_006","source_008","source_013","source_014","source_016","source_019","source_020"):
    r = con.execute(
        "SELECT source_id, date, effective_date, date_confidence, version, notes FROM sources WHERE source_id=?",
        (sid,)).fetchone()
    print(r[0], "| date=", r[1], "| eff=", r[2], "| conf=", r[3], "| ver=", r[4])
# evidence date 现状
print()
for sid in ("source_001","source_006","source_008","source_013","source_014","source_016","source_019","source_020"):
    r = con.execute("SELECT COUNT(*), MIN(date), MAX(date) FROM evidence WHERE source_id=? GROUP BY source_id", (sid,)).fetchone()
    print(sid, "evidence rows:", r[0] if r else 0, "date in evidence:", (r[1], r[2]) if r else None)
con.close()
