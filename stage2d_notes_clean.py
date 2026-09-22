import re, sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")
pat = re.compile(r"( \| Stage2D: extracted [^|]+)+$", re.S)
n = 0
for tbl in ("sources", "processing_tasks"):
    idcol = "source_id" if tbl == "sources" else "task_id"
    for rid, notes in con.execute(f"SELECT {idcol}, notes FROM {tbl} WHERE notes LIKE '%Stage2D: extracted%'"):
        cleaned, cnt = pat.subn("", notes)
        if cnt:
            # re-append a single correct entry
            new = newentry = None
            if tbl == "sources":
                m = rid
                items = con.execute(
                    "SELECT COUNT(*) FROM evidence WHERE source_id=? AND notes LIKE '%stage2d faq%' "
                    "AND (topic IS NULL OR topic<>'front_matter')", (rid,)).fetchone()[0]
                new = cleaned + f" | Stage2D: extracted {items} FAQ/OE items"
            else:
                new = cleaned + " | Stage2D: completed"
            con.execute(f"UPDATE {tbl} SET notes=? WHERE {idcol}=?", (new, rid))
            n += 1
con.commit()
print("cleaned:", n)
for r in con.execute("SELECT task_id, notes FROM processing_tasks WHERE notes LIKE '%Stage2D%' ORDER BY task_id"):
    print(r[0], "|", r[1][-120:])
con.close()
