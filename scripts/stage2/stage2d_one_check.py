import sqlite3
con = sqlite3.connect(r"workspace/rules_work.db")
r = con.execute(
    "SELECT evidence_id, faq_question, faq_answer, topic FROM evidence "
    "WHERE source_id='source_014' AND faq_question LIKE '%housekeeping%'").fetchone()
print(r[0] if r else "NOT FOUND")
if r:
    print("Q:", r[1][:160])
    print("A:", (r[2] or "<NULL/EMPTY>")[:200])
    print("topic:", r[3])
# 012 Accelerate as topic
r2 = con.execute(
    "SELECT COUNT(*), MIN(topic) FROM evidence WHERE source_id='source_012' AND topic='Accelerate'").fetchone()
print("012 topic=Accelerate items:", r2)
con.close()
