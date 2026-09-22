import re

EX = r'c:\Users\Mortis\Desktop\Workspace\riftsim\extracted'
files = {
    '001': r'loltcg_pdfs__01_2025-12-03_裁判FAQ_251023.txt',
    '005': r'loltcg_pdfs__05_2026-04-15_铸魂淬炼系列_官方FAQ_260114.txt',
    '006': r'loltcg_pdfs__06_2026-04-15_铸魂淬炼系列_裁判FAQ.txt',
    '007': r'loltcg_pdfs__07_2026-04-30_破限系列_官方FAQ.txt',
    '008': r'loltcg_pdfs__08_2026-05-13_破限系列_裁判FAQ_260511.txt',
    '011': r'loltcg_pdfs__11_2026-08-13_612b1cd53f9f41baaf3c8734c1881a3b.txt',
    '012': r'riftbound_en_rules__01_2025-10-24_Core_Rules_Patch_Notes.txt',
    '014': r'riftbound_en_rules__03_2025-12-05_Spiritforged_Patch_Notes.txt',
    '016': r'riftbound_en_rules__05_2026-03-30_Unleashed_Patch_Notes.txt',
    '019': r'riftbound_en_rules__08_2026-07-17_Vendetta_Patch_Notes.txt',
}

qmark = re.compile(r'^(问题\s*\d+\.\d+|[QＱ问]\d*\s*[:：]|\d+[.、]\s*\D|新问题|相关规则)')
rule_num = re.compile(r'^\d{3}(\.\d+)*\.?[a-z]?\.?$')
END_PUNCT = ('。', '；', '，', '、', '？', '！', '”', '）', '.', ':', '：', '”')
HEAD_SKIP = ('“', '（', '(', '《', '<', '【', '●', '•', '·', '-', '[')

out = []
for key, fn in files.items():
    lines = open(f'{EX}\\{fn}', encoding='utf-8').read().splitlines()
    out.append(f'===== {key} {fn[:45]} (lines={len(lines)}) =====')
    page = 0
    for i, ln in enumerate(lines):
        s = ln.strip()
        m = re.match(r'===== PAGE (\d+) =====', s)
        if m:
            page = int(m.group(1))
            continue
        if not s:
            continue
        is_rule = bool(rule_num.match(s))
        is_mark = bool(qmark.match(s))
        is_head = (len(s) <= 30 and not s.endswith(END_PUNCT)
                   and not s.startswith(HEAD_SKIP)
                   and not s[:2] in ('Q：','A：','Q:','A:','问：'))
        if is_rule or is_mark or is_head:
            tag = 'RULE' if is_rule else ('MARK' if is_mark else 'HEAD')
            out.append(f'  p{page:02d} L{i:4d} [{tag}] {s[:70]}')
    out.append('')

open('stage2d_skeleton_out.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written', len(out), 'lines')
