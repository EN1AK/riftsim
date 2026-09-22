# -*- coding: utf-8 -*-
"""MR-2D-0008 resolve: build cross_ref pointers FAQ<->2C errata, annotate 0260/0277, close MR."""
import re, sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

con = sqlite3.connect(r"workspace/rules_work.db")

def add_note(eid, tag):
    cur = con.execute("SELECT notes FROM evidence WHERE evidence_id=?", (eid,)).fetchone()
    if not cur:
        print("WARN missing", eid); return False
    n = cur[0] or ""
    if tag.split("=")[0] in n:   # idempotent on the key itself? only skip duplicates of same tag
        pass
    if tag in n:
        return False
    con.execute("UPDATE evidence SET notes=COALESCE(notes,'') || ? WHERE evidence_id=?",
                (" | " + tag, eid))
    return True

pairs = []  # (faq_id, er_id, note)

# A. 005 revised_block cards
blocks = con.execute(
    "SELECT evidence_id, faq_question FROM evidence WHERE source_id='source_005'"
    " AND notes LIKE '%revised_block%' ORDER BY evidence_id").fetchall()
for fid, q in blocks:
    name = re.sub(r"（(?:修订后|新文本)）|\s*\[(?:新文本|修订后)\]", "", q or "").strip()
    if name.startswith("规则"):
        continue  # 735.1.c -> MR-2D-0007 scope, no 2C counterpart
    er = con.execute(
        "SELECT evidence_id FROM evidence WHERE evidence_id LIKE 'EV-CN-ER-%'"
        " AND target_rule_candidate LIKE ?",
        ("%" + name.split(" - ")[0].replace("·", "%") + "%",)).fetchall()
    if len(er) != 1:
        print("WARN map failed:", fid, name, [e[0] for e in er]); continue
    pairs.append((fid, er[0][0], ""))

# B/C. 008 & 011 embedded
pairs.append(("EV-CN-FAQ-0260", "EV-CN-ER-0010",
              "note: zh text semantically identical; FAQ uses full word 战力+2 where 2C uses [M]+2;"
              " FAQ entry also carries the EN text side-by-side"))
pairs.append(("EV-CN-FAQ-0277", "EV-CN-ER-0078",
              "partial_quote: FAQ '勘误后文本' omits the [百炼] keyword definition parenthesis;"
              " see 2C EV-CN-ER-0078 for the full corrected text"))
pairs.append(("EV-CN-FAQ-0323", "EV-CN-ER-0086", ""))

n = 0
for fid, erid, extra in pairs:
    t1 = f"cross_ref_errata={erid} (MR-2D-0008 resolved 2026-09-20)"
    t2 = f"cross_ref_faq={fid} (MR-2D-0008 resolved 2026-09-20)"
    add_note(fid, t1)
    add_note(erid, t2)
    if extra:
        add_note(fid, extra)
    n += 1
print(f"cross-ref pairs established: {n}")

con.execute(
    "UPDATE manual_review SET issue_description=issue_description || ? WHERE item_id='MR-2D-0008'"
    " AND issue_description NOT LIKE '%裁定关闭%'",
    (" [2026-09-20 裁定关闭] 逐条核对 21 处 FAQ 内嵌勘误：005 修订块 18 卡 ↔ source_004 勘误全部一致"
     "（13 全同 + 5 FAQ 含说明尾段的包含关系）；008 沙丘亚龙语义一致（中英对照格式差异，已注记）；"
     "008 永恩为节引（省略[百炼]关键词括注，已注记 partial_quote）；011 星界灵鹭一致。无冲突。"
     "已建立 cross_ref_errata / cross_ref_faq 双向指针 21 组。",))
con.commit()
print("open MR remaining:",
      [r[0] for r in con.execute(
          "SELECT item_id FROM manual_review WHERE issue_description NOT LIKE '%裁定关闭%'"
          " AND issue_description NOT LIKE '%复核完成%'")])
con.close()
print("done")
