# -*- coding: utf-8 -*-
"""Stage 2C — Errata / Correction Evidence Extraction.

Parses the 8 errata txt sources (4 zh + 4 en) from repo-root `extracted/`,
extracts per-card errata entries anchored on [新文本]/[NEW TEXT] ... ▲ ... [旧文本]/[OLD TEXT],
and writes unified-schema evidence rows (plus errata-specific columns) into
workspace/rules_work.db.

Does NOT modify canonical rules / rules table. Cross-language reconciliation is
left to Stage 3. High-risk items are flagged into manual_review.
"""
import json
import re
import sqlite3
import sys
import difflib

DB = r"workspace/rules_work.db"
EXTRACTED = r"extracted"

SOURCES = [
    # (source_id, txt filename, language, source_type)
    ("source_002", r"loltcg_pdfs__02_2025-12-03_符文战场_勘误汇总_1028.txt", "zh", "errata"),
    ("source_003", r"loltcg_pdfs__03_2026-04-15_破限系列_勘误汇总_260403.txt", "zh", "errata"),
    ("source_004", r"loltcg_pdfs__04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.txt", "zh", "errata"),
    ("source_010", r"loltcg_pdfs__10_2026-07-24_9fe1f19110dd4678a6ad7bd96e791bba.txt", "zh", "errata"),
    ("source_013", r"riftbound_en_rules__02_2025-10-28_Origins_Errata.txt", "en", "errata"),
    ("source_015", r"riftbound_en_rules__04_2026-01-14_Spiritforged_Errata.txt", "en", "errata"),
    ("source_017", r"riftbound_en_rules__06_2026-04-03_Unleashed_Errata.txt", "en", "errata"),
    ("source_020", r"riftbound_en_rules__09_2026-07-23_Vendetta_Errata.txt", "en", "errata"),
]

# ---------- line classification ----------
PAGE_RE = re.compile(r"^===== PAGE (\d+) =====")
NEW_RE = re.compile(r"^\[(新文本|NEW TEXT)([^\]]*)\]")
OLD_RE = re.compile(r"^\[(旧文本|OLD TEXT)\]")
ZH_SECTION_RE = re.compile(r"^(“.+”.*(卡牌|勘误|优化)|翻译(勘误|优化))\s*$")
EN_SECTION_RE = re.compile(r"^(Origins|Spiritforged|Unleashed|Vendetta) Cards\s*$", re.I)
NOTE_ZH_RE = re.compile(r"^注：")
NOTE_EN_RE = re.compile(r"^Note:", re.I)
NOISE_EXACT = {
    "PRIVACY NOTICE", "TERMS OF SERVICE", "COOKIE PREFERENCES",
    "RELATED ARTICLES", "RULES AND RELEASES", "ANNOUNCEMENTS",
}
DATE_LINE_RE = re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$")
TRADEMARK_RE = re.compile(r"^©\s|^are trademarks", re.I)


def tokenize(lines, lang):
    """Yield (kind, text, page_no) tokens; blanks/pages tracked, noise skipped."""
    page = 0
    in_related = False  # after RELATED ARTICLES: all noise (EN site footer)
    for raw in lines:
        line = raw.rstrip().rstrip(" ").strip()
        m = PAGE_RE.match(line)
        if m:
            page = int(m.group(1))
            continue
        if not line:
            continue
        if lang == "en":
            if line in NOISE_EXACT:
                if line == "RELATED ARTICLES":
                    in_related = True
                continue
            if in_related:
                continue
            if TRADEMARK_RE.match(line) or DATE_LINE_RE.match(line):
                continue
        mn = NEW_RE.match(line)
        if mn:
            yield ("NEW", mn.group(2).strip(), page)  # suffix e.g. variant note
            continue
        if OLD_RE.match(line):
            yield ("OLD", "", page)
            continue
        if line == "▲":
            yield ("SEP", "", page)
            continue
        if (NOTE_ZH_RE.match(line) if lang == "zh" else NOTE_EN_RE.match(line)):
            yield ("NOTE", line, page)
            continue
        sec = (ZH_SECTION_RE.match(line) if lang == "zh" else EN_SECTION_RE.match(line))
        if sec:
            yield ("SECTION", line, page)
            continue
        yield ("TEXT", line, page)


def classify_modification(old, new, section, lang):
    """Heuristic modification_type (spec vocabulary)."""
    sec = section or ""
    if "翻译" in sec:  # 翻译勘误 / 翻译优化
        return "terminology_fix"
    digits = re.compile(r"[0-9０-９]+")
    punct = re.compile(r"[\s，。、；：,.;:()（）\-–—“”\"'’]+")
    o = punct.sub("", digits.sub("", old))
    n = punct.sub("", digits.sub("", new))
    if o == n and old.strip() != new.strip():
        return "numeric_change"
    ratio = difflib.SequenceMatcher(None, old.strip(), new.strip()).ratio()
    seq_new = ("进行一次" in new or "do this" in new.lower()) and (
        "进行一次" not in old and "do this" not in old.lower())
    if ratio >= 0.85:
        base = "partial_replacement"
    elif ratio < 0.5:
        base = "replacement"
    else:
        base = "condition_change"
    if seq_new and base in ("partial_replacement", "condition_change"):
        base = "effect_change"  # sequencing structure added -> effect-affecting
    return base


