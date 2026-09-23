import sqlite3
import json
DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("""SELECT item_id, issue_description FROM manual_review WHERE item_id LIKE 'MR-2%'
             AND issue_description NOT LIKE '%关闭%' AND issue_description NOT LIKE '%结案%'
             AND issue_description NOT LIKE '%resolved%' AND issue_description NOT LIKE '%裁定%'""")
for r in c.fetchall():
    print(r["item_id"])
    print(r["issue_description"][:600])
conn.close()
