# -*- coding: utf-8 -*-
"""Stage 2A fix: real page counts, proper task chunks, correct top-section flags."""
import os, re, json, sqlite3, datetime

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WS = os.path.join(BASE, "workspace")
EX = os.path.join(BASE, "extracted")
DB = os.path.join(WS, "rules_work.db")
MANIFEST = os.path.join(WS, "source_manifest.json")
PAGE_RE = re.compile(r"^===== PAGE (\d+) =====$")
TOP_NUM_RE = re.compile(r"^\d00$")

def page_count_of(doc):
    # extracted files are named <folder>__<doc without .pdf>.txt
    stem = doc[:-4] if doc.lower().endswith(".pdf") else doc
    for folder in ("loltcg_pdfs", "riftbound_en_rules"):
        p = os.path.join(EX, f"{folder}__{stem}.txt")
        if os.path.exists(p):
            mx = 0
            with open(p, encoding="utf-8") as f:
                for line in f:
                    m = PAGE_RE.match(line.strip())
                    if m:
                        mx = max(mx, int(m.group(1)))
            return mx
    return 0

con = sqlite3.connect(DB)
cur = con.cursor()
now = datetime.datetime.now().isoformat()

# ---- 1. real page counts into sources + manifest ----
with open(MANIFEST, encoding="utf-8") as f:
    manifest = json.load(f)
pc_report = {}
for s in manifest["sources"]:
    pc = page_count_of(s["source_document"])
    pc_report[s["source_id"]] = pc
    s["page_count"] = pc
    cur.execute("UPDATE sources SET page_count=? WHERE source_id=?", (pc, s["source_id"]))
manifest["last_updated"] = now
with open(MANIFEST, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

# ---- 2. rebuild processing_tasks with real chunks ----
cur.execute("DELETE FROM processing_tasks")
CHUNK = 10
tasks = []
for s in manifest["sources"]:
    sid, doc, pc = s["source_id"], s["source_document"], max(1, s["page_count"])
    n = 1 if pc <= 25 else (pc + CHUNK - 1) // CHUNK
    for i in range(n):
        ps, pe = i * CHUNK + 1, min(pc, (i + 1) * CHUNK)
        tid = f"{sid.replace('source_', 'task_')}_{i + 1:02d}"
        done = (sid == "source_009")
        tasks.append((tid, sid, ps, pe, "main",
                      "completed" if done else "pending", None,
                      (f"Stage2A completed: {doc} p{ps}-{pe} covered by evidence (structural parse)"
                       if done else f"Extract {doc} p{ps}-{pe}")))
cur.executemany(
    "INSERT INTO processing_tasks (task_id, source_id, page_start, page_end, section, status, assigned_role, notes) VALUES (?,?,?,?,?,?,?,?)",
    tasks)

# ---- 3. fix top_section flags & section/topic fields ----
rows = cur.execute(
    "SELECT evidence_id, rule_number, original_text, notes FROM evidence "
    "WHERE source_id='source_009' AND rule_number IS NOT NULL ORDER BY evidence_id").fetchall()
# valid top sections: \d00 + short title without 。
top_sections = {}
for eid, rn, text, notes in rows:
    if TOP_NUM_RE.match(rn) and "\u3002" not in text and len(text) <= 25:
        top_sections[rn] = text
updates = []
cur_top = None
for eid, rn, text, notes in rows:
    if rn in top_sections:
        cur_top = rn
    title = top_sections.get(cur_top, "")
    new_topic = title or "front_matter"
    new_section = f"{cur_top} {title}" if cur_top else "front_matter"
    new_notes = notes or ""
    is_top = rn in top_sections
    if is_top and "top_section" not in new_notes:
        new_notes += "; top_section"
    if not is_top and "top_section" in new_notes:
        new_notes = new_notes.replace("; top_section", "").replace("top_section; ", "").replace("top_section", "")
    updates.append((new_topic, new_section, new_notes.strip("; "), eid))
cur.executemany("UPDATE evidence SET topic=?, section=?, notes=? WHERE evidence_id=?", updates)

con.commit()

print(json.dumps({
    "page_counts": pc_report,
    "total_tasks": len(tasks),
    "tasks_009": sum(1 for t in tasks if t[1] == "source_009"),
    "valid_top_sections": top_sections,
}, ensure_ascii=False, indent=2))
con.close()
