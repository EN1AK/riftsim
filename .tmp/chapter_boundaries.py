# 只读探针：列出每个整数主编号下的规则数与首条规则的 canonical/标题，用于校准 covers 区间
import re
import sqlite3

con = sqlite3.connect("file:workspace/rules_work.db?mode=ro", uri=True)
con.row_factory = sqlite3.Row
cur = con.cursor()

rows = cur.execute(
    "SELECT rule_id, topic, proposed_canonical_rule FROM rules WHERE rule_id LIKE 'R-CR-%' ORDER BY rule_id"
).fetchall()

def key(rid: str):
    # R-CR-315.1.a -> (315, depth, rid)
    rest = rid.split("-", 2)[2]
    parts = rest.split(".")
    try:
        main = int(parts[0]) if parts[0].isdigit() else parts[0]
    except ValueError:
        main = parts[0]
    return main

from collections import defaultdict

groups = defaultdict(list)
for r in rows:
    m = key(r["rule_id"])
    groups[m].append(r)

def sort_key(k):
    return (0, k) if isinstance(k, int) else (1, 0)

for m in sorted(groups, key=sort_key):
    rs = groups[m]
    first = rs[0]
    canon = (first["proposed_canonical_rule"] or "")[:40].replace("\n", " ")
    topic = (first["topic"] or "")[:50]
    print(f"{m}\t{len(rs)}\t{topic}\t{canon}")

con.close()