def parse_doc(path, lang):
    """Return (front_matter_lines, entries). Entry dict:
    card, section, page, new_text, old_text, raw, new_marker_note, notes[]"""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    toks = list(tokenize(lines, lang))
    entries, front = [], []
    state = "INIT"
    pending_name, pending_page = None, None
    cur_section = None
    cur = None

    def finalize():
        nonlocal cur
        if cur is None:
            return
        cur["new_text"] = "\n".join(cur["new_text"]).strip()
        cur["old_text"] = "\n".join(cur["old_text"]).strip()
        entries.append(cur)
        cur = None

    for i, (kind, text, page) in enumerate(toks):
        if kind == "NEW":
            finalize()
            cur = {
                "card": pending_name, "card_page": pending_page,
                "section": cur_section, "page": page, "marker_note": text,
                "notes": [], "new_text": [], "old_text": [],
            }
            pending_name, pending_page = None, None
            state = "NEW"
        elif kind == "SEP":
            state = "AWAIT_OLD"
        elif kind == "OLD":
            state = "OLD"
        elif kind == "NOTE":
            if cur is not None:
                cur["notes"].append(text)
                finalize()
                state = "INIT"
            else:
                front.append(text)
        elif kind == "SECTION":
            finalize()
            state = "INIT"
            cur_section = text
            pending_name = None
        elif kind == "TEXT":
            # A TEXT line directly followed by a NEW token is a card name,
            # regardless of current state (it also terminates the prior entry).
            nxt = toks[i + 1] if i + 1 < len(toks) else None
            is_name = nxt is not None and nxt[0] == "NEW"
            if is_name:
                finalize()
                state = "INIT"
                pending_name, pending_page = text, page
            elif state in ("NEW", "AWAIT_OLD"):
                if cur is not None:
                    cur["new_text"].append(text)
            elif state == "OLD":
                if cur is not None:
                    cur["old_text"].append(text)
            elif not entries and cur is None:
                front.append(text)
    finalize()
    reject = [e for e in entries if not e["card"] or not e["new_text"] or not e["old_text"]]
    return front, entries, reject


