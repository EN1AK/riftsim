import sqlite3
conn = sqlite3.connect(r'c:\Users\Mortis\Desktop\Workspace\riftsim\cards_bilingual.db')
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
print('tables:', tables)
for t in tables:
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info({t})")]
    n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f'{t} ({n} rows): {cols}')
# sample
for t in tables:
    row = conn.execute(f"SELECT * FROM {t} LIMIT 1").fetchone()
    print(t, 'sample:', row)
conn.close()
