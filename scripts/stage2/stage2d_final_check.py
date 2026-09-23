import sqlite3
con = sqlite3.connect(r"workspace/rules_work.db")
r = con.execute(
    "SELECT evidence_id, page, faq_question, faq_answer FROM evidence WHERE source_id='source_001'"
    " AND faq_question LIKE '%搜魔人典狱长%'").fetchone()
print("搜魔人:", r[0], "p", r[1])
print("Q:", r[2][:110].replace("\n"," /"))
print("A:", (r[3] or "")[:110].replace("\n"," /"))
# 总数 + 分类 + needs_review 汇总
print(con.execute("SELECT COUNT(*) FROM evidence WHERE notes LIKE '%stage2d faq%'").fetchone())
print(con.execute("SELECT faq_classification, COUNT(*) FROM evidence WHERE notes LIKE '%stage2d faq%' AND faq_classification IS NOT NULL GROUP BY 1").fetchall())
con.close()
