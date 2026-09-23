"""Stage 3 3-ER: verify remaining 6 mod-DIFF pairs by card-id-intersection pairing."""
import sqlite3
import json
import re

DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

def new_block(t):
    m = re.search(r"\[新文本/NEW TEXT\]\s*\n(.*?)(?:\n▲|$)", t, re.S)
    return (m.group(1).strip() if m else "").replace("\n", " ")

def old_block(t):
    m = re.search(r"\[旧文本/OLD TEXT\]\s*\n(.*)$", t, re.S)
    return (m.group(1).strip() if m else "").replace("\n", " ")

# en pairing by source family: zh002->013, zh003->017/020(excluded), zh004->015, zh010->020
zh_ids = ["EV-CN-ER-0002", "EV-CN-ER-0004", "EV-CN-ER-0005",
          "EV-CN-ER-0017", "EV-CN-ER-0021", "EV-CN-ER-0031"]
for zid in zh_ids:
    z = c.execute("SELECT evidence_id, source_id, card_ids, original_text FROM evidence WHERE evidence_id=?", (zid,)).fetchone()
    ids = json.loads(z["card_ids"])
    qmarks = ",".join("?" * len(ids))
    ens = c.execute(
        f"""SELECT evidence_id, source_id, original_text FROM evidence
            WHERE source_type='errata' AND source_language='en' AND source_id='source_013'
              AND EXISTS (SELECT 1 FROM json_each(evidence.card_ids) je WHERE je.value IN ({qmarks}))""",
        ids).fetchall()
    print("=" * 90)
    print(zid, z["card_ids"])
    print("ZH NEW:", new_block(z["original_text"]))
    print("ZH OLD:", old_block(z["original_text"]))
    for e in ens:
        print(e["evidence_id"], e["source_id"])
        print("EN NEW:", new_block(e["original_text"]))
        print("EN OLD:", old_block(e["original_text"]))
conn.close()
