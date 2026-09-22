# -*- coding: utf-8 -*-
import sqlite3, sys, re
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")

print("### FAQ 735.1.c 修订后文本 (EV-CN-FAQ-0055)")
r = con.execute("SELECT faq_answer FROM evidence WHERE evidence_id='EV-CN-FAQ-0055'").fetchone()
faq_txt = r[0] or ""
print(faq_txt[:600])

print()
print("### 核心规则 735.x (source_009)")
rows = con.execute(
    "SELECT evidence_id, rule_number, original_text FROM evidence WHERE source_id='source_009'"
    " AND rule_number LIKE '735%' ORDER BY rule_number").fetchall()
for rid, rn, txt in rows:
    print(f"-- {rid} {rn}")
    print((txt or "")[:400])

print()
print("### 对账")
def norm(s):
    s = re.sub(r"[\s　]+", "", s or "")
    return s.replace("“", '"').replace("”", '"')
faq_n = norm(faq_txt)
core_n = ""
for rid, rn, txt in rows:
    if rn == "735.1.c":
        core_n = norm(txt)
        print("core 735.1.c found:", rid)
        break
if not core_n:
    # try EN
    rows2 = con.execute(
        "SELECT evidence_id, rule_number, original_text FROM evidence WHERE source_id='source_018'"
        " AND rule_number LIKE '735%' ORDER BY rule_number").fetchall()
    for rid, rn, txt in rows2:
        print(f"-- EN {rid} {rn}: {(txt or '')[:200]}")
match = core_n and (core_n in faq_n or faq_n in core_n)
print("normalized match:", bool(match))
con.close()
