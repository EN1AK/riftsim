import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")
con.execute(
    "UPDATE evidence SET notes=notes || ? WHERE evidence_id IN ('EV-EN-OE-0109','EV-EN-OE-0110')",
    (" | audit note 2026-09-20: intentional duplicate in source doc (lines 101 & 103; official "
     "'Repeat' keyword joke), NOT an extraction error",))
con.commit()
print("annotated:", con.total_changes)
con.close()
