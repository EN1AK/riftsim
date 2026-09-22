import sqlite3
db = sqlite3.connect(r'workspace/rules_work.db')
db.execute(
    "UPDATE manual_review SET possible_explanation=? WHERE item_id='MR-4A-0005'",
    ('ADJUDICATED 2026-09-21 (content-level): 460.2.c.3 -> 465.2.c.4(+465.2.c.4.a) 致命伤害最小分配一致; '
     '323.5 经核对在现行规则中存在且内容一致(步骤3b 致命伤害摧毁), 无需重映射 -- 仅 460.2.x 为旧编号. '
     'judge-FAQ 引用旧版编号.',))
db.commit()
print('MR-4A-0005 corrected')
