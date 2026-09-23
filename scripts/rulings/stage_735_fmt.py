import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")
# how are sub-rules numbered in core rules evidence?
rows = con.execute(
    "SELECT DISTINCT rule_number FROM evidence WHERE source_id='source_009' AND rule_number LIKE '735%'").fetchall()
print("009 735x:", rows)
rows = con.execute("SELECT rule_number FROM evidence WHERE source_id='source_009' AND rule_number LIKE '187%' ORDER BY 1").fetchall()
print("009 187x sample:", rows[:15])
rows = con.execute("SELECT rule_number FROM evidence WHERE source_id='source_009' AND rule_number LIKE '%.%' LIMIT 12").fetchall()
print("009 dotted sample:", rows)
rows = con.execute(
    "SELECT evidence_id, rule_number, substr(original_text,1,200) FROM evidence WHERE source_id='source_009' AND original_text LIKE '%法盾值%' LIMIT 5").fetchall()
for r in rows:
    print("FADUN:", r[0], r[1], "|", (r[2] or "").replace("\n"," / "))
con.close()
