import sqlite3
con = sqlite3.connect(r"workspace/rules_work.db")
for r in con.execute(
        "SELECT source_id, source_type, language, version, date, effective_date, notes FROM sources "
        "WHERE source_id IN ('source_001','source_005','source_006','source_007','source_008','source_011',"
        "'source_012','source_014','source_016','source_019') ORDER BY source_id"):
    print(r[0], "| type=", r[1], "| lang=", r[2], "| ver=", r[3], "| date=", r[4], "| eff=", r[5])
    print("   notes:", (r[6] or "")[:150])
print()
print("tasks:", con.execute(
    "SELECT task_id, status, substr(notes,-60) FROM processing_tasks "
    "WHERE task_id LIKE 'task_001%' OR task_id LIKE 'task_005%' OR task_id LIKE 'task_006%' "
    "OR task_id LIKE 'task_007%' OR task_id LIKE 'task_008%' OR task_id LIKE 'task_011%' "
    "OR task_id LIKE 'task_012%' OR task_id LIKE 'task_014%' OR task_id LIKE 'task_016%' "
    "OR task_id LIKE 'task_019%' ORDER BY task_id").fetchall())
con.close()
