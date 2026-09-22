"""Probe 2: RCC notes patterns + resolution state via reconciliation/changes cross-ref."""
import json, sqlite3
from collections import Counter, defaultdict

DB = "workspace/rules_work.db"
OUT = "workspace/checkpoints/stage4b_b006_rcc_notes.json"
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()

cur.execute("""
SELECT re.rule_id, re.evidence_id, re.notes, e.source_id
FROM rule_evidence re JOIN evidence e ON e.evidence_id=re.evidence_id
WHERE re.relationship='faq:rule_change_candidate'
""")
rows = [dict(r) for r in cur.fetchall()]

# which changes rows reference these evidence in final_conclusion/reason?
def resolved(rid, evid):
    cur.execute("SELECT change_id FROM changes WHERE rule_id=? AND (reason LIKE ? OR final_conclusion LIKE ?)",
                (rid, f"%{evid}%", f"%{evid}%"))
    ch = cur.fetchall()
    cur.execute("SELECT reconciliation_id FROM reconciliations WHERE rule_id=? AND (original_fragment LIKE ? OR corrected_fragment LIKE ?)",
                (rid, f"%{evid}%", f"%{evid}%"))
    rc = cur.fetchall()
    return [x[0] for x in ch], [x[0] for x in rc]

note_patterns = Counter()
unresolved = []
resolved_list = []
for r in rows:
    rid, evid = r["rule_id"], r["evidence_id"]
    n = (r["notes"] or "").strip()
    note_patterns[n[:60]] += 1
    ch, rc = resolved(rid, evid)
    if ch or rc:
        resolved_list.append({"rule_id": rid, "evidence_id": evid, "changes": ch, "recs": rc, "notes": n[:120]})
    else:
        unresolved.append({"rule_id": rid, "evidence_id": evid, "source_id": r["source_id"], "notes": n[:160]})

by_bucket = defaultdict(list)
for u in unresolved:
    rid = u["rule_id"]
    if rid.startswith("R-TOPIC-CN"): b = "R-TOPIC-CN"
    elif rid.startswith("R-TOPIC-EN"): b = "R-TOPIC-EN"
    elif rid.startswith("R-CARD"): b = "R-CARD"
    elif rid.startswith("R-MISC"): b = "R-MISC"
    elif rid.startswith("R-CR"): b = "R-CR"
    else: b = rid
    by_bucket[b].append(f'{u["evidence_id"]}({u["source_id"]})')

out = {
    "total_rcc": len(rows),
    "resolved": len(resolved_list),
    "unresolved": len(unresolved),
    "note_patterns": {k: v for k, v in note_patterns.most_common()},
    "unresolved_by_bucket": {k: v for k, v in by_bucket.items()},
    "resolved_list": resolved_list,
    "unresolved_list": unresolved,
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("total:", len(rows), "resolved:", len(resolved_list), "unresolved:", len(unresolved))
print("note patterns:")
for k, v in note_patterns.most_common():
    print(f"  {v:3d}  {k!r}")
print("unresolved by bucket: { %s }" % ", ".join(f"{k}:{len(v)}" for k, v in by_bucket.items()))
