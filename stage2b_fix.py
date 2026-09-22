# -*- coding: utf-8 -*-
"""Stage 2B fix: EN evidence flag parity with CN (top_section heuristic) +
flag possible extraction clips (entry text starting mid-word)."""
import sqlite3, re, json

con = sqlite3.connect('workspace/rules_work.db')
cur = con.cursor()
report = {}

# ---- 1. top_section parity: valid top section = \d00 + short title w/o terminal punctuation
TOP_NUM_RE = re.compile(r"^\d00$")
rows = cur.execute(
    "SELECT evidence_id, rule_number, original_text, notes FROM evidence "
    "WHERE source_id='source_018' AND rule_number IS NOT NULL ORDER BY evidence_id").fetchall()
valid_tops = {rn: text for _, rn, text, _ in rows
              if TOP_NUM_RE.match(rn) and len(text) <= 30 and not text.endswith((".", "?", "!"))}
removed, kept = [], []
for eid, rn, text, notes in rows:
    if not TOP_NUM_RE.match(rn):
        continue
    has_flag = "top_section" in (notes or "")
    valid = rn in valid_tops
    if valid and has_flag:
        kept.append(rn)
    elif valid and not has_flag:
        cur.execute("UPDATE evidence SET notes = COALESCE(notes,'') || '; top_section' WHERE evidence_id=?", (eid,))
        kept.append(rn)
    elif not valid and has_flag:
        new_notes = notes.replace("; top_section", "").replace("top_section; ", "").replace("top_section", "")
        cur.execute("UPDATE evidence SET notes=? WHERE evidence_id=?", (new_notes.strip("; "), eid))
        removed.append(rn)
report["top_section_valid"] = sorted(kept)
report["top_section_removed"] = removed

# ---- 2. possible_extraction_clip flags: first txt line of entry starts lowercase
EN_TXT = 'extracted/riftbound_en_rules__07_2026-07-16_Core_Rules.txt'
PAGE_RE = re.compile(r"^===== PAGE (\d+) =====$")
RN_RE = re.compile(r"^(\d{3}(?:\.(?:\d+|[a-z]))*)\.\s*(.*)$")
clips = {}
cur_rn, first = None, False
for raw in open(EN_TXT, encoding='utf-8'):
    line = raw.strip()
    if PAGE_RE.match(line):
        continue
    if not line:
        continue
    m = RN_RE.match(line)
    if m:
        cur_rn = m.group(1)
        first = not bool(m.group(2))
        if m.group(2) and m.group(2)[0].islower():
            clips[cur_rn] = m.group(2)[:50]
    elif cur_rn and first:
        first = False
        if line[0].islower():
            clips[cur_rn] = line[:50]
updated = 0
for rn in clips:
    r = cur.execute(
        "UPDATE evidence SET notes = COALESCE(notes,'') || '; possible_extraction_clip' "
        "WHERE source_id='source_018' AND rule_number=? AND notes NOT LIKE '%possible_extraction_clip%'",
        (rn,)).rowcount
    updated += r
report["clip_rules"] = clips
report["clip_rows_flagged"] = updated
con.commit()
con.close()
print(json.dumps(report, ensure_ascii=False, indent=2))
