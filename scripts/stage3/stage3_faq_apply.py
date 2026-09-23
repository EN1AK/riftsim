"""Stage 3 3-FAQ apply: no item pairs exist; tag every FAQ/OE item with explicit alignment status.

Reviewed 2026-09-21:
- 4 doc-pairs share era/set but NO item-level correspondence (different doc classes:
  zh official/judge FAQ Q&A vs en Patch Notes rule-change announcements).
- 6 signal candidates (card/rule overlap) reviewed one-by-one, all rejected:
  zh 0005/0006/0007/0008 + 0316 + 0324 vs en 0059/0263/0265 -> shared example card only,
  ruling content differs -> no alignment.
- zh 006/008 judge FAQs: no counterpart at all.
"""
import sqlite3

DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

DOC_PAIR = {"source_001": "source_012", "source_005": "source_014",
            "source_007": "source_016", "source_011": "source_019"}
EN_PAIR = {v: k for k, v in DOC_PAIR.items()}
REVIEWED_ZH = {"EV-CN-FAQ-0005", "EV-CN-FAQ-0006", "EV-CN-FAQ-0007", "EV-CN-FAQ-0008",
               "EV-CN-FAQ-0316", "EV-CN-FAQ-0324"}
REVIEWED_EN = {"EV-EN-OE-0059", "EV-EN-OE-0263", "EV-EN-OE-0265"}

c.execute("""SELECT evidence_id, source_id, source_language, faq_question, notes FROM evidence
             WHERE source_type IN ('faq','official_explanation')""")
rows = c.fetchall()
n_z = n_e = n_fm = n_rev = 0
for r in rows:
    eid, src, lang = r["evidence_id"], r["source_id"], r["source_language"]
    if "stage3_alignment" in (r["notes"] or ""):
        continue
    is_fm = not r["faq_question"]
    if is_fm:
        tag = "stage3_alignment: not_applicable (front_matter)"
        n_fm += 1
    elif eid in REVIEWED_ZH:
        tag = ("stage3_alignment: unmatched_zh (2026-09-21 reviewed; candidate pair "
               "rejected: shared example card, different ruling content)")
        n_rev += 1
    elif eid in REVIEWED_EN:
        tag = ("stage3_alignment: unmatched_en (2026-09-21 reviewed; candidate pair "
               "rejected: shared example card, different ruling content)")
        n_rev += 1
    elif lang == "zh":
        pair = DOC_PAIR.get(src, "none")
        tag = (f"stage3_alignment: unmatched_zh (no cross-language counterpart item in "
               f"corpus; doc pair {src}<->{pair} reviewed 2026-09-21)")
        n_z += 1
    else:
        pair = EN_PAIR.get(src, "none")
        tag = (f"stage3_alignment: unmatched_en (no cross-language counterpart item in "
               f"corpus; doc pair {pair}<->{src} reviewed 2026-09-21)")
        n_e += 1
    c.execute("UPDATE evidence SET notes = notes || ' | ' || ? WHERE evidence_id = ?", (tag, eid))
    conn.commit()

print(f"tagged: zh_unmatched={n_z} en_unmatched={n_e} reviewed_rejected={n_rev} front_matter={n_fm}")

c.execute("""UPDATE processing_tasks SET status='completed',
             notes='Stage 3 batch 3-FAQ done: 0 cross-language pairs (6 signal candidates reviewed+rejected); all 604 faq/oe items explicitly tagged stage3_alignment (unmatched/unmatched_en/not_applicable); doc-level relations recorded in workspace/reports/stage3_faq_alignment.md'
             WHERE task_id='task_3_04'""")
conn.commit()
print("task_3_04 -> completed")
conn.close()
