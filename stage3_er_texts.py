"""Stage 3 3-ER: dump full original_text + notes for contested errata rows."""
import sqlite3

DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

ids = [
    # FND<->OGN teemo / yasuo hypothesis
    "EV-CN-ER-0023", "EV-EN-ER-0024", "EV-CN-ER-0028", "EV-EN-ER-0029",
    # untagged source_003 terminology_fix
    "EV-CN-ER-0059", "EV-CN-ER-0060", "EV-CN-ER-0061", "EV-CN-ER-0062",
    # source_010 unmatched
    "EV-CN-ER-0089", "EV-CN-ER-0091", "EV-CN-ER-0093",
    # reuse-contested triplets
    "EV-CN-ER-0034", "EV-CN-ER-0090",  # UNL-186 vs EN source_017
    "EV-CN-ER-0022", "EV-CN-ER-0092",  # OGN-289 vs EN source_013
    "EV-CN-ER-0048", "EV-CN-ER-0084",  # UNL-079 vs EN source_020
]
c.execute(
    f"""SELECT evidence_id, card_ids, target_rule_candidate, modification_type, date,
               related_cards, original_text, notes
        FROM evidence WHERE evidence_id IN ({','.join('?'*len(ids))}) ORDER BY evidence_id""",
    ids,
)
for r in c.fetchall():
    print("=" * 100)
    print(r["evidence_id"], "|", r["card_ids"], "|", r["target_rule_candidate"], "|",
          r["modification_type"], "|", r["date"])
    print("NOTES:", (r["notes"] or "")[:300])
    print("TEXT:")
    print(r["original_text"])
# EN-side counterparts
print("\n\n########## EN counterparts (017 UNL-186, 013 OGN-289, 020 UNL-079) ##########")
c.execute("""SELECT evidence_id, source_id, card_ids, modification_type, date, original_text, notes
             FROM evidence WHERE source_type='errata' AND card_ids IS NOT NULL
               AND (card_ids LIKE '%UNL-186%' OR card_ids LIKE '%OGN-289%' OR card_ids LIKE '%UNL-079%')
               AND source_language='en' ORDER BY evidence_id""")
for r in c.fetchall():
    print("=" * 100)
    print(r["evidence_id"], r["source_id"], r["card_ids"], r["modification_type"], r["date"])
    print("NOTES:", (r["notes"] or "")[:200])
    print("TEXT:")
    print(r["original_text"])
conn.close()
