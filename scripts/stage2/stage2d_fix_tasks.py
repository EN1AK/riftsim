import sqlite3, re, os

DB = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db'
EX = r'c:\Users\Mortis\Desktop\Workspace\riftsim\extracted'

files = {
    'source_001': r'loltcg_pdfs__01_2025-12-03_裁判FAQ_251023.txt',
    'source_005': r'loltcg_pdfs__05_2026-04-15_铸魂淬炼系列_官方FAQ_260114.txt',
    'source_006': r'loltcg_pdfs__06_2026-04-15_铸魂淬炼系列_裁判FAQ.txt',
    'source_007': r'loltcg_pdfs__07_2026-04-30_破限系列_官方FAQ.txt',
    'source_008': r'loltcg_pdfs__08_2026-05-13_破限系列_裁判FAQ_260511.txt',
    'source_011': r'loltcg_pdfs__11_2026-08-13_612b1cd53f9f41baaf3c8734c1881a3b.txt',
    'source_012': r'riftbound_en_rules__01_2025-10-24_Core_Rules_Patch_Notes.txt',
    'source_014': r'riftbound_en_rules__03_2025-12-05_Spiritforged_Patch_Notes.txt',
    'source_016': r'riftbound_en_rules__05_2026-03-30_Unleashed_Patch_Notes.txt',
    'source_019': r'riftbound_en_rules__08_2026-07-17_Vendetta_Patch_Notes.txt',
}

# page coverage in extracted txt
print('=== extracted txt page coverage ===')
for sid, fn in files.items():
    txt = open(os.path.join(EX, fn), encoding='utf-8').read()
    pages = sorted(set(int(m.group(1)) for m in re.finditer(r'===== PAGE (\d+) =====', txt)))
    print(f'{sid}: pages {pages[0]}..{pages[-1]} count={len(pages)} contiguous={pages == list(range(pages[0], pages[-1]+1))}')

conn = sqlite3.connect(DB)
c = conn.cursor()

# fix task page_end to match source page_count
print()
print('=== task fixes ===')
for sid in files:
    row = c.execute("SELECT task_id, page_start, page_end FROM processing_tasks WHERE source_id=?", (sid,)).fetchone()
    pc = c.execute("SELECT page_count FROM sources WHERE source_id=?", (sid,)).fetchone()[0]
    if row and row[2] != pc:
        c.execute("UPDATE processing_tasks SET page_end=?, notes = notes || ? WHERE task_id=?",
                  (pc, f' | Stage2D: page_end {row[2]}->{pc} (full coverage)', row[0]))
        print(f'{row[0]}: page_end {row[2]} -> {pc}')
    elif row:
        print(f'{row[0]}: ok ({row[1]}-{row[2]})')

# dedupe source_012 notes
n = c.execute("SELECT notes FROM sources WHERE source_id='source_012'").fetchone()[0]
if n:
    parts = [p.strip() for p in n.split('|') if p.strip()]
    seen, out = set(), []
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    fixed = ' | '.join(out)
    if fixed != n.strip(' |'):
        c.execute("UPDATE sources SET notes=? WHERE source_id='source_012'", (fixed,))
        print(f'source_012 notes deduped: {fixed}')

conn.commit()
print()
print('=== verify tasks ===')
for r in c.execute("SELECT task_id, source_id, page_start, page_end, status FROM processing_tasks WHERE status='pending' ORDER BY source_id"):
    print(r)
conn.close()
print('done')
