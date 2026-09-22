import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")
print("### 0004: 007 金克丝中英句式差异条目")
for r in con.execute(
        "SELECT evidence_id, substr(faq_question,1,50), substr(faq_answer,1,100) FROM evidence "
        "WHERE source_id='source_007' AND (faq_question LIKE '%金克丝%' OR faq_answer LIKE '%条件分句%'"
        " OR faq_answer LIKE '%英文卡牌文本%')"):
    print("  ", r[0], "Q:", r[1].replace("\n", " "))
    print("      A:", r[2].replace("\n", " ")[:90])
print()
print("### 0005: 008 第 4 节四卡条目")
for r in con.execute(
        "SELECT evidence_id, topic, substr(faq_question,1,40), substr(faq_answer,1,70) FROM evidence "
        "WHERE source_id='source_008' AND (faq_answer LIKE '%中文文本%' AND faq_answer LIKE '%英文文本%')"
        " ORDER BY evidence_id"):
    print("  ", r[0], "topic=", r[1], "Q:", (r[2] or "").replace("\n", " ")[:35])
    print("      A:", r[3].replace("\n", " ")[:65])
con.close()
