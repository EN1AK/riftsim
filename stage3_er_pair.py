"""Stage 3 batch 3-ER step 1: mechanical zh-en errata pairing by card_id.

Outputs workspace/reports/stage3_er_pairs.json with:
- pairs: candidate zh<->en pairs (shared card_id) + heuristics, for model review
- unmatched_zh / unmatched_en: rows without cross-language counterpart
No DB writes (decisions applied by a later step with item-level commits).
"""
import sqlite3
import json
import re

DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
OUT = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\reports\stage3_er_pairs.json"

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

def load(lang):
    c.execute(
        """SELECT evidence_id, source_id, page, target_rule_candidate,
                  original_fragment, corrected_fragment, modification_type,
                  card_ids, related_cards, date, original_text, notes
           FROM evidence
           WHERE source_type='errata' AND source_language=? AND card_ids IS NOT NULL AND card_ids != ''
           ORDER BY evidence_id""",
        (lang,),
    )
    rows = []
    for r in c.fetchall():
        d = dict(r)
        try:
            d["_card_ids"] = json.loads(d["card_ids"])
        except Exception:
            d["_card_ids"] = []
        d["_key"] = d["_card_ids"][0] if d["_card_ids"] else None
        rows.append(d)
    return rows

def split_blocks(text):
    """Split errata original_text into NEW/OLD fragments (bilingual markers kept in both docs)."""
    if not text:
        return None, None
    m_new = re.search(r"\[新文本/NEW TEXT\]\s*\n(.*?)(?:\n▲|$)", text, re.S)
    m_old = re.search(r"\[旧文本/OLD TEXT\]\s*\n(.*)$", text, re.S)
    new = m_new.group(1).strip() if m_new else None
    old = m_old.group(1).strip() if m_old else None
    return new, old

def compact(s, n=600):
    if s is None:
        return None
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1] + "…"

zh = load("zh")
en = load("en")

en_by_key = {}
for r in en:
    en_by_key.setdefault(r["_key"], []).append(r)

pairs = []
unmatched_zh = []
used_en = set()
for z in zh:
    cands = en_by_key.get(z["_key"], [])
    if not cands:
        unmatched_zh.append(z)
        continue
    # if multiple en candidates for same card_id, pick same-set doc proximity (rare); mark extras
    e = cands[0]
    if len(cands) > 1:
        z.setdefault("_multi_en", [c["evidence_id"] for c in cands])
    used_en.add(e["evidence_id"])
    z_new, z_old = split_blocks(z["original_text"])
    e_new, e_old = split_blocks(e["original_text"])
    pairs.append(
        {
            "card_id": z["_key"],
            "extra_card_ids": z["_card_ids"][1:] + e["_card_ids"][1:],
            "zh_evidence": z["evidence_id"],
            "en_evidence": e["evidence_id"],
            "zh_source": z["source_id"],
            "en_source": e["source_id"],
            "zh_date": z["date"],
            "en_date": e["date"],
            "zh_target": z["target_rule_candidate"],
            "en_target": e["target_rule_candidate"],
            "zh_mod_type": z["modification_type"],
            "en_mod_type": e["modification_type"],
            "zh_new": compact(z_new),
            "en_new": compact(e_new),
            "zh_old": compact(z_old, 250),
            "en_old": compact(e_old, 250),
            "zh_notes": z["notes"],
            "en_notes": e["notes"],
        }
    )

unmatched_en = [r for r in en if r["evidence_id"] not in used_en]

def brief(rows):
    return [
        {
            "evidence_id": r["evidence_id"],
            "source_id": r["source_id"],
            "card_id": r["_key"],
            "target": r["target_rule_candidate"],
            "mod_type": r["modification_type"],
            "date": r["date"],
            "zh_only_tag": "zh_only" in (r["notes"] or ""),
            "notes": r["notes"],
        }
        for r in rows
    ]

out = {
    "counts": {
        "zh_items": len(zh),
        "en_items": len(en),
        "pairs": len(pairs),
        "unmatched_zh": len(unmatched_zh),
        "unmatched_en": len(unmatched_en),
    },
    "pairs": pairs,
    "unmatched_zh": brief(unmatched_zh),
    "unmatched_en": brief(unmatched_en),
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print(json.dumps(out["counts"], ensure_ascii=False))
print("unmatched_zh:", [r["evidence_id"] for r in out["unmatched_zh"]])
print("unmatched_en:", [r["evidence_id"] for r in out["unmatched_en"]])
conn.close()
