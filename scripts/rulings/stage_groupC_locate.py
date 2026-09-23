# -*- coding: utf-8 -*-
import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")

print("### 0006a: 005 中被废弃的 斯弗尔尚歌/厄斐琉斯 条目")
for kw in ("斯弗尔尚歌", "厄斐琉斯"):
    for r in con.execute(
            "SELECT evidence_id, substr(faq_question,1,50), substr(faq_answer,1,60) FROM evidence "
            "WHERE source_id='source_005' AND topic<>'front_matter' AND (faq_question LIKE ? OR faq_answer LIKE ?)",
            ("%" + kw + "%", "%" + kw + "%")):
        print("  ", r[0], "Q:", r[1].replace("\n", " "), "| A:", r[2].replace("\n", " ")[:50])

print()
print("### 0006b: 011 中声明废弃的条目（阿克尚）")
for r in con.execute(
        "SELECT evidence_id, substr(faq_question,1,60), substr(faq_answer,1,80) FROM evidence "
        "WHERE source_id='source_011' AND topic<>'front_matter' AND faq_answer LIKE '%不再适用%'"):
    print("  ", r[0], "Q:", r[1].replace("\n", " "), "| A:", r[2].replace("\n", " ")[:70])

print()
print("### 0012: 016 中 019 声明的 6 个主题条目定位")
topics = ["Lethal", "your damage", "Battlefield Ability", "Counting Targets", "accelerate", "Trigger Condition"]
for t in topics:
    for r in con.execute(
            "SELECT evidence_id, topic, substr(faq_question,1,60) FROM evidence WHERE source_id='source_016'"
            " AND topic<>'front_matter' AND (topic LIKE ? OR faq_question LIKE ?)",
            ("%" + t + "%", "%" + t + "%")):
        print(f"  [{t}]", r[0], "topic=", r[1], "| Q:", (r[2] or "").replace("\n", " ")[:55])

print()
print("### 0015: 007 prose_section 分布与分类")
for r in con.execute(
        "SELECT evidence_id, faq_classification, substr(faq_question,1,40) FROM evidence "
        "WHERE source_id='source_007' AND notes LIKE '%prose_section%' ORDER BY evidence_id"):
    print("  ", r[0], r[1], "|", (r[2] or "").replace("\n", " ")[:40])
con.close()
