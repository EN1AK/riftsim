# Stage 4A — Rule Clustering
# Maps every evidence row to a stable rule_id:
#   R-CR-<rule_number> / R-CR-FRONT   core rules (zh+en merged via AL-CR pairs)
#   R-CARD-<card_key>                 card errata + card-related FAQ/OE
#   R-ER-FRONT                        errata front matter
#   R-FAQ-FRONT                       faq/oe front matter
#   R-TOPIC-CN-XX / R-TOPIC-EN-XX     topic-only FAQ/OE clusters
#   R-MISC-<source_id>                FAQ/OE rows w/o topic/cards/refs
# Item-level commits per cluster. Validation + closeout at end.

import sqlite3, json, re, sys

DB = r'workspace/rules_work.db'
db = sqlite3.connect(DB)
db.execute('PRAGMA foreign_keys=OFF')
c = db.cursor()

stats = {}
warnings = []

# ---------- helpers ----------
rules_inserted = set()

def add_rule(rule_id, topic, status='pending_reconciliation', batch=None):
    if rule_id in rules_inserted:
        return False
    c.execute(
        "INSERT INTO rules (rule_id, topic, status) VALUES (?,?,?)",
        (rule_id, topic, status),
    )
    rules_inserted.add(rule_id)
    return True

def link(rule_id, evidence_id, relationship, confidence=None, notes=None):
    c.execute(
        "INSERT INTO rule_evidence (rule_id, evidence_id, relationship, confidence, notes) VALUES (?,?,?,?,?)",
        (rule_id, evidence_id, relationship, confidence, notes),
    )

def has_cards(card_ids):
    return bool(card_ids and card_ids not in ('[]', 'null'))

REF_PAT = re.compile(r'(?<![\d.])\d{3}(?:\.\d+[a-z]?)+')

# valid core rule_numbers (zh canonical)
valid_rule_numbers = {r[0] for r in c.execute(
    "SELECT DISTINCT rule_number FROM evidence WHERE source_type='rule' AND rule_number IS NOT NULL")}

