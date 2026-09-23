# -*- coding: utf-8 -*-
"""
Stage 6D: build workspace/final/change_log.md from the changes table of rules_work.db.

Per spec 17.2 change_log.md must record, for every change:
  rule_id / original_content / new_content / source_type / source_language /
  source_document / version / date / modification_type / reason / final_conclusion

Output layout:
  header      build info + source-of-truth + idempotent regeneration note
  summary     counts by tier / modification_type / source_document
  section 1   CHG-4B-T2ER-* (222) — errata application (4B-B004), grouped by rule
  section 2   CHG-4B-T1F-* (6)    — FAQ-embedded rule changes (4B-B005, incorporated / not applied)
  section 3   CHG-4B-T3-* (38)    — post-core official changes (4B-B006; 37 applied + 1 incorporated)
  section 4   CHG-5-0001 (1)      — stage-5 verification fix (R-CR-811.1.b)

Content integrity:
  original_content / new_content rendered in fenced code blocks whose fence length is
  chosen dynamically (> max backtick run) so no escaping ever alters the text.
  NULL original_content (38 new_rule_addition rows) rendered as an explicit marker,
  never fabricated. NULL version (38 source_019 rows) rendered as '-（无版本）'.

Idempotent: regenerates the whole markdown deterministically from the DB on each run.
Registers/updates task_6_04, writes workspace/checkpoints/stage6d_checkpoint.json.
Prints short stats only; never dumps content to stdout.
"""
import sqlite3, json, os, re, sys, datetime

SRC = 'workspace/rules_work.db'
OUT = 'workspace/final/change_log.md'
CKPT = 'workspace/checkpoints/stage6d_checkpoint.json'

def now():
    return datetime.datetime.now().isoformat(timespec='seconds')

def fence_for(text):
    """Longest backtick/tilde run in text + 1, min 3, so content is never escaped."""
    mx = 2
    for m in re.finditer(r'`+|~+', text):
        mx = max(mx, len(m.group(0)))
    return '`' * (mx + 1)

SECTIONS = [
    ('CHG-4B-T2ER', 'CHG-4B-T2ER-%%',
     '勘误（Errata）应用 — 4B-B004',
     '官方勘误的 `corrected_fragment` 按日期升序应用到 R-CARD 规则的 canonical '
     '（同一规则多条勘误链式叠加，canonical 取最后一条；EN 对应勘误仅记录不改 canonical）。'),
    ('CHG-4B-T1F', 'CHG-4B-T1F-%%',
     'FAQ 内嵌规则变更 — 4B-B005',
     '过渡期官方 FAQ（source_007 / source_005）声明的旧规则对照；已核实全部并入 2026-07 核心规则'
     '（incorporated），仅记录、不重复应用。'),
    ('CHG-4B-T3', 'CHG-4B-T3-%%',
     '核心规则后官方改动 — 4B-B006',
     'source_019 Vendetta Patch Notes（生效 2026-07-24，晚于核心规则，为权威方）APPLIED 的'
     ' new_rule_addition 37 条 + source_005 EV-CN-FAQ-0055 已并入 809.1.c 记录 1 条。'
     '原始内容为 NULL 表示新增规则（无原始文本，未伪造）。'),
    ('CHG-5-', 'CHG-5-%%',
     'Stage 5 独立验证修复',
     'verification 阶段确认的修正：R-CR-811.1.b 英文同版本持续条款在中文官方文本中遗漏，'
     '补充中文译写（CON-4B-T2-0001 resolved_stage5）。'),
]

def load(cur):
    rows = {}
    for key, like, _, _ in SECTIONS:
        rows[key] = [dict(r) for r in cur.execute(
            "SELECT * FROM changes WHERE change_id LIKE ? ORDER BY change_id", (like,))]
    topics = {r['rule_id']: (r['topic'] or '')
              for r in cur.execute("SELECT rule_id, topic FROM rules")}
    known_rules = set(topics)
    return rows, topics, known_rules

