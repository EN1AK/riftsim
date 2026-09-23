import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")

print("### 0307/0308 fracture state")
r = con.execute("SELECT substr(faq_answer,-160) FROM evidence WHERE evidence_id='EV-CN-FAQ-0307'").fetchone()
print("0307 answer tail:", (r[0] or "").replace("\n", " / "))
r = con.execute("SELECT substr(faq_question,1,80) FROM evidence WHERE evidence_id='EV-CN-FAQ-0308'").fetchone()
print("0308 q head:", (r[0] or "").replace("\n", " / "))

print()
print("### markers")
for rid, key in (("EV-CN-FAQ-0089","superseded_by"), ("EV-CN-FAQ-0090","superseded_by"),
                 ("EV-CN-FAQ-0307","supersedes"), ("EV-CN-FAQ-0055","incorporated_into"),
                 ("EV-CN-FAQ-0195","cross_language_note"), ("EV-CN-FAQ-0260","pending_zh_text_update")):
    n = con.execute("SELECT notes FROM evidence WHERE evidence_id=?", (rid,)).fetchone()[0] or ""
    print(f"  {rid} {key}:", "OK" if key in n else "MISSING")

print()
print("### closure texts (tails)")
for mid in ("MR-2D-0006","MR-2D-0007","MR-2D-0009","MR-2D-0012","MR-2D-0013","MR-2D-0015","MR-2D-0004","MR-2D-0005"):
    r = con.execute("SELECT substr(issue_description,-130) FROM manual_review WHERE item_id=?", (mid,)).fetchone()
    print(f"  {mid}: ...{(r[0] or '')[-130:]}")
con.close()
