import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")
for mid in ("MR-2C-0001", "MR-2C-0004"):
    r = con.execute("SELECT issue_description, conflicting_points, possible_explanation "
                    "FROM manual_review WHERE item_id=?", (mid,)).fetchone()
    print("=" * 78)
    print(mid)
    print("issue:", r[0])
    print("conflicting:", r[1])
    print("explanation:", r[2])
con.close()