def md_entry(ch, topics, null_markers):
    """Render one change row with all 11 spec fields."""
    topic = topics.get(ch['rule_id'], '')
    head = '#### {cid}  —  `{rid}`'.format(cid=ch['change_id'], rid=ch['rule_id'])
    if topic:
        head += '  —  {}'.format(topic)
    lines = [head, '']
    lines.append('| 字段 | 值 |')
    lines.append('| --- | --- |')
    def esc(v):
        return (v or '').replace('\\', '\\\\').replace('|', '\\|').replace('\n', ' ')
    ver = ch['version'] if ch['version'] not in (None, '') else '-（无版本）'
    lines.append('| rule_id | `{}` |'.format(esc(ch['rule_id'])))
    lines.append('| source_type | `{}` |'.format(esc(ch['source_type'])))
    lines.append('| source_language | `{}` |'.format(esc(ch['source_language'])))
    lines.append('| source_document | `{}` |'.format(esc(ch['source_document'])))
    lines.append('| version | `{}` |'.format(esc(ver)))
    lines.append('| date | `{}` |'.format(esc(ch['date'])))
    lines.append('| modification_type | `{}` |'.format(esc(ch['modification_type'])))
    lines.append('| reason | {} |'.format(esc(ch['reason'])))
    lines.append('| final_conclusion | {} |'.format(esc(ch['final_conclusion'])))
    lines.append('')
    orig = ch['original_content']
    if orig is None:
        lines.append('**original_content**: ' + null_markers)
        lines.append('')
    else:
        f = fence_for(orig)
        lines.append('**original_content**:')
        lines.append('')
        lines += [f, orig, f, '']
    newc = ch['new_content'] or ''
    f = fence_for(newc)
    lines.append('**new_content**:')
    lines.append('')
    lines += [f, newc, f, '']
    return '\n'.join(lines)

