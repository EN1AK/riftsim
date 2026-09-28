"""Phase-1 tool: dump canonical zh (+ en reference) for an R-CR rule-number range.

Usage: python .tmp/dump_rules.py <lo> <hi> [--en]
Rule numbers compared on the integer prefix before the first dot.
"""
import sqlite3, sys

lo, hi = int(sys.argv[1]), int(sys.argv[2])
want_en = "--en" in sys.argv

con = sqlite3.connect("file:workspace/rules_work.db?mode=ro", uri=True)
cur = con.cursor()

rows = []
for rid, canon, oi, exc, ex in cur.execute(
    "SELECT rule_id, proposed_canonical_rule, official_interpretation, exception, example FROM rules WHERE rule_id LIKE 'R-CR-%' ORDER BY rule_id"
):
    num = rid.split("-", 2)[2].split(".")[0]
    if num.isdigit() and lo <= int(num) <= hi:
        rows.append((rid, canon, oi, exc, ex))

en_map = {}
if want_en:
    for eid, rid_cand, rnum, txt in cur.execute(
        "SELECT evidence_id, rule_id_candidate, rule_number, original_text FROM evidence WHERE evidence_id LIKE 'EV-EN-CR-%'"
    ):
        en_map[f"R-CR-{rnum}"] = txt

for rid, canon, oi, exc, ex in rows:
    print(f"### {rid}")
    if canon:
        print(canon.replace("\n", " "))
    else:
        print("<NULL canonical>")
    if want_en and rid in en_map:
        print(f"  [EN] {en_map[rid][:400]}")
    if exc:
        print(f"  [EXC] {exc[:300]}")
    if oi:
        print(f"  [OI] {oi[:200]}...")
    print()
print(f"TOTAL {len(rows)} rules", file=sys.stderr)
con.close()
