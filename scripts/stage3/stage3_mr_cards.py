"""Stage 3 closeout: fetch FAQ entries + card texts for MR-2D-0004/0005."""
import sqlite3

DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
CDB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\cards_bilingual.db"

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

for eid in ("EV-CN-FAQ-0195", "EV-CN-FAQ-0260"):
    r = c.execute("SELECT faq_question, faq_answer, notes FROM evidence WHERE evidence_id=?", (eid,)).fetchone()
    print("=" * 95)
    print(eid)
    print("Q:", (r["faq_question"] or "")[:500])
    print("A:", (r["faq_answer"] or "")[:700])
    print("NOTES:", (r["notes"] or "")[:250])
conn.close()

cards = sqlite3.connect(CDB)
cards.row_factory = sqlite3.Row
cc = cards.cursor()
print("\n===== card texts for MR cards =====")
for key in ("OGN-131", "OGN-251", "UNL-097", "UNL-177"):
    r = cc.execute("SELECT card_key, name_en, name_cn, text_en, text_cn FROM cards WHERE card_key=?", (key,)).fetchone()
    if r:
        print("=" * 80)
        print(r["card_key"], r["name_en"], "/", r["name_cn"])
        print("EN:", r["text_en"])
        print("CN:", r["text_cn"])
    else:
        print(key, "not found")
# Jinx 金克丝 search
cc.execute("SELECT card_key, name_en, name_cn, sub_title_cn FROM cards WHERE name_cn LIKE '%金克丝%' OR name_en LIKE '%Jinx%'")
for r in cc.fetchall():
    print("JINX-CAND:", dict(r))
cards.close()
