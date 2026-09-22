# -*- coding: utf-8 -*-
"""Group-A manual rulings: date/effective_date adjudication + typo confirm + MR closure.

Ruling rule: date = content-declared date (in-doc 'Last Updated'/'更新日期'/article byline
outranks file-name archive date; file-name date demoted to notes); effective_date = in-doc
declared effective date, else = date. date_confidence -> declared. evidence.date synced.
"""
import sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

con = sqlite3.connect(r"workspace/rules_work.db")

RULINGS = {
 # sid: (new_date, new_effective, note_append, mr_ids_closed)
 "source_001": ("2025-10-23", "2025-10-23",
    "Date ruling 2026-09-20 (MR-2D-0001): date=doc internal '最后更新时间：2025-10-23';"
    " file-name date 2025-12-03 = PDF archive/publish date",
    ["MR-2D-0001"]),
 "source_006": ("2026-01-14", "2026-01-14",
    "Date ruling 2026-09-20 (MR-2D-0002): date=doc internal '更新日期：2026/01/14';"
    " file-name date 2026-04-15 = PDF archive/publish date",
    ["MR-2D-0002"]),
 "source_008": ("2026-05-11", "2026-05-11",
    "Date ruling 2026-09-20 (MR-2D-0003): date=2026-05-11 (newest content date in bundled doc;"
    " sections 1-3 retained from 2026-04-16 judge FAQ edition); file-name date 2026-05-13 = publish date",
    ["MR-2D-0003"]),
 "source_013": ("2025-10-21", "2025-10-21",
    "Date ruling 2026-09-20 (MR-2C-0002): date=in-page 'Last Updated: 2025-10-21';"
    " file-name date 2025-10-28 = crawl/archive date",
    ["MR-2C-0002"]),
 "source_014": ("2025-12-05", "2025-12-12",
    "Date ruling 2026-09-20 (MR-2D-0011): date=byline 12/5/2025 (unchanged);"
    " effective_date=doc-declared 'effective date of December 12, 2025'",
    []),
 "source_016": ("2026-03-31", "2026-03-31",
    "Date ruling 2026-09-20 (MR-2D-0011): date=byline 'Rules and Releases | 3/31/2026'"
    " (1-day file-name offset); no separate effective date declared in doc",
    []),
 "source_019": ("2026-07-17", "2026-07-24",
    "Date ruling 2026-09-20 (MR-2D-0011): date=byline 7/17/2026 (unchanged);"
    " effective_date=doc-declared 'effective on July 24, 2026'",
    []),
 "source_020": ("2026-07-24", "2026-07-24",
    "Date ruling 2026-09-20 (MR-2C-0003): date=byline 'Announcements | 7/24/2026'"
    " (matches zh counterpart date); file-name date 2026-07-23 = crawl-date timezone offset",
    ["MR-2C-0003"]),
}

def close_mr(con, mrid, note):
    con.execute(
        "UPDATE manual_review SET issue_description=issue_description || ? WHERE item_id=?",
        (f" [2026-09-20 裁定关闭] {note}", mrid))

for sid, (nd, ne, note, mrs) in RULINGS.items():
    old = con.execute("SELECT date, effective_date FROM sources WHERE source_id=?", (sid,)).fetchone()
    con.execute(
        "UPDATE sources SET date=?, effective_date=?, date_confidence='declared',"
        " notes=COALESCE(notes,'') || ? WHERE source_id=?",
        (nd, ne, " | " + note, sid))
    n1 = con.execute("UPDATE evidence SET date=? WHERE source_id=?", (nd, sid)).rowcount
    print(f"{sid}: date {old[0]}->{nd}, eff {old[1]}->{ne}; evidence.date synced rows={n1}")

close_mr(con, "MR-2C-0002",
         "采用内文 Last Updated: 2025-10-21 为 date；文件名 2025-10-28 为抓取归档日期（sources.notes 已记）。")
close_mr(con, "MR-2C-0003",
         "采用 byline 7/24/2026 为 date（与 zh 对应勘误日期一致）；文件名 2026-07-23 为抓取日时区偏移。")
close_mr(con, "MR-2D-0001",
         "采用内文『最后更新时间：2025-10-23』为 date；文件名 2025-12-03 为 PDF 归档/发布日期。")
close_mr(con, "MR-2D-0002",
         "采用内文『更新日期：2026/01/14』为 date；文件名 2026-04-15 为 PDF 归档/发布日期。"
         "typo『Q：可以。』自动归并人工复核正确（归并为 A，notes 标 typo_fixed）。")
close_mr(con, "MR-2D-0003",
         "合订本以最新内容日期 2026-05-11 为 date；节级日期分层（1-3 节内容保留自 2026-04-16 版）"
         "与文件名发布日 2026-05-13 均记 sources.notes。")
close_mr(con, "MR-2D-0011",
         "014/019 的 date 保持 byline，effective_date 分别改为声明生效日 2025-12-12 / 2026-07-24；"
         "016 date 改 byline 2026-03-31，无独立生效日声明故 effective=date。")

con.commit()
print()
print("open MR remaining:")
for r in con.execute("SELECT item_id FROM manual_review WHERE issue_description NOT LIKE '%裁定关闭%' AND issue_description NOT LIKE '%复核完成%' ORDER BY item_id"):
    print("  ", r[0])
print("evidence date sanity:",
      con.execute("SELECT source_id, MIN(date), MAX(date) FROM evidence WHERE source_id IN ('source_001','source_006','source_008','source_013','source_016','source_020') GROUP BY source_id").fetchall())
con.close()
print("done")
