import sqlite3, json
con = sqlite3.connect(r"workspace/rules_work.db")
sids = ["source_001","source_005","source_006","source_007","source_008","source_011",
        "source_012","source_014","source_016","source_019"]
pcnt = {r[0]: r[1] for r in con.execute("SELECT source_id, page_count FROM sources")}
for sid in sids:
    rows = con.execute(
        "SELECT evidence_id,page,faq_classification,faq_question,faq_answer,notes,topic FROM evidence "
        "WHERE source_id=? AND notes LIKE '%stage2d faq%' ORDER BY evidence_id", (sid,)).fetchall()
    its = [r for r in rows if r[6] != "front_matter"]
    fm = [r for r in rows if r[6] == "front_matter"]
    noq = [r for r in its if not (r[3] or "").strip()]
    pages = sorted({r[1] for r in its if r[1]})
    noans = [r for r in its if not (r[4] or "").strip()]
    nrev = [r for r in its if "needs_review\": true" in (r[5] or "")]
    cls = {}
    for r in its:
        cls[r[2]] = cls.get(r[2], 0) + 1
    print(f"== {sid}: items={len(its)} fm={len(fm)} pages={pages[0] if pages else '-'}-{pages[-1] if pages else '-'}"
          f"/{pcnt.get(sid)} distinct={len(pages)} noq={len(noq)} noans={len(noans)} nrev={len(nrev)}")
    print(f"   cls={json.dumps(cls, ensure_ascii=False)}")
    if noq:
        for r in noq[:3]:
            print(f"   NOQ   {r[0]} p{r[1]} topic={r[6]} A: {(r[4] or '')[:80]}")
    if noans:
        for r in noans[:5]:
            print(f"   NOANS {r[0]} p{r[1]} Q: {(r[3] or '')[:90]}")
    if nrev:
        for r in nrev[:6]:
            print(f"   NREV  {r[0]} p{r[1]} cls={r[2]} Q: {(r[3] or '')[:80]}")
con.close()
