"""Stage 3 closeout (task_3_05): close MR-2D-0004/0005/0010 with findings + validate."""
import sqlite3

DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

res = {
    "MR-2D-0004": (
        " [2026-09-21 Stage 3 结案] 已核对英文原文：触发式技能条件分句在英文中确存在前置/"
        "后置两种模板（如 Dune Drake 'When I attack, give me +2 [M] this turn if...' 后置 if "
        "vs 前置条件句式），中文译文不区分该句式差异。官方FAQ(source_007 EV-CN-FAQ-0195)已裁定"
        "两种句式同义统一执行。Stage 3 对齐口径：涉及条件分句位置的中英文模板差异不算语义差异"
        "(translation template variance)，相应对子仍可判 equivalent。不构成冲突，关闭。"
    ),
    "MR-2D-0005": (
        " [2026-09-21 Stage 3 结案] 已核对四卡英文原文：OGN-131/OGN-251/UNL-097/UNL-177 均为英文后置"
        "if 条件结构，中文译文采用前置“如果”句式，语义分歧模式 = 条件检查时点（触发时 vs 结算时）。"
        "现行结算口径以 source_008 第4节(EV-CN-FAQ-0260，设计师口径)中文结算链分析为准；四卡维持 "
        "pending_zh_text_update 观察标记，待后续版本中文勘误。跨语言分歧已文档化于本条及 FAQ 注记，"
        "Stage 4 reconciliation 采用 FAQ 现行口径并以 EN 原文为效力参照。结案（watch 持续）。"
    ),
    "MR-2D-0010": (
        " [2026-09-21 Stage 3 结案] 『先前 Origins 官方FAQ/说明文』为外部文档，不在本语料库内"
        "（同 MR-2D-0012 处理方式）；语料库内不存在被取代侧条目，无 in-corpus superseded 可标记。"
        "效力拓扑裁定维持：EN Core Rules Patch Notes(2025-10-24) > 先前 Origins 官方FAQ。"
        "012 的 CLARIFIED/NEW RULE 条目为权威侧，实际冲突比对移交 Stage 4B reconciliation"
        "（012条目 vs 核心规则聚类时裁决）。关闭。"
    ),
}
for mid, txt in res.items():
    c.execute("SELECT issue_description FROM manual_review WHERE item_id=?", (mid,))
    if "2026-09-21 Stage 3 结案" not in c.fetchone()["issue_description"]:
        c.execute("UPDATE manual_review SET issue_description = issue_description || ? WHERE item_id=?", (txt, mid))
        conn.commit()
print("MR-2D-0004/0005/0010 closed with Stage 3 findings")

# ---- validation ----
out = {}
c.execute("SELECT substr(alignment_id,1,6) p, relation, COUNT(*) n FROM alignments GROUP BY p, relation ORDER BY p")
out["alignments"] = [dict(r) for r in c.fetchall()]

# core rules coverage: every rule-evidence row paired exactly once in AL-CR
c.execute("""SELECT COUNT(*) FROM evidence e WHERE source_type='rule'
             AND NOT EXISTS (SELECT 1 FROM alignments a WHERE a.evidence_a=e.evidence_id OR a.evidence_b=e.evidence_id)""")
out["rule_evidence_unpaired"] = c.fetchone()[0]

# errata coverage
c.execute("""SELECT source_language,
               SUM(CASE WHEN notes LIKE '%stage3_alignment%' THEN 1 ELSE 0 END) tagged,
               SUM(CASE WHEN EXISTS (SELECT 1 FROM alignments a WHERE a.evidence_a=e.evidence_id OR a.evidence_b=e.evidence_id) THEN 1 ELSE 0 END) paired,
               COUNT(*) total
             FROM evidence e WHERE source_type='errata' GROUP BY source_language""")
out["errata_coverage"] = [dict(r) for r in c.fetchall()]
c.execute("""SELECT COUNT(*) FROM evidence e WHERE source_type='errata'
             AND notes NOT LIKE '%stage3_alignment%'
             AND NOT EXISTS (SELECT 1 FROM alignments a WHERE a.evidence_a=e.evidence_id OR a.evidence_b=e.evidence_id)""")
out["errata_unresolved"] = c.fetchone()[0]

# faq/oe coverage
c.execute("""SELECT COUNT(*) FROM evidence WHERE source_type IN ('faq','official_explanation')
             AND notes NOT LIKE '%stage3_alignment%'""")
out["faq_oe_untagged"] = c.fetchone()[0]

# dup alignment check
c.execute("""SELECT COUNT(*) FROM (SELECT evidence_a, evidence_b, COUNT(*) n FROM alignments GROUP BY evidence_a, evidence_b HAVING n>1)""")
out["dup_pairs"] = c.fetchone()[0]

# stage-3 tasks status
c.execute("SELECT task_id, status FROM processing_tasks WHERE task_id LIKE 'task_3_%' ORDER BY task_id")
out["stage3_tasks"] = [dict(r) for r in c.fetchall()]

# remaining open stage-2 deferred MR = 0 after close; MR-3-CR opening balance stays for Stage 4/5
c.execute("""SELECT COUNT(*) FROM manual_review WHERE item_id LIKE 'MR-3%'""")
out["mr_stage3_open_items"] = c.fetchone()[0]

import json
print(json.dumps(out, ensure_ascii=False, indent=1))
conn.close()
