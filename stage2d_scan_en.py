import re, collections

files = {
    'source_012': r'extracted\riftbound_en_rules__01_2025-10-24_Core_Rules_Patch_Notes.txt',
    'source_014': r'extracted\riftbound_en_rules__03_2025-12-05_Spiritforged_Patch_Notes.txt',
    'source_016': r'extracted\riftbound_en_rules__05_2026-03-30_Unleashed_Patch_Notes.txt',
    'source_019': r'extracted\riftbound_en_rules__08_2026-07-17_Vendetta_Patch_Notes.txt',
}

marker_re = re.compile(r'^(NEW RULE|NEW SYSTEM|CLARIFIED|UPDATED|REMOVED|FIXED|CHANGED|REVISED|CORRECTED|RENAMED|ADDED|ERRATA|RULE CHANGE|SYSTEM UPDATE|DELETED|KEYWORD|NOTE)\b\s*:?\s*', re.I)

for sid, f in files.items():
    txt = open(f, encoding='utf-8').read()
    lines = txt.splitlines()
    counts = collections.Counter()
    total_lines = 0
    for ln in lines:
        s = ln.strip()
        m = marker_re.match(s)
        if m:
            counts[m.group(1).upper()] += 1
        if s:
            total_lines += 1
    print(f'{sid}: nonblank_lines={total_lines}, markers={dict(counts)}')
