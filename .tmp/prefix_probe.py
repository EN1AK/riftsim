# 只读探针：列出非 R-CR/R-TOPIC/R-CARD 前缀的规则
import sqlite3

con = sqlite3.connect("file:workspace/rules_work.db?mode=ro", uri=True)
for r in con.execute(
    "SELECT rule_id, topic FROM rules WHERE rule_id NOT LIKE 'R-CR-%'"
    " AND rule_id NOT LIKE 'R-TOPIC-%' AND rule_id NOT LIKE 'R-CARD-%'"
):
    print(r[0], "|", r[1])
con.close()
