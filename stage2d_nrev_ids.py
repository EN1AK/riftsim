import sqlite3
con = sqlite3.connect(r"workspace/rules_work.db")
for r in con.execute(
        "SELECT evidence_id, source_id, substr(faq_question,1,50) FROM evidence "
        "WHERE notes LIKE '%stage2d faq%' AND notes LIKE '%\"needs_review\": true%' ORDER BY evidence_id"):
    print(r[0], r[1], "|", r[2].replace("\n", " /"))
con.close()
