import sqlite3

db = sqlite3.connect(r'workspace/rules_work.db')
c = db.cursor()

def search(label, pat, lang='zh', limit=15):
    print('-' * 66, label)
    rows = c.execute(
        "SELECT rule_number, substr(original_text,1,170) FROM evidence "
        "WHERE source_type='rule' AND source_language=? AND (rule_number LIKE ? OR original_text LIKE ?) "
        "ORDER BY rule_number LIMIT ?", (lang, pat[0], pat[1], limit)).fetchall()
    for rn, txt in rows:
        print(f'  {rn}: {txt}')
    if not rows:
        print('  (none)')

# FAQ-0011: cites 342.1.a (triggers ordering from focus player) vs stale 376.3.b.1
search('342.* 触发式技能加入结算链顺序', ('342.%', '%触发%焦点%'))
search('防守方身份 触发式技能 初始结算链', ('zzz%', '%防守方身份%'))
# FAQ-0031/0032: cites 440.1.a.x (special cleanup insertion) and cleanup steps 322.x
search('440.* 清理', ('440.%', '%特殊清理%'))
search('清理步骤内容 (清除标记伤害)', ('zzz%', '%清除所有单位的所有标记伤害%'))
# FAQ-0198: lethal damage, cites 323.5 cleanup task and 460.2.c.3 combat damage assignment
search('致命伤害/伤害标记清算', ('zzz%', '%非零伤害标记等同%'))
search('战斗伤害分配 460/461', ('461.%', '%分配伤害%'))
# FAQ-0216: HOT FEPR, cites 335.3 -- pending tasks + chain interaction
search('未决任务未决任务 HOT', ('zzz%', '%未决任务%'))
