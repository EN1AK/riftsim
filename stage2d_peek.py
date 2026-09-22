import os, io

files = [
    (r'extracted\loltcg_pdfs__01_2025-12-03_裁判FAQ_251023.txt', 'source_001'),
    (r'extracted\loltcg_pdfs__05_2026-04-15_铸魂淬炼系列_官方FAQ_260114.txt', 'source_005'),
    (r'extracted\loltcg_pdfs__06_2026-04-15_铸魂淬炼系列_裁判FAQ.txt', 'source_006'),
    (r'extracted\loltcg_pdfs__07_2026-04-30_破限系列_官方FAQ.txt', 'source_007'),
    (r'extracted\loltcg_pdfs__08_2026-05-13_破限系列_裁判FAQ_260511.txt', 'source_008'),
    (r'extracted\loltcg_pdfs__11_2026-08-13_612b1cd53f9f41baaf3c8734c1881a3b.txt', 'source_011'),
    (r'extracted\riftbound_en_rules__01_2025-10-24_Core_Rules_Patch_Notes.txt', 'source_012'),
    (r'extracted\riftbound_en_rules__03_2025-12-05_Spiritforged_Patch_Notes.txt', 'source_014'),
    (r'extracted\riftbound_en_rules__05_2026-03-30_Unleashed_Patch_Notes.txt', 'source_016'),
    (r'extracted\riftbound_en_rules__08_2026-07-17_Vendetta_Patch_Notes.txt', 'source_019'),
]

out = io.StringIO()
for f, sid in files:
    if not os.path.exists(f):
        out.write(f'### {sid}: MISSING {f}\n\n')
        continue
    txt = open(f, encoding='utf-8').read()
    out.write(f'### {sid}  {os.path.basename(f)}  chars={len(txt)} lines={txt.count(chr(10))+1}\n')
    # show first 600 chars
    out.write('--- head ---\n')
    out.write(txt[:600].replace('\n', '\\n\n'))
    out.write('\n------------\n\n')

open('stage2d_peek_out.txt', 'w', encoding='utf-8').write(out.getvalue())
print('written stage2d_peek_out.txt')
