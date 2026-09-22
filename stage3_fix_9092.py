import sqlite3
DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
conn = sqlite3.connect(DB)
c = conn.cursor()
tags = {
    "EV-CN-ER-0090": "stage3_alignment: unmatched (zh_only wording refinement 2026-09-21; functional errata at AL via EV-CN-ER-0034<->EV-EN-ER-0052)",
    "EV-CN-ER-0092": "stage3_alignment: unmatched (zh_only wording refinement 2026-09-21; functional errata at AL via EV-CN-ER-0022<->EV-EN-ER-0023)",
}
for eid, t in tags.items():
    c.execute("SELECT notes FROM evidence WHERE evidence_id=?", (eid,))
    row = c.fetchone()
    if row and "stage3_alignment" not in row[0]:
        c.execute("UPDATE evidence SET notes = notes || ' | ' || ? WHERE evidence_id=?", (t, eid))
        conn.commit()
c.execute("""SELECT COUNT(*) FROM evidence e WHERE source_type='errata'
             AND notes NOT LIKE '%stage3_alignment%'
             AND NOT EXISTS (SELECT 1 FROM alignments a WHERE a.evidence_a=e.evidence_id OR a.evidence_b=e.evidence_id)""")
print("errata_unresolved now:", c.fetchone()[0])
conn.close()
