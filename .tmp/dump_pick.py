"""Pick exact rule_ids to dump: python .tmp/dump_pick.py R-CR-a R-CR-b ..."""
import sqlite3, sys

con = sqlite3.connect("file:workspace/rules_work.db?mode=ro", uri=True)
for rid in sys.argv[1:]:
    row = con.execute(
        "SELECT proposed_canonical_rule, exception FROM rules WHERE rule_id=?", (rid,)
    ).fetchone()
    if not row:
        print(f"### {rid} <NOT FOUND>"); continue
    canon, exc = row
    print(f"### {rid}")
    print((canon or "<NULL>").replace("\n", " "))
    if exc:
        print(f"  [EXC] {exc[:250]}")
    print()
con.close()
