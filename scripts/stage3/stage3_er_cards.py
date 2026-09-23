"""Stage 3 3-ER: check card identities for unmatched ids in cards_bilingual.db."""
import sqlite3
import json

CDB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\cards_bilingual.db"
conn = sqlite3.connect(CDB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
out = {"tables": tables}
for t in tables:
    c.execute(f"PRAGMA table_info({t})")
    out[f"{t}_cols"] = [r["name"] for r in c.fetchall()]
    c.execute(f"SELECT COUNT(*) FROM {t}")
    out[f"{t}_n"] = c.fetchone()[0]

ids = ["FND-196", "FND-259", "OGN-121", "OGN-259", "OGN-002", "OGN-048", "OGN-146",
       "OGN-207", "OGN-122", "SFD-126", "VEN-079"]
# find a pk column heuristically
for t in tables:
    cols = out[f"{t}_cols"]
    pk = None
    for cand in ("card_key", "card_id", "id", "code", "collector_number", "key"):
        if cand in cols:
            pk = cand
            break
    rows_found = []
    if pk:
        q = f"SELECT * FROM {t} WHERE {pk} IN ({','.join('?'*len(ids))})"
        try:
            c.execute(q, ids)
            for r in c.fetchall():
                d = dict(r)
                rows_found.append({k: (v[:60] if isinstance(v, str) else v) for k, v in d.items()})
        except Exception as e:
            rows_found.append({"error": str(e)})
    out[f"{t}_matches"] = rows_found

print(json.dumps(out, ensure_ascii=False, indent=1))
conn.close()
