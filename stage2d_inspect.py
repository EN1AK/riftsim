import sqlite3, json, os

WS = r'c:\Users\Mortis\Desktop\Workspace\riftsim'
conn = sqlite3.connect(os.path.join(WS, 'workspace', 'rules_work.db'))
conn.row_factory = sqlite3.Row
c = conn.cursor()

SRC2D = ('source_001','source_005','source_006','source_007','source_008',
         'source_011','source_012','source_014','source_016','source_019')
ph = ','.join('?'*len(SRC2D))

print("=== sources rows for 2D ===")
for r in c.execute(f"SELECT * FROM sources WHERE source_id IN ({ph}) ORDER BY source_id", SRC2D):
    print(dict(r))

print("\n=== processing_tasks for 2D sources ===")
for r in c.execute(f"SELECT task_id, source_id, page_start, page_end, section, status, assigned_role, notes FROM processing_tasks WHERE source_id IN ({ph}) ORDER BY source_id, task_id", SRC2D):
    print(dict(r))

print("\n=== max evidence id for 2D prefixes ===")
for r in c.execute("SELECT evidence_id FROM evidence WHERE evidence_id LIKE 'EV-CN-FAQ%' OR evidence_id LIKE 'EV-EN-FAQ%' OR evidence_id LIKE 'EV-CN-OE%' OR evidence_id LIKE 'EV-EN-OE%' ORDER BY evidence_id DESC LIMIT 5"):
    print(tuple(r))
conn.close()

cddb = os.path.join(WS, 'cards_bilingual.db')
print("\n=== cards_bilingual.db exists?", os.path.exists(cddb))
if os.path.exists(cddb):
    cc = sqlite3.connect(cddb)
    cc.row_factory = sqlite3.Row
    cur = cc.cursor()
    names = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    print("tables:", names)
    for t in names:
        cols = cur.execute(f"PRAGMA table_info({t})").fetchall()
        print(f"--- {t} ({len(cols)} cols):", [ (x['name'], x['type']) for x in cols ])
        n = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"    rows: {n}")
        for r in cur.execute(f"SELECT * FROM {t} LIMIT 2"):
            print("   ", dict(r))
    cc.close()
