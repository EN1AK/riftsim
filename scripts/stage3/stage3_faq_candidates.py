"""Stage 3 3-FAQ: candidate pair generation per doc pair.

Signals per zh item vs en item (same doc pair):
- shared rule-number refs (zh rule_id_candidate / notes related_rule_refs vs en question+answer rule numbers)
- shared cards (zh card_ids vs en card_ids, plus EN-text mentions of en card names mapped from zh related_cards)
Output: workspace/reports/stage3_faq_candidates.json (compact, top-3 per zh).
"""
import sqlite3
import json
import re

DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
CDB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\cards_bilingual.db"
OUT = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\reports\stage3_faq_candidates.json"

DOC_PAIRS = [
    ("source_001", "source_012"),  # 2025-10-23/24 Core Rules era
    ("source_005", "source_014"),  # Spiritforged
    ("source_007", "source_016"),  # Unleashed
    ("source_011", "source_019"),  # Vendetta
]

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

cards = sqlite3.connect(CDB)
cards.row_factory = sqlite3.Row
cc = cards.cursor()
cc.execute("SELECT card_key, name_en, name_cn FROM cards WHERE name_en IS NOT NULL AND name_cn IS NOT NULL")
en_by_cn = {}
for r in cc.fetchall():
    en_by_cn.setdefault(r["name_cn"], set()).add(r["name_en"].lower())

def rule_refs(texts):
    out = set()
    for t in texts:
        if not t:
            continue
        for m in re.finditer(r"\b(\d{3}(?:\.\d+[a-z]?)*)\b", t):
            out.add(m.group(1))
    return out

def load(source_id):
    c.execute("""SELECT evidence_id, source_id, faq_question, faq_answer, rule_id_candidate,
                        card_ids, related_cards, notes, topic
                 FROM evidence WHERE source_id=? AND faq_question IS NOT NULL AND faq_question != ''
                 ORDER BY evidence_id""", (source_id,))
    rows = []
    for r in c.fetchall():
        d = dict(r)
        d["_rule_refs"] = rule_refs([d["rule_id_candidate"], d["notes"], d["faq_question"]])
        d["_cards"] = set(json.loads(d["card_ids"]) if d["card_ids"] else [])
        try:
            d["_rel_cards"] = set(json.loads(d["related_cards"]) if d["related_cards"] else [])
        except Exception:
            d["_rel_cards"] = set()
        # zh: map related card cn names to en names for text matching
        en_names = set()
        for cn in d["_rel_cards"]:
            for en in en_by_cn.get(cn, set()):
                en_names.add(en.split(",")[0].strip())
        d["_en_names"] = en_names
        rows.append(d)
    return rows

result = {}
for zs, es in DOC_PAIRS:
    zh = load(zs)
    en = load(es)
    # en index: text blob for card-name matching
    for e in en:
        e["_blob"] = ((e["faq_question"] or "") + " " + (e["faq_answer"] or "")).lower()
    pairs = []
    unmatched = []
    for z in zh:
        cands = []
        for e in en:
            score = 0
            why = []
            shared_rules = z["_rule_refs"] & e["_rule_refs"]
            if shared_rules:
                score += 3 * len(shared_rules)
                why.append("rules:" + ",".join(sorted(shared_rules))[:60])
            shared_ids = z["_cards"] & e["_cards"]
            if shared_ids:
                score += 2 * len(shared_ids)
                why.append("card_ids:" + ",".join(sorted(shared_ids)))
            if z["_en_names"]:
                hit = [n for n in z["_en_names"] if n and n in e["_blob"]]
                if hit:
                    score += 2 * len(hit)
                    why.append("card_names:" + ",".join(hit)[:60])
            if score >= 3:
                cands.append({"en": e["evidence_id"], "score": score, "why": "; ".join(why)})
        cands.sort(key=lambda x: -x["score"])
        entry = {
            "zh": z["evidence_id"],
            "q": (z["faq_question"] or "")[:70].replace("\n", " "),
            "cards": sorted(z["_cards"])[:4],
            "rules": sorted(z["_rule_refs"])[:6],
            "cands": cands[:3],
        }
        pairs.append(entry)
        if not cands:
            unmatched.append(z["evidence_id"])
    result[f"{zs}<->{es}"] = {
        "zh_items": len(zh), "en_items": len(en),
        "with_cand": sum(1 for p in pairs if p["cands"]),
        "pairs": pairs,
    }
    print(zs, "<->", es, "| zh", len(zh), "en", len(en),
          "| with candidates:", sum(1 for p in pairs if p["cands"]), "| unmatched zh:", len(unmatched))

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
conn.close()
