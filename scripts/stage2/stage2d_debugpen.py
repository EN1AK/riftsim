import sys
sys.path.insert(0, ".")
from stage2d_extract_faq import tokenize, parse_pen

lines = open(r"extracted/riftbound_en_rules__03_2025-12-05_Spiritforged_Patch_Notes.txt", encoding="utf-8").read().splitlines()
toks = tokenize(lines, "en")
print("last 8 tokens:")
for t in toks[-8:]:
    print("  ", t[0], repr(t[1][:60]), "p", t[2])
front, items = parse_pen(toks)
print("items:", len(items))
for it in items[-3:]:
    print("Q:", it.q[:70])
    print("A:", it.answer_text()[:120])
    print("notes:", it.notes)
