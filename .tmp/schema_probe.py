# 只读探针：确认 rules_work.db 中规则与来源的连接结构，供生成器取 source 字段
import sqlite3

con = sqlite3.connect("file:workspace/rules_work.db?mode=ro", uri=True)
con.row_factory = sqlite3.Row
cur = con.cursor()

print("== tables ==")
for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    print(r["name"])

for t in ("rules", "rule_evidence", "evidence", "sources"):
    print(f"\n== schema: {t} ==")
    try:
        for r in cur.execute(f"PRAGMA table_info({t})"):
            print(dict(r))
    except sqlite3.Error as e:
        print("ERR", e)

print("\n== rules row sample ==")
for r in cur.execute("SELECT * FROM rules WHERE rule_id IN ('R-CR-315.1','R-CR-801.3.a.1') LIMIT 2"):
    print(dict(r))

print("\n== rule_evidence sample (R-CR-315.1) ==")
try:
    for r in cur.execute("SELECT * FROM rule_evidence WHERE rule_id='R-CR-315.1'"):
        print(dict(r))
except sqlite3.Error as e:
    print("ERR", e)

print("\n== evidence sample ==")
try:
    row = cur.execute("SELECT * FROM evidence LIMIT 1").fetchone()
    if row:
        d = dict(row)
        for k, v in d.items():
            s = str(v)
            print(k, "=", s[:120].replace("\n", " "))
except sqlite3.Error as e:
    print("ERR", e)

print("\n== sources sample ==")
try:
    for r in cur.execute("SELECT * FROM sources LIMIT 3"):
        print(dict(r))
except sqlite3.Error as e:
    print("ERR", e)

con.close()
