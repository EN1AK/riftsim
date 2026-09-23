import sqlite3, json, sys
sid = sys.argv[1] if len(sys.argv) > 1 else "source_001"
n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
con = sqlite3.connect(r"workspace/rules_work.db")
rows = con.execute(
    "SELECT evidence_id, page, topic, faq_classification, confidence, faq_question, "
    "faq_answer, related_cards, card_ids, rule_id_candidate FROM evidence "
    "WHERE source_id=? AND notes LIKE '%stage2d faq%' AND faq_question IS NOT NULL "
    "ORDER BY evidence_id", (sid,)).fetchall()
print(f"== {sid}: {len(rows)} items; showing {min(n, len(rows))} ==")
for r in rows[:n]:
    print("-" * 70)
    print(f"[{r[0]}] p{r[1]} topic={r[2]} cls={r[3]} conf={r[4]} rule_cand={r[9]}")
    print("Q:", (r[5] or "")[:220].replace("\n", " / "))
    print("A:", (r[6] or "")[:350].replace("\n", " / "))
    print("cards:", r[7])
    print("card_ids:", r[8])
# last item too
if rows:
    r = rows[-1]
    print("-" * 70)
    print(f"[LAST {r[0]}] p{r[1]} topic={r[2]} cls={r[3]}")
    print("Q:", (r[5] or "")[:220].replace("\n", " / "))
    print("A:", (r[6] or "")[:350].replace("\n", " / "))
con.close()
