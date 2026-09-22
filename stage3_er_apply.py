"""Stage 3 3-ER apply: write 63 zh-en errata alignments + zh_only tags, item-level commits.

Decisions (2026-09-21 model review of NEW/OLD text blocks):
- 63 pairs, relation=equivalent, high confidence (NEW texts reviewed equivalent).
- 30 zh rows unmatched = zh-only translation/wording fixes (no EN errata needed).
  - 0059..0062 newly confirmed zh_only_translation (extends MR-2C-0004 ruling).
  - 0089/0091/0092/0093 source_010 zh wording refinements; 0093 corrected a mistranslated
    targeting restriction (zh old text wrongly added 'might greater than mine').
  - 0090/0092 reference the functional-errata alignment of the same card.
- 3 EN front_matter rows: not_applicable.
"""
import sqlite3
import json
import re

DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

fam = {"source_002": ("source_013", "zh Origins errata republished 2025-12-03 (en 2025-10-21)"),
       "source_003": ("source_017", "zh Unleashed errata 2026-04-15 (en 2026-04-03)"),
       "source_004": ("source_015", "zh Spiritforged errata 2026-04-15 (en 2026-01-14)"),
       "source_010": ("source_020", "zh/en Vendetta errata same release 2026-07-24")}

# build pairs by family + card-id intersection
c.execute("""SELECT evidence_id, source_id, card_ids, modification_type, date FROM evidence
             WHERE source_type='errata' AND source_language='zh' ORDER BY evidence_id""")
zh_rows = c.fetchall()
pairs = []
seen_en = set()
for z in zh_rows:
    if z["source_id"] not in fam or not z["card_ids"]:
        continue
    ids = json.loads(z["card_ids"])
    qmarks = ",".join("?" * len(ids))
    en_src = fam[z["source_id"]][0]
    cands = c.execute(
        f"""SELECT evidence_id, modification_type, date FROM evidence
            WHERE source_type='errata' AND source_language='en' AND source_id=?
              AND EXISTS (SELECT 1 FROM json_each(evidence.card_ids) je WHERE je.value IN ({qmarks}))
            ORDER BY evidence_id""",
        [en_src, *ids]).fetchall()
    cands = [e for e in cands if e["evidence_id"] not in seen_en]
    if not cands:
        continue
    e = cands[0]
    seen_en.add(e["evidence_id"])
    pairs.append((z, e))

assert len(pairs) == 63, f"expected 63 pairs, got {len(pairs)}"

seq = 0
for z, e in pairs:
    seq += 1
    al_id = f"AL-ER-{seq:04d}"
    vz, ve = z["date"], e["date"]
    mod_note = ""
    if z["modification_type"] != e["modification_type"]:
        mod_note = f" mod_type heuristic differs zh={z['modification_type']}/en={e['modification_type']} (NEW texts reviewed equivalent)."
    notes = (f"card errata pair {json.loads(z['card_ids'])[0]}; stage3 2026-09-21 model review: "
             f"NEW/OLD correction content equivalent.{mod_note}")
    c.execute(
        "INSERT INTO alignments (alignment_id, evidence_a, evidence_b, relation, confidence, version_relation, notes) VALUES (?,?,?,?,?,?,?)",
        (al_id, z["evidence_id"], e["evidence_id"], "equivalent", "high",
         f"same_correction; {fam[z['source_id']][1]}", notes))
    conn.commit()

print(f"alignments written: {seq}")

# zh-only rows tagging
extra_tags = {
    "EV-CN-ER-0059": "zh_only_translation (confirmed 2026-09-21 Stage 3: translation-only fix, no EN errata needed; extends MR-2C-0004 ruling)",
    "EV-CN-ER-0060": "zh_only_translation (confirmed 2026-09-21 Stage 3: translation-only fix, no EN errata needed; extends MR-2C-0004 ruling)",
    "EV-CN-ER-0061": "zh_only_translation (confirmed 2026-09-21 Stage 3: translation-only fix, no EN errata needed; extends MR-2C-0004 ruling)",
    "EV-CN-ER-0062": "zh_only_translation (confirmed 2026-09-21 Stage 3: translation-only fix, no EN errata needed; extends MR-2C-0004 ruling)",
    "EV-CN-ER-0089": "zh_only_translation (confirmed 2026-09-21 Stage 3: zh wording refinement of Time Warp; no EN errata)",
    "EV-CN-ER-0091": "zh_only_translation (confirmed 2026-09-21 Stage 3: zh wording refinement of Loyal Pup; no EN errata)",
    "EV-CN-ER-0093": "zh_only_translation (confirmed 2026-09-21 Stage 3: corrected mistranslated targeting restriction 'might greater than mine' -> matches EN text; no EN errata needed; note: changes zh effective card text)",
    "EV-CN-ER-0090": "zh_only wording refinement (2026-09-21 Stage 3): zh polish of UNL-186 post-errata text; functional errata aligned at 0034<->EV-EN-ER-0052",
    "EV-CN-ER-0092": "zh_only wording refinement (2026-09-21 Stage 3): zh polish of OGN-289 post-errata text; functional errata aligned at 0022<->EV-EN-ER-0023",
}
for eid, tag in extra_tags.items():
    c.execute("UPDATE evidence SET notes = notes || ' | ' || ? WHERE evidence_id = ?", (tag, eid))
    conn.commit()

# mark the 21 pre-tagged zh_only rows + newly tagged with stage3 alignment status
c.execute("""SELECT evidence_id FROM evidence
             WHERE source_type='errata' AND source_language='zh' AND notes LIKE '%zh_only_translation%'""")
tagged = [r["evidence_id"] for r in c.fetchall()]
n_status = 0
for eid in tagged:
    c.execute("SELECT notes FROM evidence WHERE evidence_id=?", (eid,))
    if "stage3_alignment" not in c.fetchone()["notes"]:
        c.execute("UPDATE evidence SET notes = notes || ' | stage3_alignment: unmatched (zh_only_translation confirmed 2026-09-21)' WHERE evidence_id=?", (eid,))
        conn.commit()
        n_status += 1

# EN front_matter: not applicable
c.execute("""UPDATE evidence SET notes = notes || ' | stage3_alignment: not_applicable (front_matter, no zh counterpart required)'
             WHERE source_type='errata' AND (card_ids IS NULL OR card_ids='') AND notes NOT LIKE '%stage3_alignment%'""")
conn.commit()

print(f"extra zh_only tags: {len(extra_tags)}; stage3_alignment status added to {n_status} zh_only rows")

# task close
c.execute("""UPDATE processing_tasks SET status='completed', completed_at=datetime('now'),
             notes='Stage 3 batch 3-ER done: 63 zh-en errata alignments AL-ER-0001..0063 (relation=equivalent, high); 30 zh-only rows tagged/unmatched explicitly (incl. 0059..0062 newly confirmed zh_only_translation, 0089/0090/0091/0092/0093 source_010 wording fixes); 3 EN front_matter N/A; report workspace/reports/stage3_er_alignment.md'
             WHERE task_id='task_3_03'""")
conn.commit()
print("task_3_03 -> completed")
conn.close()
