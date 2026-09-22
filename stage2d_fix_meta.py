import sqlite3

DB = r'c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db'
conn = sqlite3.connect(DB)
c = conn.cursor()

# --- 1. Fix languages (content verified from extracted txt heads) ---
fixes = [
    ('source_001', 'zh'),
    ('source_005', 'zh'),
    ('source_006', 'zh'),
    ('source_007', 'zh'),
    ('source_008', 'zh'),
    ('source_012', 'en'),
    ('source_014', 'en'),
    ('source_016', 'en'),
]
for sid, lang in fixes:
    c.execute("UPDATE sources SET language=? WHERE source_id=?", (lang, sid))
    print(f'{sid}: language -> {lang}')

# --- 2. Reclassify source_012 (Core Rules Patch Notes): rule -> official_explanation ---
# Verified content: "RIFTBOUND CORE RULES: PATCH NOTES ... rules patch ... clarifications"
c.execute("UPDATE sources SET source_type='official_explanation', "
          "notes=COALESCE(notes,'') || ' | Stage2D: reclassified rule->official_explanation (content = Core Rules Patch Notes, same class as source_014/016/019)' "
          "WHERE source_id='source_012'")
print('source_012: source_type -> official_explanation')

# --- 3. Add FAQ-specific columns to evidence ---
cols = [r[1] for r in c.execute("PRAGMA table_info(evidence)")]
new_cols = {
    'faq_question': 'TEXT',
    'faq_answer': 'TEXT',
    'faq_classification': 'TEXT',
    'related_cards': 'TEXT',
}
for name, typ in new_cols.items():
    if name not in cols:
        c.execute(f"ALTER TABLE evidence ADD COLUMN {name} {typ}")
        print(f'evidence: added column {name}')

conn.commit()

print()
print('=== verify ===')
for r in c.execute("SELECT source_id, source_type, language FROM sources WHERE source_id IN ('source_001','source_005','source_006','source_007','source_008','source_011','source_012','source_014','source_016','source_019') ORDER BY source_id"):
    print(r)

conn.close()
print('done')
