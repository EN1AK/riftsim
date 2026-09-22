"""Stage 3 pre-inspection: dump schema + key counts for planning. Read-only."""
import sqlite3
import json

DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

out = {}

# tables
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in c.fetchall()]
out["tables"] = tables

# schema for each table
schemas = {}
for t in tables:
    c.execute(f"PRAGMA table_info({t})")
    schemas[t] = [(r["name"], r["type"]) for r in c.fetchall()]
out["schemas"] = schemas

# counts
counts = {}
for t in tables:
    c.execute(f"SELECT COUNT(*) FROM {t}")
    counts[t] = c.fetchone()[0]
out["counts"] = counts

# evidence breakdown
c.execute("SELECT source_type, source_language, COUNT(*) FROM evidence GROUP BY source_type, source_language")
out["evidence_by_type_lang"] = [dict(r) for r in c.fetchall()]

# evidence columns sample (core rules)
c.execute("SELECT * FROM evidence LIMIT 1")
out["evidence_sample_keys"] = list(dict(c.fetchone()).keys()) if c.description else None

# sources
c.execute("SELECT source_id, source_document, source_type, language, version, date, effective_date FROM sources ORDER BY source_id")
out["sources"] = [dict(r) for r in c.fetchall()]

# manual_review: dump all rows (small table)
c.execute("SELECT * FROM manual_review")
mr = [dict(r) for r in c.fetchall()]
out["manual_review_rows"] = mr
out["manual_review_open"] = [r for r in mr if r.get("status") not in ("closed", "resolved")]

# alignments schema + any rows
if "alignments" in tables:
    c.execute("SELECT COUNT(*) FROM alignments")
    out["alignments_count"] = c.fetchone()[0]

# card_ids / related_cards population check
for col in ("card_ids", "related_cards"):
    if col in [n for n, _ in schemas.get("evidence", [])]:
        c.execute(f"SELECT COUNT(*) FROM evidence WHERE {col} IS NOT NULL AND {col} != ''")
        out[f"evidence_{col}_nonnull"] = c.fetchone()[0]

print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
conn.close()
