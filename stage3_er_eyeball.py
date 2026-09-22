"""Stage 3 3-ER: one-line NEW-text eyeball for the 47 not-yet-verified family pairs."""
import sqlite3
import json
import re

DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

def new_block(t):
    m = re.search(r"\[新文本/NEW TEXT\]\s*\n(.*?)(?:\n▲|$)", t, re.S)
    return re.sub(r"\s+", " ", (m.group(1).strip() if m else ""))

verified = {"EV-CN-ER-0001", "EV-CN-ER-0002", "EV-CN-ER-0004", "EV-CN-ER-0005",
            "EV-CN-ER-0017", "EV-CN-ER-0021", "EV-CN-ER-0031",
            "EV-CN-ER-0069", "EV-CN-ER-0074", "EV-CN-ER-0083", "EV-CN-ER-0084",
            "EV-CN-ER-0022", "EV-CN-ER-0034"}

fam = {"source_002": "source_013", "source_003": "source_017",
       "source_004": "source_015", "source_010": "source_020"}

c.execute("""SELECT evidence_id, source_id, card_ids, original_text FROM evidence
             WHERE source_type='errata' AND source_language='zh' ORDER BY evidence_id""")
rows = [r for r in c.fetchall() if r["source_id"] in fam]

for z in rows:
    if z["evidence_id"] in verified:
        continue
    ids = json.loads(z["card_ids"]) if z["card_ids"] else []
    if not ids:
        continue
    qmarks = ",".join("?" * len(ids))
    e = c.execute(
        f"""SELECT evidence_id, original_text FROM evidence
            WHERE source_type='errata' AND source_language='en' AND source_id=?
              AND EXISTS (SELECT 1 FROM json_each(evidence.card_ids) je WHERE je.value IN ({qmarks}))""",
        [fam[z["source_id"]], *ids]).fetchone()
    if not e:
        print(z["evidence_id"], "NO-EN-CANDIDATE", z["card_ids"])
        continue
    print(f"{z['evidence_id'][-4:]}~{e['evidence_id'][-4:]} {ids[0]}")
    print(" Z:", new_block(z["original_text"])[:240])
    print(" E:", new_block(e["original_text"])[:240])
conn.close()
