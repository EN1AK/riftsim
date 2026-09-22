import re, collections

EX = r'c:\Users\Mortis\Desktop\Workspace\riftsim\extracted'
files = {
    'source_001': r'loltcg_pdfs__01_2025-12-03_裁判FAQ_251023.txt',
    'source_005': r'loltcg_pdfs__05_2026-04-15_铸魂淬炼系列_官方FAQ_260114.txt',
    'source_006': r'loltcg_pdfs__06_2026-04-15_铸魂淬炼系列_裁判FAQ.txt',
    'source_007': r'loltcg_pdfs__07_2026-04-30_破限系列_官方FAQ.txt',
    'source_008': r'loltcg_pdfs__08_2026-05-13_破限系列_裁判FAQ_260511.txt',
    'source_011': r'loltcg_pdfs__11_2026-08-13_612b1cd53f9f41baaf3c8734c1881a3b.txt',
}

out = []
for sid, fn in files.items():
    txt = open(f'{EX}\\{fn}', encoding='utf-8').read()
    lines = txt.splitlines()
    first = collections.Counter()
    q_lines = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s or s.startswith('===== PAGE'):
            continue
        # first char distribution
        ch = s[0]
        if ch in 'QqAaＱＡ问题答旧新' or re.match(r'\d', ch):
            tok = s[:6]
            first[tok[0:2]] += 1
        if re.match(r'^[QＱ]', s):
            q_lines.append((i, s[:50]))
    out.append(f'=== {sid} ===')
    for tok, n in first.most_common(25):
        out.append(f'  {tok!r}: {n}')
    out.append(f'  Q-start lines: {len(q_lines)}')
    for i, s in q_lines[:3]:
        out.append(f'    L{i}: {s!r}')
    out.append('')

open('stage2d_markers_out.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written stage2d_markers_out.txt')
