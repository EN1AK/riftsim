import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")
for r in con.execute(
        "SELECT item_id, rule_id, issue_description FROM manual_review ORDER BY item_id"):
    resolved = "2026-09-20 复核完成" in (r[2] or "")
    print(f"[{'CLOSED' if resolved else 'OPEN'}] {r[0]} rule={r[1] or '-'}")
    print("   ", (r[2] or "")[:110].replace("\n", " "))
con.close()
