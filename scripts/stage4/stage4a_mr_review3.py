import sqlite3

db = sqlite3.connect(r'workspace/rules_work.db')
c = db.cursor()

def search(label, like_text, limit=12):
    print('-' * 66, label)
    rows = c.execute(
        "SELECT rule_number, substr(original_text,1,180) FROM evidence "
        "WHERE source_type='rule' AND source_language='zh' AND original_text LIKE ? "
        "ORDER BY rule_number LIMIT ?", (like_text, limit)).fetchall()
    for rn, txt in rows:
        print(f'  {rn}: {txt}')
    if not rows:
        print('  (none)')

def nums(label, prefix, limit=20):
    print('-' * 66, label)
    rows = c.execute(
        "SELECT rule_number, substr(original_text,1,180) FROM evidence "
        "WHERE source_type='rule' AND source_language='zh' AND rule_number LIKE ? "
        "ORDER BY rule_number LIMIT ?", (prefix, limit)).fetchall()
    for rn, txt in rows:
        print(f'  {rn}: {txt}')
    if not rows:
        print('  (none)')

# old 322.2/322.3/322.8 were cleanup steps (insert/remove marks, etc.) -> find current cleanup step list
nums('318-323 清理全流程', '3%')
search('清理步骤:标记/伤害', '%清理的步骤%')
search('清理:摧毁 伤害标记>=战力', '%伤害标记%视为被摧毁%')
search('清理:获得优先权/清除', '%清理条件%')
# old 376.3.b.1 trigger ordering for initial chain
nums('383.* 触发式技能章节', '383.%')
search('初始结算链 顺序 焦点', '%初始结算链%')
# old 342.1.a (trigger chain focus not passing) current 346.1? check 346.*
nums('346.*', '346.%')
