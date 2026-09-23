import sqlite3, re
from pathlib import Path

SOURCES = {
 "source_001": ("loltcg_pdfs__01_2025-12-03_裁判FAQ_251023.txt", "zh"),
 "source_005": ("loltcg_pdfs__05_2026-04-15_铸魂淬炼系列_官方FAQ_260114.txt", "zh"),
 "source_006": ("loltcg_pdfs__06_2026-04-15_铸魂淬炼系列_裁判FAQ.txt", "zh"),
 "source_007": ("loltcg_pdfs__07_2026-04-30_破限系列_官方FAQ.txt", "zh"),
 "source_008": ("loltcg_pdfs__08_2026-05-13_破限系列_裁判FAQ_260511.txt", "zh"),
 "source_011": ("loltcg_pdfs__11_2026-08-13_612b1cd53f9f41baaf3c8734c1881a3b.txt", "zh"),
 "source_012": ("riftbound_en_rules__01_2025-10-24_Core_Rules_Patch_Notes.txt", "en"),
 "source_014": ("riftbound_en_rules__03_2025-12-05_Spiritforged_Patch_Notes.txt", "en"),
 "source_016": ("riftbound_en_rules__05_2026-03-30_Unleashed_Patch_Notes.txt", "en"),
 "source_019": ("riftbound_en_rules__08_2026-07-17_Vendetta_Patch_Notes.txt", "en"),
}
con = sqlite3.connect(r"workspace/rules_work.db")
PAGE_RE = re.compile(r"^===== PAGE (\d+) =====")
def norm(s):
    return re.sub(r"[\s　]+", "", s)
EN_NOISE = re.compile(r"©|RIOT GAMES|trademarks? of|PRIVACY NOTICE|TERMS OF SERVICE|COOKIE|website utilizes|Manage Preferences|RELATED ARTICLES", re.I)
for sid, (fname, lang) in SOURCES.items():
    pages = {}
    cur = 0
    for line in Path("extracted", fname).read_text(encoding="utf-8").splitlines():
        m = PAGE_RE.match(line.strip())
        if m:
            cur = int(m.group(1)); continue
        t = line.strip()
        if t:
            pages.setdefault(cur, []).append(t)
    # drop trailing noise lines (en footer) from the last page
    maxp = max(pages)
    tail_lines = pages[maxp]
    if lang == "en":
        tail_lines = [l for l in tail_lines if not EN_NOISE.search(l)]
    rows = {rid: norm(ot or "") for rid, ot in con.execute(
        "SELECT evidence_id, original_text FROM evidence WHERE source_id=? AND notes LIKE '%stage2d faq%'",
        (sid,)).fetchall()}
    uncovered = []
    for tl in tail_lines:
        n = norm(tl)
        if len(n) < 4:
            continue
        if not any(n in ot for ot in rows.values()):
            uncovered.append(tl)
    print(f"{sid} lastpage={maxp} uncovered_lines={len(uncovered)}")
    for u in uncovered[:6]:
        print(f"   ! {u[:95]}")
con.close()
