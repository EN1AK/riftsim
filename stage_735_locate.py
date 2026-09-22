import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")
for src in ("source_009", "source_018"):
    rows = con.execute(
        "SELECT rule_number FROM evidence WHERE source_id=? AND rule_number LIKE '735.1%' ORDER BY rule_number",
        (src,)).fetchall()
    print(src, "735.1x rules:", [r[0] for r in rows])
rows = con.execute(
    "SELECT evidence_id, rule_number, substr(original_text,1,260) FROM evidence "
    "WHERE source_id='source_009' AND rule_number IN ('735.1.c','735.1','735.1.b','735.2') ORDER BY rule_number").fetchall()
for r in rows:
    print("--", r[0], r[1])
    print("  ", (r[2] or "").replace("\n", " / ")[:250])
con.close()
