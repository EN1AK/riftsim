import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")
print("### 011 阿克尚条目")
for r in con.execute(
        "SELECT evidence_id, substr(faq_question,1,60), substr(faq_answer,1,120) FROM evidence "
        "WHERE source_id='source_011' AND (faq_question LIKE '%阿克尚%' OR faq_answer LIKE '%阿克尚%'"
        " OR faq_answer LIKE '%斯弗尔尚歌%')"):
    print("  ", r[0], "Q:", r[1].replace("\n", " "))
    print("      A:", r[2].replace("\n", " "))
print()
print("### 019 front_matter 中关于 Unleashed FAQ 的声明")
r = con.execute("SELECT substr(original_text,1,900) FROM evidence WHERE source_id='source_019' AND topic='front_matter'").fetchone()
print((r[0] or "")[:900])
con.close()
