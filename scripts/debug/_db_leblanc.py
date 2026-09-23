# -*- coding: utf-8 -*-
import sqlite3
conn = sqlite3.connect(r"c:\Users\Mortis\Desktop\Workspace\riftsim\cards_bilingual.db")
cur = conn.cursor()
cur.execute("SELECT card_key, name_en, name_cn, sub_title_cn, set_id FROM cards WHERE name_en LIKE '%Leblanc%' OR name_cn LIKE '%乐芙兰%' OR sub_title_cn LIKE '%诡术%'")
for r in cur.fetchall():
    print(r)
conn.close()
