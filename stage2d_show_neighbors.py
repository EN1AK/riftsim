import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")
for rid in ("EV-CN-FAQ-0245","EV-CN-FAQ-0246","EV-CN-FAQ-0247","EV-CN-FAQ-0248","EV-CN-FAQ-0249","EV-CN-FAQ-0264","EV-CN-FAQ-0265"):
    r = con.execute(
        "SELECT evidence_id,page,topic,faq_question,faq_answer FROM evidence WHERE evidence_id=?", (rid,)).fetchone()
    if not r:
        print(rid, "MISSING"); continue
    print("=" * 72)
    print(f"[{r[0]}] p{r[1]} topic={r[2]}")
    print("Q:", (r[3] or "<NULL>")[:300].replace("\n", " / "))
    print("A:", (r[4] or "<NULL>")[:300].replace("\n", " / "))
con.close()
