import sqlite3
con = sqlite3.connect(r"workspace/rules_work.db")
for r in con.execute(
        "SELECT source_id, notes FROM sources WHERE source_id IN "
        "('source_001','source_005','source_006','source_007','source_008','source_011',"
        "'source_012','source_014','source_016','source_019') ORDER BY source_id"):
    print(r[0], "|", (r[1] or "<NULL>")[:200])
con.close()
