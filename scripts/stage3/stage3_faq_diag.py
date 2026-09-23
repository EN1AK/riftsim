"""Stage 3 3-FAQ diagnosis: show the 6 found candidates + why 005/007 pairs miss."""
import json
import sqlite3
import re

OUT = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\reports\stage3_faq_candidates.json"
d = json.load(open(OUT, encoding="utf-8"))

for k, v in d.items():
    print("####", k)
    for p in v["pairs"]:
        if p["cands"]:
            print(" ", p["zh"], p["q"][:60])
            for cd in p["cands"]:
                print("    ->", cd["en"], "score", cd["score"], cd["why"][:80])

DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("\n===== source_014 (en Spiritforged Patch Notes) non-null questions =====")
c.execute("""SELECT evidence_id, substr(faq_question,1,90) q, card_ids FROM evidence
             WHERE source_id='source_014' AND faq_question IS NOT NULL AND faq_question!='' ORDER BY evidence_id""")
for r in c.fetchall():
    print(r["evidence_id"], "|", r["q"].replace("\n", " "), "|", r["card_ids"])

print("\n===== source_005 (zh) questions =====")
c.execute("""SELECT evidence_id, substr(faq_question,1,80) q, related_cards FROM evidence
             WHERE source_id='source_005' AND faq_question IS NOT NULL AND faq_question!='' ORDER BY evidence_id""")
for r in c.fetchall():
    print(r["evidence_id"], "|", r["q"].replace("\n", " "), "|", (r["related_cards"] or "")[:60])
conn.close()
