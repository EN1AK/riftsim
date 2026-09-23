import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")
r = con.execute("SELECT faq_answer FROM evidence WHERE evidence_id='EV-CN-FAQ-0307'").fetchone()
print("0307 FULL ANSWER:")
print(r[0])
print()
print("0308 keyword check:")
r2 = con.execute("SELECT faq_answer FROM evidence WHERE evidence_id='EV-CN-FAQ-0308'").fetchone()
print((r2[0] or "")[:500])
con.close()