def main():
    c = sqlite3.connect(SRC)
    c.row_factory = sqlite3.Row
    cur = c.cursor()

    # --- register task (idempotent) ---
    row = cur.execute(
        "SELECT task_id, status FROM processing_tasks WHERE task_id='task_6_04'").fetchone()
    note = (f'Stage 6D change_log.md build; script stage6d_build_change_log.py (idempotent); '
            f'output {OUT}; checkpoint {CKPT}; started {now()}')
    if row is None:
        prev = cur.execute("SELECT assigned_role FROM processing_tasks WHERE task_id='task_6_01'").fetchone()
        role = prev['assigned_role'] if prev else 'agent'
        cur.execute(
            "INSERT INTO processing_tasks (task_id, source_id, page_start, page_end, section, "
            "status, assigned_role, notes) VALUES (?,?,?,?,?,?,?,?)",
            ('task_6_04', None, None, None, 'stage6d_change_log', 'running', role, note))
    else:
        cur.execute("UPDATE processing_tasks SET status='running', notes=? WHERE task_id='task_6_04'",
                    (note,))
    c.commit()

    rows, topics, known_rules = load(cur)
    total = sum(len(v) for v in rows.values())
    assert total == 267, f'changes rows {total} != 267'

    NULL_ORIG = '*（NULL — 本条为新增规则，无原始规则文本；未伪造）*'

    # totals by modification_type / source_document
    mt = {}
    docs = {}
    for v in rows.values():
        for ch in v:
            mt[ch['modification_type']] = mt.get(ch['modification_type'], 0) + 1
            key = '{} [{}|{}]'.format(ch['source_document'], ch['source_type'], ch['source_language'])
            docs[key] = docs.get(key, 0) + 1

    L = []
    A = L.append
    A('# Change Log — 规则变更日志')
    A('')
    A('> Stage 6D 产物。由 `stage6d_build_change_log.py` 从 `workspace/rules_work.db` 的 '
      '`changes` 表全量幂等重建；事实来源为数据库，任何手工改动会被下次重建覆盖。')
    A('')
    A('- 构建时间: {}'.format(now()))
    A('- 变更总数: {}（{} 个不同规则受影响）'.format(
        total, len({ch['rule_id'] for v in rows.values() for ch in v})))
    A('- 说明: original_content 为 NULL 的条目属于新增规则（new_rule_addition），'
      '以显式标记呈现，未伪造原始文本；version 为 NULL 的记录以 `-（无版本）` 呈现。')
    A('')
    A('---')
    A('')
    A('## 汇总统计')
    A('')
    A('### 按批次（change tier）')
    A('')
    A('| 批次 | 数量 | 说明 |')
    A('| --- | ---: | --- |')
    for key, _, title, _blurb in SECTIONS:
        A('| {} | {} | {} |'.format(key, len(rows[key]), title))
    A('| **合计** | **{}** |  |'.format(total))
    A('')
    A('### 按 modification_type')
    A('')
    A('| modification_type | 数量 |')
    A('| --- | ---: |')
    for k in sorted(mt, key=lambda k: (-mt[k], k)):
        A('| `{}` | {} |'.format(k, mt[k]))
    A('')
    A('### 按来源文档')
    A('')
    A('| 文档 | 数量 |')
    A('| --- | ---: |')
    for k in sorted(docs, key=lambda k: (-docs[k], k)):
        A('| `{}` | {} |'.format(k, docs[k]))
    A('')
    A('---')
    A('')

    written_ids = []
    for idx, (key, _like, title, blurb) in enumerate(SECTIONS, 1):
        A('## {}. {}（{} 条）'.format(idx, title, len(rows[key])))
        A('')
        A('> ' + blurb)
        A('')
        cur_rule = None
        for ch in rows[key]:
            written_ids.append(ch['change_id'])
            rid = ch['rule_id']
            if rid != cur_rule:
                cur_rule = rid
                topic = topics.get(rid, '')
                same = sum(1 for x in rows[key] if x['rule_id'] == rid)
                A('### `{}`{} — 本规则共 {} 条变更'.format(
                    rid, ('  —  ' + topic) if topic else '', same))
                A('')
            A(md_entry(ch, topics, NULL_ORIG))
    A('---')
    A('')
    A('*End of change_log.md — {} entries. 复核请回查 workspace/rules_work.db 的 changes 表。*'.format(total))

    text = '\n'.join(L) + '\n'
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)

    # ---------------- validation ----------------
    val = {}
    val['entries_written'] = len(written_ids)
    val['distinct_ids'] = len(set(written_ids))
    val['count_match'] = len(written_ids) == 267 and len(set(written_ids)) == 267
    db_ids = {r['change_id'] for r in
              cur.execute("SELECT change_id FROM changes").fetchall()}
    val['id_set_match'] = set(written_ids) == db_ids
    val['orphan_rule_refs'] = sorted({r for v in rows.values() for ch_ in v
                                      for r in [ch_['rule_id']] if r not in known_rules})
    text_ids = re.findall(r'^#### (CHG-\S+)', text, flags=re.M)
    val['id_headers_in_file'] = len(text_ids)
    val['file_headers_match'] = (len(text_ids) == 267 and sorted(text_ids) == sorted(db_ids))
    # per-entry field presence: in the entries region (from first entry section on),
    # each field label must appear exactly 267 times (once per entry)
    entries_region = text[text.index('## 1. '):]
    miss = []
    fields = ['| rule_id |', '| source_type |', '| source_language |', '| source_document |',
              '| version |', '| date |', '| modification_type |', '| reason |',
              '| final_conclusion |', '**original_content**', '**new_content**']
    for fl in fields:
        n = entries_region.count(fl)
        if n != 267:
            miss.append((fl, n))
    val['field_label_counts_ok'] = (len(miss) == 0)
    val['field_label_mismatches'] = miss[:5]
    val['file_size_bytes'] = os.path.getsize(OUT)
    val['tier_counts'] = {key: len(rows[key]) for key, _, _, _ in SECTIONS}
    val['PASS'] = (val['count_match'] and val['id_set_match'] and val['file_headers_match']
                   and not val['orphan_rule_refs'] and val['field_label_counts_ok'])

    ckpt = {
        'task_id': 'task_6_04', 'stage': '6D', 'output': OUT, 'built_at': now(),
        'stats': {'changes': total,
                  'tiers': val['tier_counts'],
                  'modification_types': mt,
                  'rules_affected': len({ch['rule_id'] for v in rows.values() for ch in v}),
                  'null_original_content': sum(1 for v in rows.values() for ch in v
                                               if ch['original_content'] is None),
                  'null_version': sum(1 for v in rows.values() for ch in v
                                      if ch['version'] in (None, '')),
                  'file_size_bytes': val['file_size_bytes']},
        'validation': val,
    }
    os.makedirs(os.path.dirname(CKPT), exist_ok=True)
    with open(CKPT, 'w', encoding='utf-8') as f:
        json.dump(ckpt, f, ensure_ascii=False, indent=2)

    if val['PASS']:
        cur.execute("UPDATE processing_tasks SET status='completed', notes=? WHERE task_id='task_6_04'",
                    (f"Stage 6D change_log.md build COMPLETED {now()}; script stage6d_build_change_log.py "
                     f"(idempotent); output {OUT}; entries 267 (T2ER 222 / T1F 6 / T3 38 / CHG-5 1), "
                     f"rules affected {ckpt['stats']['rules_affected']}, null original 38 (new_rule_addition), "
                     f"validation PASS; checkpoint {CKPT}",))
    else:
        cur.execute("UPDATE processing_tasks SET status='failed', notes=? WHERE task_id='task_6_04'",
                    ('validation failed: ' + json.dumps(val, ensure_ascii=False),))
    c.commit()
    c.close()

    print(json.dumps({'stats': ckpt['stats'],
                      'validation': {k: v for k, v in val.items() if k != 'tier_counts'}},
                     ensure_ascii=False, indent=2))
    print('RESULT:', 'PASS - task_6_04 completed' if val['PASS'] else 'FAIL')
    sys.exit(0 if val['PASS'] else 1)

if __name__ == '__main__':
    main()
