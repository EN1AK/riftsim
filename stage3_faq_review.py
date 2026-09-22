"""Stage 3 3-FAQ: review found candidates + rule-ref pass for 007/011 vs 016/019."""
import sqlite3
import json
import re

DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

def show(eids):
    c.execute(f"""SELECT evidence_id, faq_question, faq_answer FROM evidence
                  WHERE evidence_id IN ({','.join('?'*len(eids))})""", eids)
    for r in c.fetchall():
        print("=" * 95)
        print(r["evidence_id"])
        print("Q:", (r["faq_question"] or "")[:400])
        print("A:", (r["faq_answer"] or "")[:400])

print("##### C1: zh 0005-0008 <-> en OE-0059 (Baited Hook timing) #####")
show(["EV-EN-OE-0059"])
show(["EV-CN-FAQ-0006"])
print("(0005/0007/0008 same card theme as 0006)")

print("\n##### C2: zh 0316 <-> en 0263 #####")
show(["EV-CN-FAQ-0316", "EV-EN-OE-0263"])
print("\n##### C3: zh 0324 <-> en 0265 #####")
show(["EV-CN-FAQ-0324", "EV-EN-OE-0265"])

# rule-ref pass: extract rule numbers from en 016/019 blobs and zh 007/011 refs
def refs(t):
    return set(re.findall(r"\b(\d{3}(?:\.\d+[a-z]?){0,3})\b", t or ""))

print("\n##### rule-ref cross-match zh 007/011 vs en 016/019 #####")
for zs, es in (("source_007", "source_016"), ("source_011", "source_019")):
    en = {}
    c.execute("""SELECT evidence_id, faq_question, faq_answer FROM evidence
                 WHERE source_id=? AND faq_question IS NOT NULL""", (es,))
    for r in c.fetchall():
        refs_e = refs((r["faq_question"] or "") + " " + (r["faq_answer"] or ""))
        en[r["evidence_id"]] = refs_e
    c.execute("""SELECT evidence_id, faq_question, rule_id_candidate, notes FROM evidence
                 WHERE source_id=? AND faq_question IS NOT NULL""", (zs,))
    matches = 0
    for r in c.fetchall():
        zrefs = refs(r["rule_id_candidate"]) | refs(r["notes"]) | refs(r["faq_question"])
        hits = [(eid, sorted(zrefs & er)) for eid, er in en.items() if zrefs & er]
        if hits:
            matches += 1
            print(r["evidence_id"], (r["faq_question"] or "")[:40].replace("\n", " "),
                  "->", [(h[0], h[1][:4]) for h in hits[:3]])
    print(zs, "items with rule-ref overlap:", matches)
conn.close()
