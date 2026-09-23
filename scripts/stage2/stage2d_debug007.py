import sys
sys.path.insert(0, ".")
from stage2d_extract_faq import tokenize, RULE_NO_LINE_RE, BARE_Q_RE, is_title_line

lines = open(r"extracted/loltcg_pdfs__07_2026-04-30_破限系列_官方FAQ.txt", encoding="utf-8").read().splitlines()
toks = tokenize(lines, "zh")
for i, (k, t, p) in enumerate(toks):
    if k != "LINE":
        continue
    if not (140 <= i <= 200):
        continue
    flags = []
    if RULE_NO_LINE_RE.match(t):
        flags.append("RULE")
    if BARE_Q_RE.search(t):
        flags.append("Q?")
    if is_title_line(t):
        flags.append("TITLE" + ("<=14" if len(t) <= 14 else f">14:{len(t)}"))
    print(f"{i:4d} p{p} [{'|'.join(flags):14s}] {t[:60]}")
