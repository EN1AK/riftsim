import os, sqlite3, sys, datetime
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
p = r"workspace/rules_work.db"
print("db mtime:", datetime.datetime.fromtimestamp(os.path.getmtime(p)).isoformat())
con = sqlite3.connect(p)
print("evidence total:", con.execute("SELECT COUNT(*) FROM evidence").fetchone()[0])
print("stage2d rows:", con.execute("SELECT COUNT(*) FROM evidence WHERE notes LIKE '%stage2d faq%'").fetchone()[0])
print("needs_review rows:")
for r in con.execute(
        "SELECT evidence_id, source_id, substr(faq_question,1,40) FROM evidence "
        "WHERE notes LIKE '%stage2d faq%' AND notes LIKE '%\"needs_review\": true%' ORDER BY evidence_id"):
    print("  ", r[0], r[1], r[2].replace("\n", " /"))
r = con.execute(
    "SELECT faq_answer FROM evidence WHERE evidence_id='EV-CN-FAQ-0169'").fetchone()
print("0169 answer head:", (r[0] or "")[:120] if r else "MISSING")
r2 = con.execute(
    "SELECT notes FROM evidence WHERE evidence_id='EV-CN-FAQ-0247'").fetchone()
print("0247 notes:", r2[0][:300] if r2 else "MISSING")
print("0248 exists:", con.execute("SELECT COUNT(*) FROM evidence WHERE evidence_id='EV-CN-FAQ-0248'").fetchone()[0])
con.close()
