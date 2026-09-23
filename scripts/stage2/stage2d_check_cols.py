import sqlite3
conn = sqlite3.connect(r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db')
cols = [r[1] for r in conn.execute("PRAGMA table_info(evidence)")]
print(cols)
print('faq cols present:', all(x in cols for x in ['faq_question','faq_answer','faq_classification','related_cards']))
conn.close()
