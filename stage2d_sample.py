import sys

EX = r'c:\Users\Mortis\Desktop\Workspace\riftsim\extracted'
which = {
    '001': r'loltcg_pdfs__01_2025-12-03_裁判FAQ_251023.txt',
    '006': r'loltcg_pdfs__06_2026-04-15_铸魂淬炼系列_裁判FAQ.txt',
    '008': r'loltcg_pdfs__08_2026-05-13_破限系列_裁判FAQ_260511.txt',
    '005': r'loltcg_pdfs__05_2026-04-15_铸魂淬炼系列_官方FAQ_260114.txt',
    '007': r'loltcg_pdfs__07_2026-04-30_破限系列_官方FAQ.txt',
    '011': r'loltcg_pdfs__11_2026-08-13_612b1cd53f9f41baaf3c8734c1881a3b.txt',
    '012': r'riftbound_en_rules__01_2025-10-24_Core_Rules_Patch_Notes.txt',
    '014': r'riftbound_en_rules__03_2025-12-05_Spiritforged_Patch_Notes.txt',
    '016': r'riftbound_en_rules__05_2026-03-30_Unleashed_Patch_Notes.txt',
    '019': r'riftbound_en_rules__08_2026-07-17_Vendetta_Patch_Notes.txt',
}
key = sys.argv[1]
a, b = int(sys.argv[2]), int(sys.argv[3])
lines = open(f'{EX}\\{which[key]}', encoding='utf-8').read().splitlines()
for i in range(a, min(b, len(lines))):
    ln = lines[i].rstrip()
    if ln.strip():
        print(f'{i:4d}| {ln}')
