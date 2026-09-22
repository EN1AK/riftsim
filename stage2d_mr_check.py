import sqlite3
con = sqlite3.connect(r"workspace/rules_work.db")
rows = con.execute("SELECT item_id, substr(issue_description,1,60) FROM manual_review ORDER BY item_id").fetchall()
for r in rows:
    print(r[0], "|", r[1])
print("total:", len(rows))
con.close()
