import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")
MARK = " [2026-09-20 复核完成] 4 条已全部人工复核并修复："
row = con.execute("SELECT issue_description FROM manual_review WHERE item_id='MR-2D-0014'").fetchone()
d = row[0]
first = d.find(MARK)
second = d.find(MARK, first + 1)
if second > 0:
    d = d[:second]
    con.execute("UPDATE manual_review SET issue_description=? WHERE item_id='MR-2D-0014'", (d,))
    con.commit()
    print("deduped")
print("final tail:", con.execute("SELECT substr(issue_description,-160) FROM manual_review WHERE item_id='MR-2D-0014'").fetchone()[0])
con.close()
