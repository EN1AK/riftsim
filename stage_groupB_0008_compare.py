# -*- coding: utf-8 -*-
"""MR-2D-0008 detail: FAQ-embedded errata vs Stage 2C errata evidence, side by side."""
import re, sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

con = sqlite3.connect(r"workspace/rules_work.db")

def norm(s):
    if not s:
        return ""
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    s = s.replace("–", "-").replace("—", "-").replace("　", " ")
    s = re.sub(r"[\s]+", "", s)
    s = s.replace("【", "[").replace("】", "]").replace("<", "[").replace(">", "]")
    return s

def compare(faq_id, faq_label, faq_text, er_target_filter):
    rows = con.execute(
        "SELECT evidence_id, target_rule_candidate, corrected_fragment FROM evidence "
        "WHERE evidence_id LIKE 'EV-CN-ER-%' AND target_rule_candidate LIKE ?",
        (er_target_filter,)).fetchall()
    nf = norm(faq_text)
    if not rows:
        print(f"  [{faq_id}] {faq_label}: ⚠ 2C 无对应勘误条目 (filter={er_target_filter})")
        return
    for er_id, target, corrected in rows:
        nc = norm(corrected)
        if nf == nc:
            st = "✅ EXACT"
        elif nc and nc in nf:
            st = "✅ FAQ ⊇ 2C (2C 文本完整含于 FAQ)"
        elif nf and nf in nc:
            st = "🟡 2C ⊇ FAQ (FAQ 文本更短)"
        else:
            # rough prefix overlap
            k = 0
            for a, b in zip(nf, nc):
                if a != b:
                    break
                k += 1
            st = f"❌ DIFF (common prefix {k} chars)"
        print(f"  [{faq_id}] {faq_label}")
        print(f"      ↔ 2C [{er_id}] {target}: {st}")
        if "DIFF" in st or "🟡" in st:
            print(f"      FAQ: {nf[:180]}")
            print(f"      2C : {nc[:180]}")

print("=" * 78)
print("A. source_005 revised_block (18 卡 + 1 规则) ↔ source_004 铸魂淬炼 zh 勘误")
print("=" * 78)
blocks = con.execute(
    "SELECT evidence_id, faq_question, faq_answer FROM evidence WHERE source_id='source_005'"
    " AND notes LIKE '%revised_block%' ORDER BY evidence_id").fetchall()
for fid, q, a in blocks:
    name = re.sub(r"（(?:修订后|新文本)）|\s*\[(?:新文本|修订后)\]", "", q or "").strip()
    if name.startswith("规则"):
        print(f"  [{fid}] {q.strip()}: ⏩ 规则条文级修订，2C 勘误仅含卡牌，无对应（属 MR-2D-0007 范围）")
        continue
    compare(fid, name, a or "", "%" + name.split(" - ")[0] + "%")

print()
print("=" * 78)
print("B. source_008 内嵌勘误提及 (0260 沙丘亚龙注记 / 0277 永恩)")
print("=" * 78)
r = con.execute("SELECT faq_answer FROM evidence WHERE evidence_id='EV-CN-FAQ-0260'").fetchone()
seg = (r[0] or "")
i = seg.find("中文文本：")
j = seg.find("注：")
compare("EV-CN-FAQ-0260", "沙丘亚龙（FAQ 给出的勘误后中文文本）", seg[i:j] if i >= 0 and j > i else seg[:400], "%沙丘亚龙%")
r = con.execute("SELECT faq_answer FROM evidence WHERE evidence_id='EV-CN-FAQ-0277'").fetchone()
seg = (r[0] or "")
i = seg.find("勘误后文本为：")
compare("EV-CN-FAQ-0277", "永恩 - 一剑封尘（FAQ 内嵌“勘误后文本”）", seg[i:i + 200] if i >= 0 else seg[:240], "%永恩%")

print()
print("=" * 78)
print("C. source_011 内嵌勘误提及 (0323 星界灵鹭)")
print("=" * 78)
r = con.execute("SELECT faq_answer FROM evidence WHERE evidence_id='EV-CN-FAQ-0323'").fetchone()
seg = (r[0] or "")
i = seg.find("技能描述更新为：")
compare("EV-CN-FAQ-0323", "星界灵鹭（FAQ“技能描述更新为”）", seg[i:i + 200] if i >= 0 else seg[:240], "%星界灵鹭%")
con.close()