def main():
    con = sqlite3.connect(DB)
    con.execute("PRAGMA foreign_keys=ON")
    srows = {r[0]: r for r in con.execute(
        "SELECT source_id, source_document, version, date FROM sources")}
    stats = {"documents": 0, "evidence": 0, "mapped": 0, "unmapped": 0,
             "warnings": [], "per_doc": {}}
    reject_all = []
    id_counters = {"zh": 0, "en": 0}

    def next_id(lang):
        id_counters[lang] += 1
        p = "EV-CN-ER" if lang == "zh" else "EV-EN-ER"
        return f"{p}-{id_counters[lang]:04d}"

    import os
    for sid, fname, lang, stype in SOURCES:
        path = os.path.join(EXTRACTED, fname)
        front, entries, reject = parse_doc(path, lang)
        sdoc, sver, sdate = srows[sid][1], srows[sid][2], srows[sid][3]
        stats["documents"] += 1
        doc_stat = {"entries": len(entries), "mapped": 0, "unmapped": 0}
        if front and any(t.strip() for t in front):
            ev = next_id(lang)
            con.execute(
                "INSERT INTO evidence (evidence_id, topic, source_id, source_type, source_language,"
                " source_document, version, date, page, section, heading, original_text,"
                " normalized_summary, confidence, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (ev, "front_matter", sid, stype, lang, sdoc, sver, sdate, 1,
                 None, None, "\n".join(front).strip(),
                 "Errata document header / title block", "high",
                 "structural_extraction; stage2c errata doc header"))
            stats["evidence"] += 1
        for e in entries:
            card, new, old = e["card"], e["new_text"], e["old_text"]
            ok = bool(card) and bool(new) and bool(old)
            mod = classify_modification(old, new, e["section"], lang) if ok else "uncertain"
            scope = "card_text"
            if e["marker_note"]:  # e.g. zh010 '– 与目前卡面文本一致'
                e["notes"].append(f"marker: {e['marker_note']}")
                if "一致" in e["marker_note"]:
                    scope = "printed_text_alignment"
            if any("英文版" in n or "English version" in n for n in e["notes"]):
                scope = "english_card_text_only"
            conf = "high" if ok else "low"
            raw = (card or "<NO_CARD_NAME>") + "\n[新文本/NEW TEXT]\n" + new + \
                "\n▲\n[旧文本/OLD TEXT]\n" + old
            notes = ["structural_extraction; stage2c card errata",
                     "modification_type_source: heuristic"]
            notes += e["notes"]
            if not ok:
                notes.append("needs_review: missing card name or fragment")
            if e["card_page"] and e["card_page"] != e["page"]:
                notes.append(f"card name on page {e['card_page']}, text starts page {e['page']}")
            ev = next_id(lang)
            con.execute(
                "INSERT INTO evidence (evidence_id, rule_id_candidate, topic, source_id, source_type,"
                " source_language, source_document, version, date, page, section, original_text,"
                " normalized_summary, confidence, notes,"
                " target_rule_candidate, target_source, original_fragment, corrected_fragment,"
                " modification_type, effective_scope)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (ev, card, "card_errata", sid, stype, lang, sdoc, sver, sdate,
                 e["page"], e["section"], raw,
                 f"Errata: {card or '?'} — {mod}", conf, "; ".join(notes),
                 card, e["section"], old, new, mod, scope))
            stats["evidence"] += 1
            if ok:
                stats["mapped"] += 1
                doc_stat["mapped"] += 1
            else:
                stats["unmapped"] += 1
                doc_stat["unmapped"] += 1
                reject_all.append((sid, ev, card))
        stats["per_doc"][sid] = doc_stat

    # ---- needs_review / manual_review entries (document- and dataset-level) ----
    mr_items = [
        ("MR-2C-0001", None,
         "zh source_004 (铸魂淬炼勘误) contains 2 entries (沉没神庙, 遗忘丰碑) with no counterpart "
         "in EN source_015 (Spiritforged_Errata): cross-language errata coverage differs",
         "source_004", "source_015",
         "zh has 18 entries incl. 沉没神庙/遗忘丰碑; en has 16 without them",
         "zh-only correction entries (possibly translation-only or EN issued separately)",
         "cannot confirm EN-side status automatically; cross-language meaning check deferred to Stage 3"),
        ("MR-2C-0002", None,
         "source_013 (Origins_Errata): internal 'Last Updated: 2025-10-21' differs from filename date 2025-10-28",
         "source_013", "source_013",
         "document-internal date 2025-10-21 vs filename date 2025-10-28",
         "PDF last-updated stamp predates the 10-28 site release/packaging date",
         "date/version ambiguity flagged per Stage 2C rules; sources.date kept as filename date"),
        ("MR-2C-0003", None,
         "source_020 (Vendetta_Errata): article byline date 7/24/2026 differs from filename date 2026-07-23 "
         "(matches zh counterpart source_010 dated 2026-07-24)",
         "source_020", "source_010",
         "EN article date 2026-07-24 vs EN filename 2026-07-23; zh doc 2026-07-24",
         "timezone/packaging offset of one day",
         "date/version ambiguity flagged per Stage 2C rules; sources.date kept as filename date"),
        ("MR-2C-0004", None,
         "zh source_003 contains 13 zh-only 翻译勘误/翻译优化 entries (倾颓宫殿, 击退, 苍蓝雕纹魔像, 圣裁之刻, "
         "宏伟广场, 卡尔萨斯-永恒颂葬, 厄运小姐-海盗, 伊泽瑞尔-奥法逸才, 黛安娜, 兰博, 杰斯, 临终仪式, 蔚, 咂魂者, "
         "自适应机器人, plus 翻译优化 德莱文/暗巷神偷/奥恩的锻炉/帝王神坛): no EN errata counterparts",
         "source_003", None,
         "zh translation-correction sections have no EN parallel errata",
         "translation-only fixes cannot alter EN card text meaning",
         "cross-language equivalence must be verified in Stage 3; flagged per Stage 2C rules"),
    ]
    for item_id, rid, desc, sa, sb, cp, pe, cr in mr_items:
        con.execute(
            "INSERT OR REPLACE INTO manual_review (item_id, rule_id, issue_description, source_a,"
            " source_b, conflicting_points, possible_explanation, cannot_auto_resolve_reason)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (item_id, rid, desc, sa, sb, cp, pe, cr))
    stats["warnings"] = [
        "modification_type values are heuristic (not adjudicated); refine during Reconciliation",
        "cross-language entry mapping NOT attempted in Stage 2C (deferred to Stage 3); "
        "known anomaly: zh source_004 entries 沉没神庙/遗忘丰碑 lack EN counterpart (MR-2C-0001)",
        "source_013 internal date 2025-10-21 vs filename 2025-10-28 (MR-2C-0002)",
        "source_020 article date 2026-07-24 vs filename 2026-07-23 (MR-2C-0003)",
        "EN site-export documents (source_017/020) contained footer/sidebar noise; filtered during parse",
        "zh source_003 zh-only translation sections flagged (MR-2C-0004)",
        "note-marked entries '只有英文版文本不同/需要勘误' & 'Note: Text only differs for English version' "
        "assigned effective_scope=english_card_text_only",
        "zh source_010 entries marked '新文本与目前卡面文本一致' assigned effective_scope=printed_text_alignment",
    ]
    for sid, ev, card in reject_all:
        stats["warnings"].append(f"unmapped entry {ev} in {sid} (card={card!r}) -> needs_review")

    con.commit()
    with open("workspace/reports/stage2c_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in stats.items() if k != "warnings"}, ensure_ascii=False, indent=2))
    print("WARNINGS:", len(stats["warnings"]))
    con.close()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
