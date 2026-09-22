import os, sqlite3, sys, datetime
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
p = r"workspace/rules_work.db"
print("db mtime:", datetime.datetime.fromtimestamp(os.path.getmtime(p)).isoformat())
con = sqlite3.connect(p)
SEQS = ["EV-CN-FAQ-0246","EV-CN-FAQ-0247","EV-CN-FAQ-0248","EV-CN-FAQ-0262","EV-CN-FAQ-0263",
        "EV-CN-FAQ-0264","EV-CN-FAQ-0169"]
for rid in SEQS:
    r = con.execute(
        "SELECT evidence_id,page,faq_question,faq_answer,notes FROM evidence WHERE evidence_id=?", (rid,)).fetchone()
    if not r:
        print(rid, "MISSING"); continue
    print(f"-- [{r[0]}] p{r[1]}")
    print("   Q:", (r[2] or "<NULL>")[:130].replace("\n", " / "))
    print("   A:", (r[3] or "<NULL>")[:130].replace("\n", " / "))
    print("   nrev:", "true" if '"needs_review": true' in r[4] else "false",
          "| manual_fix" if "manual_fix" in r[4] else "")
print()
print("stage2d rows:", con.execute("SELECT COUNT(*) FROM evidence WHERE notes LIKE '%stage2d faq%'").fetchone()[0])
print("nrev open:", con.execute("SELECT COUNT(*) FROM evidence WHERE notes LIKE '%stage2d faq%' AND notes LIKE '%\"needs_review\": true%'").fetchone()[0])
print("zh range:", con.execute("SELECT MIN(evidence_id), MAX(evidence_id), COUNT(DISTINCT evidence_id) FROM evidence WHERE evidence_id LIKE 'EV-CN-FAQ-%'").fetchone())
print("008 notes:", con.execute("SELECT notes FROM sources WHERE source_id='source_008'").fetchone()[0])
print("MR-2D-0014 tail:", con.execute("SELECT substr(issue_description,-180) FROM manual_review WHERE item_id='MR-2D-0014'").fetchone()[0])
con.close()
