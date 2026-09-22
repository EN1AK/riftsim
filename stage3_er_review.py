"""Stage 3 3-ER: compact review table of 66 pairs + unmatched details.

Prints per-pair decision-relevant signals only (no big fragments):
- sources/dates, mod_type zh vs en, target match, multi-en flag, zh_only tags
- fragment first-line comparison signal (first heading line of NEW block)
"""
import json
import re

P = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\reports\stage3_er_pairs.json"
d = json.load(open(P, encoding="utf-8"))

rows = []
for p in d["pairs"]:
    zm, em = p["zh_mod_type"], p["en_mod_type"]
    zt, et = (p["zh_target"] or "").strip(), (p["en_target"] or "").strip()
    zh_only = "zh_only" in (p.get("zh_notes") or "")
    zn = (p["zh_new"] or "")[:80].replace("\n", " ")
    en = (p["en_new"] or "")[:80].replace("\n", " ")
    rows.append({
        "zh": p["zh_evidence"], "en": p["en_evidence"], "card": p["card_id"],
        "zs": p["zh_source"], "es": p["en_source"],
        "zd": p["zh_date"], "ed": p["en_date"],
        "mod": f"{zm}/{em}" + (" !DIFF" if zm != em else ""),
        "tgt": "ok" if (zt and et and zt.replace(" ", "") == et.replace(" ", "")) else f"zh:{zt[:40]}|en:{et[:40]}",
        "zOnly": zh_only,
        "multi": bool(p.get("extra_card_ids")) or "multi" in json.dumps(p),
        "zn": zn, "en": en,
    })

print("pairs:", len(rows))
for r in rows:
    flag = ""
    if "!DIFF" in r["mod"] or r["tgt"] != "ok" or r["zOnly"] or r["zd"] != r["ed"]:
        flag = " <<CHECK"
    print(f"{r['zh'][-4:]}<->{r['en'][-4:]} {r['card']:10s} {r['zs'][7:]}vs{r['es'][7:]} "
          f"{str(r['zd'])}vs{str(r['ed'])} mod={r['mod']:42s} tgt={r['tgt'][:60]:60s} z1={r['zOnly']}{flag}")

print("\n--- unmatched_zh detail (21 expected zh-only translation fixes; others?) ---")
for r in d["unmatched_zh"]:
    print(r["evidence_id"], r["source_id"], r["card_id"], r["mod_type"], r["date"],
          "zh_only" if r["zh_only_tag"] else "<<NOT-TAGGED", (r["notes"] or "")[:90])

print("\n--- unmatched_en detail ---")
for r in d["unmatched_en"]:
    print(r["evidence_id"], r["source_id"], r["card_id"], r["mod_type"], r["date"], (r["notes"] or "")[:90])
