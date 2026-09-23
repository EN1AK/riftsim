import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")
MARK = " [2026-09-20 裁定关闭] "
for mid in ("MR-2C-0002","MR-2C-0003","MR-2D-0001","MR-2D-0002","MR-2D-0003","MR-2D-0011"):
    d = con.execute("SELECT issue_description FROM manual_review WHERE item_id=?", (mid,)).fetchone()[0]
    cnt = d.count(MARK)
    if cnt > 1:
        first = d.find(MARK)
        second = d.find(MARK, first + 1)
        # keep first closure block (until second occurrence), drop rest
        d2 = d[:second]
        con.execute("UPDATE manual_review SET issue_description=? WHERE item_id=?", (d2, mid))
        print(f"{mid}: deduped {cnt}->1")
    else:
        print(f"{mid}: closures={cnt} (ok)")
# sources notes dup check for ruling note
for sid in ("source_001","source_013","source_020"):
    n = con.execute("SELECT notes FROM sources WHERE source_id=?", (sid,)).fetchone()[0]
    c = n.count("Date ruling 2026-09-20")
    if c > 1:
        i = n.find("Date ruling 2026-09-20", n.find("Date ruling 2026-09-20") + 10)
        # drop from the second occurrence's preceding " | " to end of that ruling block? keep first: rebuild
        parts = n.split(" | Date ruling 2026-09-20")
        keep = parts[0] + " | Date ruling 2026-09-20" + parts[1].split(" | ")[0].join(["", ""]) \
            if False else None
        # simpler: keep everything before the second occurrence marker block
        idx = n.find(" | Date ruling 2026-09-20", n.find(" | Date ruling 2026-09-20") + 5)
        con.execute("UPDATE sources SET notes=? WHERE source_id=?", (n[:idx], sid))
        print(f"{sid}: notes deduped {c}->1")
    else:
        print(f"{sid}: ruling note count={c} (ok)")
con.commit()
print("--- final states ---")
for sid in ("source_001","source_006","source_008","source_013","source_014","source_016","source_019","source_020"):
    r = con.execute("SELECT date, effective_date, date_confidence FROM sources WHERE source_id=?", (sid,)).fetchone()
    print(f"{sid}: date={r[0]} eff={r[1]} conf={r[2]}")
con.close()
