"""Stage 3 3-ER spot checks: VEN-079 EN full text + mod-DIFF pairs zh/en NEW blocks."""
import sqlite3
import re

CDB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\cards_bilingual.db"
DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"

c1 = sqlite3.connect(CDB)
c1.row_factory = sqlite3.Row
r = c1.execute("SELECT card_key, name_en, text_en, text_cn FROM cards WHERE card_key='VEN-079'").fetchone()
print("VEN-079 EN text:", r["text_en"])
print("VEN-079 CN text:", r["text_cn"])

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

def new_block(t):
    m = re.search(r"\[新文本/NEW TEXT\]\s*\n(.*?)(?:\n▲|$)", t, re.S)
    return (m.group(1).strip() if m else "").replace("\n", " ")

pairs = [("EV-CN-ER-0001", "斥候标兵 艾娃"), ("EV-CN-ER-0069", "夜之锋刃"),
         ("EV-CN-ER-0074", "芮尔"), ("EV-CN-ER-0083", "菲兹")]
print("\n--- mod-DIFF pair NEW-text comparison ---")
for zid, name in pairs:
    z = c.execute("SELECT original_text FROM evidence WHERE evidence_id=?", (zid,)).fetchone()
    card = c.execute("SELECT card_ids FROM evidence WHERE evidence_id=?", (zid,)).fetchone()["card_ids"]
    e = c.execute(
        """SELECT evidence_id, original_text FROM evidence
           WHERE source_type='errata' AND source_language='en' AND card_ids=?""",
        (card,)).fetchone()
    # pick same-source-family en row already paired; for 0083 card is in source_020
    print("=" * 90)
    print(zid, name, card, "<->", e["evidence_id"] if e else "NONE")
    print("ZH NEW:", new_block(z["original_text"]))
    if e:
        print("EN NEW:", new_block(e["original_text"]))
conn.close()
