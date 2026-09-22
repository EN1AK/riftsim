import sqlite3
import json
DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("PRAGMA table_info(processing_tasks)")
print([r["name"] for r in c.fetchall()])
c.execute("""UPDATE processing_tasks SET status='completed',
             notes='Stage 3 batch 3-ER done: 63 zh-en errata alignments AL-ER-0001..0063 (relation=equivalent, high); 30 zh-only rows unmatched explicitly + zh_only tags (incl. 0059..0062 newly confirmed zh_only_translation, 0089/0090/0091/0092/0093 source_010 wording fixes; 0093 corrected mistranslated targeting restriction); 3 EN front_matter N/A; report workspace/reports/stage3_er_alignment.md'
             WHERE task_id='task_3_03'""")
conn.commit()
c.execute("SELECT task_id, status FROM processing_tasks WHERE task_id='task_3_03'")
print(dict(c.fetchone()))
conn.close()
