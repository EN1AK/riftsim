# 只读探针：选定英雄/英雄区域的打出权限
import sqlite3

con = sqlite3.connect("file:workspace/rules_work.db?mode=ro", uri=True)
rows = con.execute(
    "SELECT rule_id, substr(proposed_canonical_rule,1,150) FROM rules"
    " WHERE proposed_canonical_rule LIKE '%英雄区%' AND rule_id LIKE 'R-CR-%'"
).fetchall()
print("## 英雄区:", len(rows))
for rid, txt in rows[:30]:
    print(" ", rid, "|", txt.replace("\n", " "))
con.close()
