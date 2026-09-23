import sqlite3
import json
DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("SELECT * FROM manual_review WHERE item_id IN ('MR-2D-0004','MR-2D-0005','MR-2D-0010')")
for r in c.fetchall():
    print(json.dumps(dict(r), ensure_ascii=False, indent=1))
conn.close()
