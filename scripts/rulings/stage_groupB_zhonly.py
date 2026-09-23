# -*- coding: utf-8 -*-
"""Group B rulings: MR-2C-0001 & MR-2C-0004 -> zh-only confirmed; tag evidence scope."""
import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

con = sqlite3.connect(r"workspace/rules_work.db")

# MR-2C-0004 正文列名（15 翻译勘误 + 4 翻译优化） -> EV-CN-ER targets
ZH_ONLY_003 = ["倾颓宫殿","击退","苍蓝雕纹魔像","圣裁之刻","宏伟广场","卡尔萨斯 - 永恒颂葬",
               "厄运小姐 - 海盗","伊泽瑞尔-奥法逸才","黛安娜-皎月化身","兰博 - 热力全开",
               "杰斯 – 推陈出新","临终仪式","蔚 - 铲除者","咂魂者","自适应机器人",
               "德莱文 - 血斧飞旋","暗巷神偷","奥恩的锻炉","帝王神坛"]
ZH_ONLY_004 = ["沉没神庙","遗忘丰碑"]

TAG = " | zh_only_translation (ruled 2026-09-20 per MR-2C-0004/0001): no EN errata counterpart; zh text authoritative"

ids = []
for t in ZH_ONLY_003:
    r = con.execute(
        "SELECT evidence_id FROM evidence WHERE evidence_id LIKE 'EV-CN-ER-%' AND target_rule_candidate=?",
        (t,)).fetchall()
    ids += [x[0] for x in r]
missing = [t for t in ZH_ONLY_003 if not any(
    con.execute("SELECT 1 FROM evidence WHERE evidence_id=? AND target_rule_candidate=?",
                (i, t)).fetchone() for i in ids)]
for t in ZH_ONLY_004:
    r = con.execute(
        "SELECT evidence_id FROM evidence WHERE evidence_id LIKE 'EV-CN-ER-%' AND target_rule_candidate=?",
        (t,)).fetchall()
    ids += [x[0] for x in r]

# dedupe & tag (skip already tagged)
ids = sorted(set(ids))
n = 0
for i in ids:
    cur = con.execute("SELECT notes FROM evidence WHERE evidence_id=?", (i,)).fetchone()[0]
    if "zh_only_translation" in (cur or ""):
        continue
    con.execute("UPDATE evidence SET notes=COALESCE(notes,'') || ? WHERE evidence_id=?", (TAG, i))
    n += 1
print(f"tagged {n}/{len(ids)} rows with zh_only_translation")
print("ids:", ids)
for t in ZH_ONLY_003 + ZH_ONLY_004:
    hit = con.execute(
        "SELECT COUNT(*) FROM evidence WHERE evidence_id LIKE 'EV-CN-ER-%' AND target_rule_candidate=?",
        (t,)).fetchone()[0]
    if not hit:
        print("WARN: no errata row for", t)

def close_mr(mrid, note):
    con.execute("UPDATE manual_review SET issue_description=issue_description || ? WHERE item_id=? AND issue_description NOT LIKE '%裁定关闭%'",
                (f" [2026-09-20 裁定关闭] {note}", mrid))

close_mr("MR-2C-0001",
    "裁定为 zh 独有勘误：沉没神庙(EV-CN-ER-0079)/遗忘丰碑(EV-CN-ER-0080) 为中文侧独立勘误（EN Spiritforged "
    "Errata 无对应），中文文本为最终口径；相关 evidence 已标 zh_only_translation。")
close_mr("MR-2C-0004",
    "裁定为 zh 独有翻译勘误/翻译优化：按正文明细 15 张翻译勘误（倾颓宫殿…自适应机器人）+4 张翻译优化"
    "（德莱文/暗巷神偷/奥恩的锻炉/帝王神坛）= 19 张卡（标题『13 条』为历史笔误），均为中文本地化文本修订，"
    "不改 EN 原义，EN 无对应属正常；相关 evidence 已标 zh_only_translation。")
con.commit()
print("MR closed. open remaining:",
      [r[0] for r in con.execute("SELECT item_id FROM manual_review WHERE issue_description NOT LIKE '%裁定关闭%' AND issue_description NOT LIKE '%复核完成%'")])
con.close()
print("done")
