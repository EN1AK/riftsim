# -*- coding: utf-8 -*-
"""Renumber Stage 2D evidence ids sequentially per language prefix (idempotent)."""
import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

con = sqlite3.connect(r"workspace/rules_work.db")
PLANS = [
    ("EV-CN-FAQ", ["source_001","source_005","source_006","source_007","source_008","source_011"]),
    ("EV-EN-OE", ["source_012","source_014","source_016","source_019"]),
]
for pref, sids in PLANS:
    rows = []
    for sid in sids:
        rows += [r[0] for r in con.execute(
            "SELECT evidence_id FROM evidence WHERE source_id=? AND notes LIKE '%stage2d faq%' "
            "ORDER BY evidence_id", (sid,))]
    for i, rid in enumerate(rows, 1):
        new = f"{pref}-{i:04d}"
        if rid != new:
            con.execute("UPDATE evidence SET evidence_id=? WHERE evidence_id=?", (new, rid))
    print(pref, "renumbered:", len(rows), f"({pref}-0001..{pref}-{len(rows):04d})")
con.commit()
# refresh sources notes id ranges
for sid in ("source_001","source_005","source_006","source_007","source_008","source_011",
            "source_012","source_014","source_016","source_019"):
    lo, hi = con.execute(
        "SELECT MIN(evidence_id), MAX(evidence_id) FROM evidence WHERE source_id=? "
        "AND notes LIKE '%stage2d faq%'", (sid,)).fetchone()
    notes = con.execute("SELECT notes FROM sources WHERE source_id=?", (sid,)).fetchone()[0]
    import re
    notes = re.sub(r"\(EV-[A-Z-]+-\d+\.\.EV-[A-Z-]+-\d+\)", f"({lo}..{hi})", notes)
    con.execute("UPDATE sources SET notes=? WHERE source_id=?", (notes, sid))
con.commit()
print("sources notes ranges refreshed")
con.close()
