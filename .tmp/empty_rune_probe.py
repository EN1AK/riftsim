# 只读探针：检索"符文牌堆空/召出失败"相关 canonical
import sqlite3

con = sqlite3.connect("file:workspace/rules_work.db?mode=ro", uri=True)
cur = con.cursor()
keys = ["符文牌堆为空", "符文牌堆为 空", "没有符文", "无法召出", "燃尽", "符文牌堆顶"]
for k in keys:
    rows = cur.execute(
        "SELECT rule_id, substr(proposed_canonical_rule,1,140) FROM rules"
        " WHERE proposed_canonical_rule LIKE ? AND rule_id LIKE 'R-CR-%'",
        (f"%{k}%",),
    ).fetchall()
    print(f"## {k}: {len(rows)}")
    for rid, txt in rows[:12]:
        print(" ", rid, "|", txt.replace("\n", " "))
con.close()
