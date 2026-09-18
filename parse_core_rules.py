import re, json, os

BASE = os.path.dirname(__file__)
EX = os.path.join(BASE, "extracted")
KB = os.path.join(BASE, "kb")
os.makedirs(KB, exist_ok=True)

RULE_ID = re.compile(r"^(\d{3}(?:\.[A-Za-z0-9]+)*\.)\s*(.*)$")
PAGE = re.compile(r"^===== PAGE \d+ =====$")

def parse(path, stop_marker=None):
    entries = []
    cur = None
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n").strip()
            if PAGE.match(line):
                continue
            m = RULE_ID.match(line)
            # section headers like "100." followed by title line, or "700. Additional Rules"
            if m and (len(m.group(1)) >= 4):
                rid, rest = m.group(1)[:-1], m.group(2).strip()
                if cur:
                    entries.append(cur)
                cur = {"rule_id": rid, "text": rest}
            else:
                if cur is None:
                    continue
                cur["text"] += ("\n" if cur["text"] else "") + line
    if cur:
        entries.append(cur)
    # cleanup whitespace
    for e in entries:
        e["text"] = re.sub(r"[ \t]+", " ", e["text"]).strip()
    return entries

en = parse(os.path.join(EX, "riftbound_en_rules__07_2026-07-16_Core_Rules.txt"))
cn = parse(os.path.join(EX, "loltcg_pdfs__09_2026-07-23_6f47b6ebe57341a5bb5f4bed5548d051.txt"))

with open(os.path.join(KB, "core_rules_en.json"), "w", encoding="utf-8") as f:
    json.dump(en, f, ensure_ascii=False, indent=1)
with open(os.path.join(KB, "core_rules_cn.json"), "w", encoding="utf-8") as f:
    json.dump(cn, f, ensure_ascii=False, indent=1)

en_ids = [e["rule_id"] for e in en]
cn_ids = [e["rule_id"] for e in cn]
print("EN entries:", len(en_ids))
print("CN entries:", len(cn_ids))
en_set, cn_set = set(en_ids), set(cn_ids)
only_en = [i for i in en_ids if i not in cn_set]
only_cn = [i for i in cn_ids if i not in en_set]
print("only EN:", len(only_en), only_en[:30])
print("only CN:", len(only_cn), only_cn[:30])
# duplicates
from collections import Counter
dup_en = [k for k, v in Counter(en_ids).items() if v > 1]
dup_cn = [k for k, v in Counter(cn_ids).items() if v > 1]
print("dup EN:", dup_en[:20])
print("dup CN:", dup_cn[:20])
