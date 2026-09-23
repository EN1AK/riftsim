# -*- coding: utf-8 -*-
"""
Stage 2A: Chinese Core Rules Evidence Extraction
- Fix/populate `sources` table from source_manifest.json + real page counts
- Rebuild processing_tasks queue (chunked by real page counts)
- Parse CN Core Rules (source_009) -> evidence table (verbatim original_text, page, rule_number)
Structural extraction only: no semantic fields, no canonical decisions.
"""
import os, re, json, sqlite3, datetime, sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WS = os.path.join(BASE, "workspace")
EX = os.path.join(BASE, "extracted")
DB = os.path.join(WS, "rules_work.db")
MANIFEST = os.path.join(WS, "source_manifest.json")

PAGE_RE = re.compile(r"^===== PAGE (\d+) =====$")
RULE_RE = re.compile(r"^(\d{3}(?:\.[A-Za-z0-9]+)*\.)\s*(.*)$")
TOP_SECTION_RE = re.compile(r"^\d00$")

# ---------- source_id -> extracted file mapping ----------
def extracted_map():
    m = {}
    for fn in os.listdir(EX):
        if not fn.endswith(".txt"):
            continue
        stem = fn[:-4]
        folder, doc = stem.split("__", 1)
        m[doc] = fn
    return m

def page_count(path):
    mx = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            pm = PAGE_RE.match(line.strip())
            if pm:
                mx = max(mx, int(pm.group(1)))
    return mx

