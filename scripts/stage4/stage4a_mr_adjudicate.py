# Adjudicate MR-4A-0001..0006: record successor mapping; keep OPEN for Stage 4B final check
import sqlite3

db = sqlite3.connect(r'workspace/rules_work.db')
c = db.cursor()

ADJ = {
    'MR-4A-0001': ('EV-CN-FAQ-0011', '376.3 -> 383.3.d/383.3.d.1 '
                   '(383.3.d.1 内容与旧条文一致：同时多触发按回合顺序放置；'
                   '战斗防守方最后添加的细则由 383.4.f 系列 + 466.x 承担)'),
    'MR-4A-0002': ('EV-CN-FAQ-0031', '322.2,322.3 -> 318 清理(步骤序列); '
                   '现行清理全流程集中于 318-324, 特殊清理步骤由 324.1/466.1.a 决定'),
    'MR-4A-0003': ('EV-CN-FAQ-0032', '322.2,322.3,322.8 -> 318 清理 + 324 特殊清理 + 466 结算步骤; '
                   '440.1.a.1-3/440.1.b -> 466.1.a 战斗特殊清理 (旧440.x为燃烧规则,编号已重用)'),
    'MR-4A-0004': ('EV-CN-FAQ-0055', '735.1.c -> 809.1.c (文本几乎逐字对应, 完全确认; MR-2D-0007 先例)'),
    'MR-4A-0005': ('EV-CN-FAQ-0198', '460.2.c.3 -> 465.2.c.4(+465.2.c.4.a) 致命伤害最小分配一致; '
                   '323.5 -> 318 清理步骤(伤害标记>=战力摧毁)'),
    'MR-4A-0006': ('EV-CN-FAQ-0216', '335.3 -> 334 (+335-336) HOT FEPR 主规则名称逐字对应'),
}

for mid, (eid, mapping) in ADJ.items():
    conf = 'full' if mid == 'MR-4A-0004' else 'content-level (numbering restructured)'
    c.execute(
        "UPDATE manual_review SET possible_explanation=?, cannot_auto_resolve_reason=? WHERE item_id=?",
        (f'ADJUDICATED 2026-09-21 ({conf}): {mapping}. Source FAQ is judge-tier citing older '
         f'core-rules numbering (pre-2026-07 restructure).',
         'kept OPEN per operator decision: Stage 4B must verify successor text covers the FAQ ruling '
         'before closing; treat ref as historical until verified',
         mid))
    print(mid, 'updated')

# annotate affected FAQ evidence rows
for mid, (eid, mapping) in ADJ.items():
    c.execute(
        "UPDATE evidence SET notes = COALESCE(notes,'') || ? WHERE evidence_id=?",
        (f' | stage4a_adjudication[{mid}]: stale rule ref mapped -> {mapping}; pending 4B verification', eid))
db.commit()

# show resulting MR rows
for row in c.execute("SELECT item_id, rule_id, substr(possible_explanation,1,90), substr(cannot_auto_resolve_reason,1,60) FROM manual_review WHERE item_id LIKE 'MR-4A-%'"):
    print(row)
