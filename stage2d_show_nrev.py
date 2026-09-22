import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")
for rid in ("EV-CN-FAQ-0169", "EV-CN-FAQ-0248", "EV-CN-FAQ-0263", "EV-CN-FAQ-0264"):
    r = con.execute(
        "SELECT evidence_id, page, faq_classification, faq_question, faq_answer FROM evidence "
        "WHERE evidence_id=?", (rid,)).fetchone()
    print("=" * 76)
    print(f"[{r[0]}] page={r[1]} cls={r[2]}")
    print("--- 原问题 faq_question ---")
    print(r[3])
    print("--- 原回答 faq_answer ---")
    print((r[4] or "<NULL/EMPTY>")[:1200])
con.close()
