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

pats = {
    'wentii': re.compile(r'^问题\s*\d+[.:：]\s*\d*'),
    'Q_colon': re.compile(r'^Q[\d]*\s*[::]'),
    'A_colon': re.compile(r'^A[\d]*\s*[::]'),
    'sec_num': re.compile(r'^\d+[.、]\s*\S'),
    'bullet': re.compile(r'^[●•·]\s*'),
    'card_ref': re.compile(r'【[^】]+】'),
    'qa_head': re.compile(r'^(QA|Q&A)\b', re.I),
}

for sid, fn in files.items():
    txt = open(f'{EX}\\{fn}', encoding='utf-8').read()
    lines = txt.splitlines()
    counts = collections.Counter()
    samples = collections.defaultdict(list)
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith('===== PAGE'):
            continue
        for name, p in pats.items():
            if p.search(s):
                counts[name] += 1
                if len(samples[name]) < 4:
                    samples[name].append(s[:60])
    print(f'=== {sid} ({fn[:40]}) ===')
    for name in pats:
        if counts[name]:
            print(f'  {name}: {counts[name]}')
            for sm in samples[name][:3]:
                print(f'      e.g. {sm}')
    print()
