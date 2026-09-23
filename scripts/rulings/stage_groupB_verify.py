import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")
n1 = con.execute("SELECT COUNT(*) FROM evidence WHERE notes LIKE '%cross_ref_errata%' AND notes LIKE '%stage2d faq%'").fetchone()[0]
n2 = con.execute("SELECT COUNT(*) FROM evidence WHERE notes LIKE '%cross_ref_faq%' AND evidence_id LIKE 'EV-CN-ER-%'").fetchone()[0]
print("FAQ side cross_ref_errata:", n1, "| 2C side cross_ref_faq:", n2)
nt = con.execute("SELECT COUNT(*) FROM evidence WHERE notes LIKE '%zh_only_translation%'").fetchone()[0]
print("zh_only_translation tagged:", nt)
r = con.execute("SELECT notes FROM evidence WHERE evidence_id='EV-CN-FAQ-0277'").fetchone()[0]
print("0277 tail:", r[-160:])
r = con.execute("SELECT notes FROM evidence WHERE evidence_id='EV-CN-FAQ-0053'").fetchone()[0]
print("0053 tail:", r[-120:])
con.close()