# card name lookup (optional)
card_names = {}
try:
    cdb = sqlite3.connect(r'cards_bilingual.db')
    cc = cdb.cursor()
    tnames = [r[0] for r in cc.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    # find a table with id + name columns
    for t in tnames:
        cols = [r[1].lower() for r in cc.execute(f'PRAGMA table_info({t})')]
        if any('card' in x and ('id' in x or 'key' in x) for x in cols):
            idcol = None
            for cand in cols:
                if 'card' in cand and ('id' in cand or 'key' in cand):
                    idcol = cand
                    break
            en = next((x for x in cols if x in ('name_en', 'en_name', 'english_name', 'name')), None)
            zh = next((x for x in cols if x in ('name_zh', 'zh_name', 'chinese_name', 'name_cn')), None)
            if idcol:
                realcols = [r[1] for r in cc.execute(f'PRAGMA table_info({t})')]
                idreal = realcols[cols.index(idcol)]
                enreal = realcols[cols.index(en)] if en else None
                zhreal = realcols[cols.index(zh)] if zh else None
                for row in cc.execute(f"SELECT {idreal}, {enreal or 'NULL'}, {zhreal or 'NULL'} FROM {t}"):
                    card_names[str(row[0])] = (row[1], row[2])
                break
    cdb.close()
except Exception as e:  # keep going without names
    warnings.append(f'cards_bilingual.db lookup skipped: {e}')

def card_topic(key):
    n = card_names.get(key)
    if n and (n[0] or n[1]):
        return f"card:{key} ({' / '.join([x for x in n if x])})"
    return f"card:{key}"

# =====================================================================
# BATCH 4A-01: core rules (R-CR-*)
# =====================================================================
# alignment pair map: alignment_id -> (zh, en, relation)
pairs = c.execute(
    "SELECT evidence_a, evidence_b, relation FROM alignments WHERE alignment_id LIKE 'AL-CR-%'").fetchall()
en_heading = {r[1]: r[0] for r in c.execute(
    "SELECT heading, evidence_id FROM evidence WHERE source_language='en' AND source_type='rule'")}

n_rules = n_links = 0
trdiff = 0
for zh_id, en_id, relation in pairs:
    rn = c.execute("SELECT rule_number FROM evidence WHERE evidence_id=?", (zh_id,)).fetchone()[0]
    rule_id = f'R-CR-{rn}' if rn else 'R-CR-FRONT'
    h = en_heading.get(en_id) or ''
    topic = re.sub(r'^\d+\s*', '', h).strip() or (f'rule {rn}' if rn else 'front matter')
    if add_rule(rule_id, f'{rn} {topic}'.strip() if rn else 'Core Rules front matter', batch='4A-01'):
        n_rules += 1
    note = f'alignment={relation}'
    if relation == 'translation_difference':
        trdiff += 1
        note += '; see MR-3-CR translation_difference flag (Stage 4B/5)'
    link(rule_id, zh_id, 'same', 'high', note + '; zh canonical text (source_009)')
    link(rule_id, en_id, 'same', 'high', note + '; en official text (source_018, same version confirmed)')
    n_links += 2
    if n_links % 500 == 0:
        db.commit()
db.commit()
stats['core_rules'] = {'clusters': n_rules, 'links': n_links, 'translation_difference_pairs': trdiff}

# =====================================================================
# BATCH 4A-02: errata (R-CARD-*), errata front matter
# =====================================================================
er_rows = c.execute(
    "SELECT evidence_id, card_ids, target_rule_candidate, modification_type, confidence FROM evidence WHERE source_type='errata'").fetchall()
n_card_clusters = 0
n_er_links = 0
n_er_front = 0
er_cards = set()
for eid, card_ids, target, mtype, conf in er_rows:
    if not has_cards(card_ids):
        add_rule('R-ER-FRONT', 'Errata documents front matter', batch='4A-02')
        link('R-ER-FRONT', eid, 'front_matter', conf, 'errata doc header/front matter')
        n_er_front += 1
        continue
    for key in json.loads(card_ids):
        rid = f'R-CARD-{key}'
        if add_rule(rid, card_topic(key), batch='4A-02'):
            n_card_clusters += 1
        er_cards.add(key)
        note = f'errata target={target or "?"}; modification_type={mtype or "?"} (heuristic; scope per Stage 4B)'
        link(rid, eid, 'replacement', conf or 'medium', note)
        n_er_links += 1
    if n_er_links % 50 == 0:
        db.commit()
db.commit()
stats['errata'] = {'card_clusters_created': n_card_clusters, 'links': n_er_links, 'front_matter_links': n_er_front}

# =====================================================================
# BATCH 4A-03/04: FAQ/OE — explicit rule ref > card > topic > misc
# =====================================================================
faq_rows = c.execute(
    "SELECT evidence_id, source_id, source_language, topic, faq_question, faq_answer, "
    "faq_classification, card_ids, confidence FROM evidence "
    "WHERE source_type IN ('faq','official_explanation')").fetchall()

# pre-create topic clusters
topic_ids = {}
for lang, prefix in (('zh', 'R-TOPIC-CN'), ('en', 'R-TOPIC-EN')):
    topics = [r[0] for r in c.execute(
        "SELECT DISTINCT topic FROM evidence WHERE source_type IN ('faq','official_explanation') "
        "AND source_language=? AND topic IS NOT NULL AND topic != 'front_matter' ORDER BY topic", (lang,))]
    for i, t in enumerate(topics, 1):
        rid = f'{prefix}-{i:02d}'
        topic_ids[(lang, t)] = rid
        add_rule(rid, f'faq topic [{lang}]: {t}', batch='4A-03')
db.commit()

n_card_links = n_ref_links = n_topic_links = n_front = n_misc = 0
ref_unmapped = []
faq_card_set = set()

for eid, sid, lang, topic, q, a, cls, card_ids, conf in faq_rows:
    text = f'{q or ""} {a or ""}'
    rel = f'faq:{cls or "unclassified"}'
    linked = False

    if topic == 'front_matter':
        add_rule('R-FAQ-FRONT', 'FAQ / Official Explanation documents front matter', batch='4A-03')
        link('R-FAQ-FRONT', eid, 'front_matter', conf, f'faq/oe doc header (source {sid})')
        n_front += 1
        continue

    # 1) explicit rule-number references
    refs = sorted(set(REF_PAT.findall(text)))
    for ref in refs:
        if ref in valid_rule_numbers:
            rid = f'R-CR-{ref}'
            add_rule(rid, f'{ref} (referenced by FAQ)', batch='4A-03')
            link(rid, eid, rel, conf, 'explicit rule-number reference in faq text')
            n_ref_links += 1
            linked = True
        else:
            ref_unmapped.append((eid, ref))

    # 2) card entities
    if has_cards(card_ids):
        for key in json.loads(card_ids):
            rid = f'R-CARD-{key}'
            add_rule(rid, card_topic(key), batch='4A-03')
            faq_card_set.add(key)
            link(rid, eid, rel, conf, 'card entity mentioned in faq (stage3 entity resolution)')
            n_card_links += 1
            linked = True

    if linked:
        if (n_card_links + n_ref_links) % 80 == 0:
            db.commit()
        continue

    # 3) topic cluster
    rid = topic_ids.get((lang, topic or ''))
    if rid:
        link(rid, eid, rel, conf, f'topic-only cluster assignment; refine in Stage 4B')
        n_topic_links += 1
        continue

    # 4) misc fallback per source
    rid = f'R-MISC-{sid}'
    add_rule(rid, f'faq/oe ungrouped items ({sid}, lang={lang})', batch='4A-03')
    link(rid, eid, rel, conf, 'no topic/card/rule-ref; manual topic assignment in Stage 4B')
    n_misc += 1
    linked = True

db.commit()
n_faq_card_clusters = len(faq_card_set - er_cards)
stats['faq_oe'] = {
    'rule_ref_links': n_ref_links,
    'card_links': n_card_links,
    'topic_links': n_topic_links,
    'front_matter_links': n_front,
    'misc_links': n_misc,
    'topic_clusters': len(topic_ids),
    'new_card_clusters_from_faq': n_faq_card_clusters,
}
if ref_unmapped:
    warnings.append(f'FAQ rule refs with no current core rule target: {ref_unmapped}')

# =====================================================================
# 4A-04: validation
# =====================================================================
total_ev = c.execute("SELECT COUNT(*) FROM evidence").fetchone()[0]
mapped = c.execute("SELECT COUNT(DISTINCT evidence_id) FROM rule_evidence").fetchone()[0]
orphans = c.execute(
    "SELECT evidence_id FROM evidence WHERE evidence_id NOT IN (SELECT DISTINCT evidence_id FROM rule_evidence)").fetchall()
ruleless = c.execute(
    "SELECT rule_id FROM rules WHERE rule_id NOT IN (SELECT DISTINCT rule_id FROM rule_evidence)").fetchall()
n_rule_ids = c.execute("SELECT COUNT(*) FROM rules").fetchone()[0]
n_links = c.execute("SELECT COUNT(*) FROM rule_evidence").fetchone()[0]
dup_pair = c.execute(
    "SELECT rule_id, evidence_id, COUNT(*) FROM rule_evidence GROUP BY 1,2 HAVING COUNT(*)>1").fetchall()

stats['validation'] = {
    'evidence_total': total_ev,
    'evidence_mapped': mapped,
    'unmapped': [o[0] for o in orphans],
    'rules_total': n_rule_ids,
    'rule_evidence_links': n_links,
    'rules_without_evidence': [r[0] for r in ruleless],
    'duplicate_links': len(dup_pair),
}

# processing tasks
for tid, sid, desc in [
    ('task_4a_01', 'source_009/018', 'core rules clustering: 2382 AL-CR pairs -> R-CR-*'),
    ('task_4a_02', 'errata', 'errata clustering: -> R-CARD-*/R-ER-FRONT'),
    ('task_4a_03', 'faq/oe', 'faq/oe clustering: rule-ref > card > topic > misc'),
    ('task_4a_04', 'all', 'stage4a validation + closeout'),
]:
    c.execute(
        "INSERT INTO processing_tasks (task_id, source_id, page_start, page_end, section, status, assigned_role, notes) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (tid, sid, None, None, 'rule_clustering', 'completed', 'main_agent', desc))
db.commit()

print(json.dumps(stats, ensure_ascii=False, indent=2))
print('WARNINGS:', json.dumps(warnings, ensure_ascii=False))
