import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")
row = con.execute("SELECT issue_description FROM manual_review WHERE item_id='MR-2D-0010'").fetchone()
if "移交 Stage 3" not in (row[0] or ""):
    con.execute(
        "UPDATE manual_review SET issue_description=issue_description || ? WHERE item_id='MR-2D-0010'",
        (" [2026-09-20 移交 Stage 3] 012 未列出矛盾条目清单，无法在本阶段机械识别；按效力拓扑裁定，"
         "后发官方文档（012 Patch Notes，2025-10-24）效力高于先前 Origins FAQ。Stage 3 reconciliation 时"
         "以 012 文本为准比对 Origins FAQ/说明文，凡文本冲突处在被取代侧标 superseded。",))
    con.commit()
    print("deferred MR-2D-0010")
print("states:", con.execute(
    "SELECT CASE WHEN issue_description LIKE '%裁定关闭%' THEN 'CLOSED' WHEN issue_description LIKE '%复核完成%' THEN 'CLOSED'"
    " WHEN issue_description LIKE '%移交 Stage 3%' THEN 'DEFERRED' ELSE 'OPEN' END, COUNT(*)"
    " FROM manual_review GROUP BY 1").fetchall())
con.close()
