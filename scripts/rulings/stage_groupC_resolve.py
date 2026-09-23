# -*- coding: utf-8 -*-
"""Group C bundle: authority topology (0009/0013), supersession (0006), incorporation
(0012/0007), classification review (0015), Stage-3 handoff tags (0004/0005).
Also repairs 0307/0308 fractured question boundary."""
import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")

def note(eid, tag, guard_key=None):
    cur = con.execute("SELECT notes FROM evidence WHERE evidence_id=?", (eid,)).fetchone()
    if not cur:
        print("WARN missing", eid); return
    n = cur[0] or ""
    key = guard_key or tag.split("=")[0]
    if key in n:
        return
    con.execute("UPDATE evidence SET notes=COALESCE(notes,'') || ? WHERE evidence_id=?",
                (" | " + tag, eid))

def close_mr(mrid, text):
    row = con.execute("SELECT issue_description FROM manual_review WHERE item_id=?", (mrid,)).fetchone()
    if "裁定关闭" in (row[0] or ""):
        print(mrid, "already closed"); return
    con.execute("UPDATE manual_review SET issue_description=issue_description || ? WHERE item_id=?",
                (" [2026-09-20 裁定关闭] " + text, mrid))
    print(mrid, "closed")

def defer_mr(mrid, text):
    row = con.execute("SELECT issue_description FROM manual_review WHERE item_id=?", (mrid,)).fetchone()
    if "移交 Stage 3" in (row[0] or ""):
        return
    con.execute("UPDATE manual_review SET issue_description=issue_description || ? WHERE item_id=?",
                (" [2026-09-20 移交 Stage 3] " + text, mrid))
    print(mrid, "deferred to Stage 3")

# ---------- repair 0307/0308 fracture ----------
a = con.execute("SELECT faq_answer FROM evidence WHERE evidence_id='EV-CN-FAQ-0307'").fetchone()[0] or ""
if "相关规则" in a:
    lines = a.split("\n")
    idx = next(i for i, l in enumerate(lines) if l.startswith("相关规则"))
    tail = [l for l in lines[idx + 1:] if l.strip()]
    if tail:
        q7 = con.execute("SELECT faq_question FROM evidence WHERE evidence_id='EV-CN-FAQ-0307'").fetchone()[0] or ""
        q8 = con.execute("SELECT faq_question FROM evidence WHERE evidence_id='EV-CN-FAQ-0308'").fetchone()[0] or ""
        a8 = con.execute("SELECT faq_answer FROM evidence WHERE evidence_id='EV-CN-FAQ-0308'").fetchone()[0] or ""
        # only repair if not already done (tail should start with 我的“黄沙士兵)
        if not q8.startswith("我的“黄沙士兵”"):
            new_a7 = "\n".join(lines[:idx + 1])
            new_q8 = "\n".join(tail) + "\n" + q8
            con.execute("UPDATE evidence SET faq_answer=?, original_text=? WHERE evidence_id='EV-CN-FAQ-0307'",
                        (new_a7, q7 + "\n\n" + new_a7))
            con.execute("UPDATE evidence SET faq_question=?, original_text=? WHERE evidence_id='EV-CN-FAQ-0308'",
                        (new_q8, new_q8 + "\n\n" + a8))
            mftag = ("manual_fix 2026-09-20: question fractured across items; leading line(s) relocated"
                     " from 0307 answer to 0308 question (found during MR-2D-0006 resolution)")
            note("EV-CN-FAQ-0307", mftag)
            note("EV-CN-FAQ-0308", mftag)
            print("0307/0308 fracture repaired, moved lines:", len(tail))
        else:
            print("0307/0308 already repaired")

# ---------- Domain 1: authority topology (0009/0013) ----------
TOPO = ("效力拓扑裁定：1) 核心规则（当前版本，含官方声明已并入的内容）为常态最高；"
        "2) 官方FAQ/Patch Notes 具有过渡性最高效力——与核心规则冲突时以FAQ/Patch Notes 为准，"
        "有效期至下一版核心规则发布即失效（007/011/005 声明机制）；3) FAQ 间后发取代先发；"
        "4) 裁判FAQ（001/006/008，社区整理，非官方FAQ）为最低层级，仅作判罚参考，与上述冲突自动让位。")
close_mr("MR-2D-0009", TOPO)
close_mr("MR-2D-0013", TOPO + " 裁判FAQ 归入第 4 层级确认。")

