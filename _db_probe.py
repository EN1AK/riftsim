import sqlite3, json
conn = sqlite3.connect(r"c:\Users\Mortis\Desktop\Workspace\riftsim\cards_bilingual.db")
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("tables:", cur.fetchall())
cur.execute("PRAGMA table_info(cards)")
print("cols:", cur.fetchall())
cur.execute("SELECT COUNT(*) FROM cards")
print("count:", cur.fetchone())
cur.execute("SELECT card_key, name_en, name_cn FROM cards LIMIT 10")
for r in cur.fetchall():
    print(r)
conn.close()
