import sqlite3
con = sqlite3.connect(r"workspace/rules_work.db")
print("cols:", [r[1] for r in con.execute("PRAGMA table_info(evidence)")])
print("confidence values:", con.execute("SELECT DISTINCT confidence FROM evidence").fetchall())
print("evidence count:", con.execute("SELECT COUNT(*) FROM evidence").fetchone())
print("faq cols sample:", con.execute(
    "SELECT evidence_id, faq_question, faq_classification FROM evidence WHERE faq_question IS NOT NULL LIMIT 3"
).fetchall())
con.close()