def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    report = {}

    with open(MANIFEST, encoding="utf-8") as f:
        manifest = json.load(f)

    emap = extracted_map()
    now = datetime.datetime.now().isoformat()

    # ---------- 1. populate & fix sources ----------
    fixes = []
    for s in manifest["sources"]:
        doc = s["source_document"]
        fn = emap.get(doc)
        pc = page_count(os.path.join(EX, fn)) if fn else 0
        lang = "zh" if doc in emap and emap[doc].startswith("loltcg_pdfs__") else \
               "en" if doc in emap and emap[doc].startswith("riftbound_en_rules__") else s["language"]
        stype = s["source_type"]
        sdate, dconf, notes = s["date"], s["date_confidence"], s.get("notes", "")
        # content-verified corrections
        if s["source_id"] == "source_009":
            stype, lang = "rule", "zh"
            sdate, dconf = "2026-07-17", "confirmed"
            notes = (notes + " | Stage2A: content verified = 《符文战场》核心规则 CN; "
                     "doc self-states last update 2026-07-17 (filename date 2026-07-23)").strip(" |")
            fixes.append("source_009 -> rule/zh, date 2026-07-17 confirmed")
        elif s["source_id"] == "source_010":
            stype, lang = "errata", "zh"
            notes = (notes + " | Stage2A: content verified = 卡牌新旧文本勘误 (铸魂淬炼/破限)").strip(" |")
            fixes.append("source_010 -> errata/zh")
        elif s["source_id"] == "source_011":
            stype, lang = "faq", "zh"
            notes = (notes + " | Stage2A: content verified = 化神争锋系列 官方FAQ").strip(" |")
            fixes.append("source_011 -> faq/zh")
        counterpart = s["possible_counterpart"]
        if s["source_id"] == "source_009":
            counterpart = "source_018"
        if s["source_id"] == "source_018":
            counterpart = "source_009"
        cur.execute(
            """INSERT OR REPLACE INTO sources
               (source_id, source_document, source_type, language, version, date,
                effective_date, page_count, supersedes, possible_counterpart,
                date_confidence, version_confidence, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (s["source_id"], doc, stype, lang, s["version"], sdate,
             s["effective_date"], pc, s["supersedes"], counterpart,
             dconf, s["version_confidence"], notes))
        # write corrections back to manifest
        s.update(source_type=stype, language=lang, page_count=pc,
                 date=sdate, date_confidence=dconf, notes=notes,
                 possible_counterpart=counterpart)
    manifest["last_updated"] = now
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    report["source_fixes"] = fixes

    # ---------- 2. rebuild processing_tasks ----------
    cur.execute("DELETE FROM processing_tasks")
    tasks = []
    CHUNK = 10
    for s in manifest["sources"]:
        sid, doc = s["source_id"], s["source_document"]
        pc = s["page_count"] or 1
        n = max(1, (pc + CHUNK - 1) // CHUNK) if pc > 25 else 1
        for i in range(n):
            ps = i * CHUNK + 1
            pe = min(pc, (i + 1) * CHUNK)
            tid = f"{sid.replace('source_', 'task_')}_{i+1:02d}"
            tasks.append((tid, sid, ps, pe, "main", "pending", None,
                          f"Extract {doc} p{ps}-{pe} (rebuilt Stage 2A, real page count {pc})"))
    cur.executemany(
        "INSERT INTO processing_tasks (task_id, source_id, page_start, page_end, section, status, assigned_role, notes) VALUES (?,?,?,?,?,?,?,?)",
        tasks)
    report["tasks_total"] = len(tasks)
    report["tasks_009"] = sum(1 for t in tasks if t[1] == "source_009")

    # ---------- 3. parse CN core rules ----------
    cn_file = os.path.join(EX, "loltcg_pdfs__09_2026-07-23_6f47b6ebe57341a5bb5f4bed5548d051.txt")
    entries = []   # (rule_number, text, page_start, page_end)
    front = []     # front matter lines (page 1 before first rule)
    page = 0
    cur_e = None
    for raw in open(cn_file, encoding="utf-8"):
        line = raw.rstrip("\n").strip()
        pm = PAGE_RE.match(line)
        if pm:
            page = int(pm.group(1))
            continue
        if not line:
            continue
        m = RULE_RE.match(line)
        if m:
            if cur_e:
                entries.append(cur_e)
            cur_e = [m.group(1)[:-1], m.group(2).strip(), page, page]
        else:
            if cur_e is None:
                front.append((page, line))
            else:
                cur_e[1] += line
                cur_e[3] = page
    if cur_e:
        entries.append(cur_e)

    # top section & heading tracking
    top_title, top_num = None, None
    last_heading = None
    rows = []
    seq = 0
    seen = {}
    dups = []
    pages_covered = set()
    for rn, text, ps, pe in entries:
        seq += 1
        is_top = bool(TOP_SECTION_RE.match(rn))
        if is_top:
            top_num, top_title = rn, text
        is_heading_cand = ("。" not in text and len(text) <= 25 and not text.startswith(("*", "（", "(", "“《")))
        if is_heading_cand:
            last_heading = f"{rn} {text}"
        if rn in seen:
            dups.append(rn)
        seen[rn] = seen.get(rn, 0) + 1
        for p in range(ps, pe + 1):
            pages_covered.add(p)
        notes = ["structural_extraction"]
        if is_heading_cand:
            notes.append("heading_candidate")
        if is_top:
            notes.append("top_section")
        if pe > ps:
            notes.append(f"spans_pages {ps}-{pe}")
        rows.append((
            f"EV-CN-CR-{seq:04d}",
            f"CN-CR-{rn}",
            (top_title or "front_matter") if not is_top or top_title else top_title,
            "source_009", "rule", "zh",
            "09_2026-07-23_6f47b6ebe57341a5bb5f4bed5548d051.pdf",
            "v2026", "2026-07-17",
            ps,
            f"{top_num} {top_title}" if top_num else "000 黄金与白银法则",
            last_heading,
            rn,
            text,
            None, None, None, None, None, None, None, None,
            "high",
            "; ".join(notes)))

    # front matter evidence
    if front:
        ftext = "\n".join(l for _, l in front)
        fpage = front[0][0]
        cur.execute(
            """INSERT INTO evidence (evidence_id, rule_id_candidate, topic, source_id, source_type,
               source_language, source_document, version, date, page, section, heading, rule_number,
               original_text, normalized_summary, applicable_object, trigger, precondition, effect,
               restriction, exception, example, confidence, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            ("EV-CN-CR-0000", None, "front_matter", "source_009", "rule", "zh",
             "09_2026-07-23_6f47b6ebe57341a5bb5f4bed5548d051.pdf", "v2026", "2026-07-17",
             fpage, "front_matter", None, None, ftext,
             None, None, None, None, None, None, None, None, "high",
             "structural_extraction; document title + last-updated date"))
        pages_covered.add(fpage)

    cur.executemany(
        """INSERT INTO evidence (evidence_id, rule_id_candidate, topic, source_id, source_type,
           source_language, source_document, version, date, page, section, heading, rule_number,
           original_text, normalized_summary, applicable_object, trigger, precondition, effect,
           restriction, exception, example, confidence, notes)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        rows)

    # mark source_009 tasks completed
    cur.execute("UPDATE processing_tasks SET status='completed', notes=notes||' -> evidence rows written' WHERE source_id='source_009'")

    con.commit()

    total_pages = page_count(cn_file)
    missing_pages = [p for p in range(1, total_pages + 1) if p not in pages_covered]
    report.update(
        evidence_rows=len(rows) + (1 if front else 0),
        numbered_entries=len(entries),
        first_rule=entries[0][0], last_rule=entries[-1][0],
        duplicate_rule_numbers=dups,
        total_pages=total_pages,
        missing_pages=missing_pages,
        completed_009_tasks=report["tasks_009"],
    )
    cur.execute("SELECT COUNT(*) FROM evidence WHERE source_id='source_009'")
    report["db_evidence_009"] = cur.fetchone()[0]
    con.close()
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
