import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")
print("processing_tasks total:", con.execute("SELECT COUNT(*) FROM processing_tasks").fetchone()[0])
print("status dist:", con.execute(
    "SELECT status, COUNT(*) FROM processing_tasks GROUP BY status").fetchall())
print("evidence total:", con.execute("SELECT COUNT(*) FROM evidence").fetchone()[0])
print("stage2d rows:", con.execute(
    "SELECT COUNT(*) FROM evidence WHERE notes LIKE '%stage2d faq%'").fetchone()[0])
print("manual_review:", con.execute("SELECT COUNT(*) FROM manual_review").fetchone()[0])
# completion criteria per spec: pending=0, running=0, failed=0
bad = con.execute(
    "SELECT COUNT(*) FROM processing_tasks WHERE status IN ('pending','running','failed')").fetchone()[0]
print("2D completion criteria (pending+running+failed==0):", "PASS" if bad == 0 else f"FAIL({bad})")
# id spot: first/last per prefix
for pref in ("EV-CN-FAQ", "EV-EN-OE"):
    print(pref, con.execute(
        "SELECT MIN(evidence_id), MAX(evidence_id), COUNT(*) FROM evidence WHERE evidence_id LIKE ?",
        (pref + "-%",)).fetchone())
con.close()
