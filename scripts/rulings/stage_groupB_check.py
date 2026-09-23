# -*- coding: utf-8 -*-
import sqlite3, sys, json
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
con = sqlite3.connect(r"workspace/rules_work.db")

print("### 1. MR-2C-0004: source_003 的 zh-only 翻译勘误条目（2C evidence）")
rows = con.execute(
    "SELECT evidence_id, target_rule_candidate, modification_type, substr(corrected_fragment,1,60),"
    " substr(notes,1,150) FROM evidence WHERE source_id='source_003' ORDER BY evidence_id").fetchall()
for r in rows:
    print(" ", r[0], r[2], "target=", r[1])
    print("    new:", (r[3] or "").replace("\n", " / ")[:90])

print()
print("### 2. MR-2C-0001: source_004 全部条目")
rows = con.execute(
    "SELECT evidence_id, target_rule_candidate, modification_type, substr(corrected_fragment,1,70)"
    " FROM evidence WHERE source_id='source_004' ORDER BY evidence_id").fetchall()
for r in rows:
    print(" ", r[0], r[2], "target=", r[1], "|", (r[3] or "").replace("\n"," / ")[:80])

print()
print("### 3. MR-2D-0008a: 005 的 FAQ 内嵌勘误（revised_block）")
rows = con.execute(
    "SELECT evidence_id, faq_question, substr(faq_answer,1,80) FROM evidence "
    "WHERE source_id='source_005' AND notes LIKE '%revised_block%' ORDER BY evidence_id").fetchall()
for r in rows:
    print(f"  {r[0]} {r[1][:45]}")

print()
print("### 4. MR-2D-0008b: 008 永恩内嵌勘误")
rows = con.execute(
    "SELECT evidence_id, faq_question, faq_answer FROM evidence WHERE source_id='source_008'"
    " AND faq_answer LIKE '%勘误后文本%' ORDER BY evidence_id").fetchall()
for r in rows:
    print(f"  {r[0]} Q: {(r[1] or '')[:60]}")
    print("   A:", (r[2] or "")[:260].replace("\n", " / "))

print()
print("### 5. MR-2D-0008c: 011 星界灵鹭内嵌勘误")
rows = con.execute(
    "SELECT evidence_id, faq_question, faq_answer FROM evidence WHERE source_id='source_011'"
    " AND faq_answer LIKE '%已受到勘误%' ORDER BY evidence_id").fetchall()
for r in rows:
    print(f"  {r[0]} Q: {(r[1] or '')[:60]}")
    i = (r[2] or "").find("已受到勘误")
    print("   A:", (r[2] or "")[max(0,i-50):i+260].replace("\n", " / "))

print()
print("### 6. 2C 勘误 evidence 全部 target 清单（zh）")
rows = con.execute(
    "SELECT evidence_id, target_rule_candidate, substr(corrected_fragment,1,50) FROM evidence "
    "WHERE evidence_id LIKE 'EV-CN-ER-%' AND topic<>'front_matter' ORDER BY evidence_id").fetchall()
for r in rows:
    print(" ", r[0], r[1], "|", (r[2] or "").replace("\n", " / ")[:60])

print()
print("### 7. 2C 勘误 EN target 清单")
rows = con.execute(
    "SELECT evidence_id, target_rule_candidate, substr(corrected_fragment,1,50) FROM evidence "
    "WHERE evidence_id LIKE 'EV-EN-ER-%' AND topic<>'front_matter' ORDER BY evidence_id").fetchall()
for r in rows:
    print(" ", r[0], r[1], "|", (r[2] or "").replace("\n", " / ")[:60])
con.close()