# ---------- Domain 2: supersession (0006) ----------
note("EV-CN-FAQ-0089", "superseded_by=EV-CN-FAQ-0307 (011 明示『铸魂淬炼常见问题解答中的相关答复已不再适用』; MR-2D-0006 ruled 2026-09-20)")
note("EV-CN-FAQ-0090", "superseded_by=EV-CN-FAQ-0307 (same supersession; 厄斐琉斯双触发答复废弃; MR-2D-0006 ruled 2026-09-20)")
note("EV-CN-FAQ-0307", "supersedes=EV-CN-FAQ-0089,EV-CN-FAQ-0090 (MR-2D-0006 ruled 2026-09-20)")
close_mr("MR-2D-0006",
         "取代链建立：005 的斯弗尔尚歌答复(0089)/厄斐琉斯答复(0090) 标 superseded_by=0307；"
         "011 阿克尚条目(0307) 标 supersedes。顺带修复 0307/0308 问句断行错位（manual_fix 注记）。")

# ---------- Domain 2: incorporation metadata (0012) ----------
close_mr("MR-2D-0012",
         "对账确认：声明所指的是外部文档『Unleashed FAQ』（非本库 source_016 Patch Notes），本库无该文档条目可标；"
         "声明本身已作为 reconciliation 元数据存于 source_019 front_matter，Stage 3 处理 016/019 条目与核心规则"
         "重复计数问题时以此为依据。")

# ---------- Domain 3: 735.1.c (0007) ----------
note("EV-CN-FAQ-0055",
     "incorporated_into=EV-CN-CR-2140 (2026-07 核心规则 809.1.c; 条文编号迁移 735.1.c->809.1.c,"
     "措辞重构、语义等价：法盾费用语义一致; MR-2D-0007 ruled 2026-09-20)")
close_mr("MR-2D-0007",
         "FAQ(2026-01) 对 735.1.c 的文本修订已被 2026-07 版核心规则吸收——现行规则位于 809.1.c"
         "（『由对手控制且将[我/此牌]选为目标的法术或技能，每将[我/此牌]选作一次目标，其费用就增加等同于"
         "[法盾值]的额外费用才能打出』），与 FAQ 修订版语义等价、文本重构、编号迁移。FAQ 条目已标 "
         "incorporated_into=EV-CN-CR-2140，无未决冲突。")

# ---------- Domain 5: 007 prose classification review (0015) ----------
cls_rows = con.execute(
    "SELECT evidence_id, faq_classification FROM evidence WHERE source_id='source_007'"
    " AND notes LIKE '%prose_section%' ORDER BY evidence_id").fetchall()
dist = {}
for _, c in cls_rows:
    dist[c] = dist.get(c, 0) + 1
close_mr("MR-2D-0015",
         f"复核 source_007 全部 {len(cls_rows)} 条 prose_section 条目（分布 {dist}）：分类口径与内容匹配合理"
         "（0201 战斗结果/0196 控制权含（旧）（新）对照=rule_change_candidate；0199/0200 含特殊情况声明=exception；"
         "0217 层级合并标题正常）。采用现有启发式分类，不再调整。")

# ---------- Domain 4: Stage 3 handoff (0004/0005) ----------
note("EV-CN-FAQ-0195",
     "cross_language_note (MR-2D-0004 -> Stage 3): 英文条件分句位置差异；中文执行口径已统一（两种句式同义理解），"
     "Stage 3 中英对齐时注记", )
note("EV-CN-FAQ-0260",
     "pending_zh_text_update (MR-2D-0005 -> Stage 3): 沙丘亚龙/金克丝/均衡门徒/艾翁 中文文本官方声明"
     "『或将在未来作出更新调整』；现行结算以本条中英对照分析为准，待后续勘误落地")
defer_mr("MR-2D-0004",
         "已在 EV-CN-FAQ-0195 标注 cross_language_note；中文执行口径由 007 FAQ 统一（两句式同义），"
         "句式差异仅注记。Stage 3 实体对齐时核对英文原文。")
defer_mr("MR-2D-0005",
         "已在 EV-CN-FAQ-0260 标注 pending_zh_text_update；以 008 第 4 节给出的中文结算链分析为现行口径，"
         "四卡（沙丘亚龙/金克丝-暴走萝莉/均衡门徒/艾翁-万物之友）挂观察标记，等后续版本中文勘误。")

con.commit()
print()
print("final MR states:")
for r in con.execute(
        "SELECT item_id, CASE WHEN issue_description LIKE '%裁定关闭%' THEN 'CLOSED'"
        " WHEN issue_description LIKE '%复核完成%' THEN 'CLOSED'"
        " WHEN issue_description LIKE '%移交 Stage 3%' THEN 'DEFERRED' ELSE 'OPEN' END, item_id"
        " FROM manual_review ORDER BY 2"):
    print(f"  {r[1]:8s} {r[0]}")
con.close()
print("done")
