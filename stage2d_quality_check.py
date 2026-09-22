import sqlite3, json
con = sqlite3.connect(r"workspace/rules_work.db")

def show(title, rows, qmax=180, amax=400):
    print("=" * 78)
    print(title)
    for r in rows:
        print(f"-- [{r[0]}] p{r[1]} cls={r[2]} conf={r[3]} topic={r[4]}")
        print("   Q:", (r[5] or "<NULL>")[:qmax].replace("\n", " / "))
        print("   A:", (r[6] or "<NULL>")[:amax].replace("\n", " / "))
        if len(r) > 7 and r[7]:
            print("   notes:", r[7][:230])

q = "SELECT evidence_id,page,faq_classification,confidence,topic,faq_question,faq_answer,notes FROM evidence WHERE "
show("A. 005 rule_change_candidate (规则735.1.c)", con.execute(
    q + "source_id='source_005' AND faq_classification='rule_change_candidate'").fetchall())
show("B. 007 rule_change_candidate 3条（旧/新对照）", con.execute(
    q + "source_id='source_007' AND faq_classification='rule_change_candidate'").fetchall())
show("C. EN marker 分布 (4源)", [
    (f"{src} marker={m}", "", "", "", "", str(c), "", "")
    for src, m, c in con.execute(
        "SELECT source_id, substr(notes, instr(notes,'marker='), 20), COUNT(*) FROM evidence "
        "WHERE notes LIKE '%marker=%' GROUP BY source_id, substr(notes, instr(notes,'marker='), 12)"
        " ORDER BY source_id, 3 DESC").fetchall()])
show("D. 006 typo_fixed 条目", con.execute(
    q + "source_id='source_006' AND notes LIKE '%typo_fixed%'").fetchall())
show("E. 011 相关规则 refs 样本", con.execute(
    q + "source_id='source_011' AND notes LIKE '%related_rule_refs%' LIMIT 2").fetchall())
show("F. 007 front_matter 完整性", con.execute(
    q + "source_id='source_007' AND topic='front_matter'").fetchall())
show("G. 014 front_matter（含生效日声明）", con.execute(
    q + "source_id='source_014' AND topic='front_matter'").fetchall())
show("H. card_ids 对齐样本（011 梅尔）", con.execute(
    q + "source_id='source_011' AND card_ids IS NOT NULL LIMIT 2").fetchall())
con.close()
