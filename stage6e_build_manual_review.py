# -*- coding: utf-8 -*-
"""
Stage 6E: build workspace/final/manual_review.md from the manual_review table.

Per spec 17.2 manual_review.md must record, for every item:
  Issue ID / Rule ID / 问题 / 来源 A / 来源 B / 冲突点 / 可能解释 / 无法自动裁决原因

All 186 items are formally closed; closure notes were appended in-place at the end
of issue_description as bracketed dated markers ([YYYY-MM-DD ...]). The entry
renderer splits issue_description at the first dated bracket into
  问题（原始记录）      original description, verbatim
  裁定结论（关闭记录）  closure/adjudication trail, verbatim
and adds a 状态 field = 已关闭(<final closure date>). If no closure marker were
found, the item would be rendered as 待复盘 — but validation enforces 186/186
closed, per coverage check C12 (manual_review 186 formally closed). Formally
closed items are never re-presented as pending.

Sections:
  1  MR-2C   (4)   Stage 2C 勘误抽取 — 跨语言勘误覆盖
  2  MR-2D   (15)  Stage 2D FAQ/官方说明抽取与人工复核
  3  MR-3-CR (161) Stage 3 中英核心规则对齐差异
  4  MR-4A   (6)   Stage 4A 聚类 — FAQ 引用旧规则编号

NULL fields are rendered with explicit markers, never fabricated. Long fields
are wrapped in dynamically sized fences (zero escaping, verbatim content).
rule_id values not in rules table (e.g. legacy rule numbers like 735.1.c) are
expected and reported separately from R-* cluster id orphans.

Idempotent: regenerates the whole markdown deterministically from the DB.
Registers/updates task_6_05, writes workspace/checkpoints/stage6e_checkpoint.json.
Prints short stats only.
"""
import sqlite3, json, os, re, sys, datetime

SRC = 'workspace/rules_work.db'
OUT = 'workspace/final/manual_review.md'
CKPT = 'workspace/checkpoints/stage6e_checkpoint.json'

CLOSED_RE = re.compile(r'关闭|结案|CLOSED|closed|复核完成')
DATE_BRACKET_RE = re.compile(r'\[\d{4}-\d{2}-\d{2}')

SECTIONS = [
    ('MR-2C', 'Stage 2C 勘误抽取 — 跨语言勘误覆盖',
     '中英勘误文档条目数 / 覆盖差异的裁决（Group-B 2026-09-20 裁定：中文独有勘误 '
     'zh_only_translation、跨文档一致性核对、cross_ref 指针）。'),
    ('MR-2D', 'Stage 2D FAQ / 官方说明抽取 — 人工复核与裁决',
     '日期归属、FAQ 取代关系、权威层级、旧版编号衔接、抽取结构复核等;'
     'Group-A/Group-C 裁定与人工复核均已完成。'),
    ('MR-3-CR', 'Stage 3 中英核心规则对齐差异',
     '中英核心规则逐条比对标记的 translation_difference;4B-B003 已全文复核裁决:'
     '160 条 equivalent_despite_diff（标点/数字/占位符等文字差异）,'
     '1 条语义分歧（R-CR-811.1.b → CON-4B-T2-0001,Stage 5 已修复 CHG-5-0001)。'),
    ('MR-4A', 'Stage 4A 聚类 — FAQ 引用旧规则编号',
     'FAQ 引用 2026-07 核心规则中不存在的旧规则编号;4B-B005 已逐条核验后继条文'
     '覆盖（successor coverage verified)并结案。'),
]

def now():
    return datetime.datetime.now().isoformat(timespec='seconds')

def fence_for(text):
    mx = 2
    for m in re.finditer(r'`+|~+', text):
        mx = max(mx, len(m.group(0)))
    return '`' * (mx + 1)

def num_key(item_id):
    return int(item_id.rsplit('-', 1)[1])

def load(cur):
    rows = [dict(r) for r in cur.execute("SELECT * FROM manual_review")]
    rules = {r['rule_id'] for r in cur.execute("SELECT rule_id FROM rules")}
    return rows, rules

def md_entry(r):
    """Render one manual_review row."""
    desc = r['issue_description'] or ''
    m = DATE_BRACKET_RE.search(desc)
    if m:
        problem = desc[:m.start()].strip()
        verdict = desc[m.start():].strip()
    else:
        problem, verdict = desc.strip(), ''
    closed = bool(CLOSED_RE.search(verdict))
    dates = re.findall(r'\[(\d{4}-\d{2}-\d{2})', verdict)
    status = ('**已关闭**（{}）'.format(dates[-1]) if closed and dates
              else ('**已关闭**' if closed else '**待复盘**（缺少裁定记录）'))
    lines = ['#### `{iid}`'.format(iid=r['item_id']), '']
    lines.append('| 字段 | 值 |')
    lines.append('| --- | --- |')
    def esc(v):
        return (v or '').replace('\\', '\\\\').replace('|', '\\|').replace('\n', ' ')
    rid = esc(r['rule_id']) if r['rule_id'] else '-（无关联规则 — 来源级问题）'
    lines.append('| Issue ID | `{}` |'.format(esc(r['item_id'])))
    lines.append('| Rule ID | `{}` |'.format(rid) if r['rule_id'] else '| Rule ID | {} |'.format(rid))
    lines.append('| 状态 | {} |'.format(status))
    lines.append('| 来源 A | {} |'.format('`' + esc(r['source_a']) + '`' if r['source_a'] else '-（NULL）'))
    lines.append('| 来源 B | {} |'.format('`' + esc(r['source_b']) + '`' if r['source_b'] else '-（不适用/NULL）'))
    lines.append('')
    def block(title, text, null_marker):
        lines.append('**{}**:'.format(title))
        lines.append('')
        if text is None or text == '':
            lines.append(null_marker)
            lines.append('')
        else:
            f = fence_for(text)
            lines.extend((f, text, f, ''))
    block('问题（原始记录）', problem, '-（NULL — 原始问题描述缺失，未伪造）')
    block('冲突点', r['conflicting_points'], '-（NULL — 无独立冲突点记录）')
    block('可能解释', r['possible_explanation'], '-（NULL — 无独立解释记录）')
    block('无法自动裁决原因', r['cannot_auto_resolve_reason'], '-（NULL — 无独立记录）')
    if verdict:
        f = fence_for(verdict)
        lines.append('**裁定结论（关闭记录）**:')
        lines.append('')
        lines += [f, verdict, f, '']
    else:
        lines.append('**裁定结论（关闭记录）**:-（无独立记录）')
        lines.append('')
    return '\n'.join(lines), closed

def main():
    c = sqlite3.connect(SRC)
    c.row_factory = sqlite3.Row
    cur = c.cursor()

    # --- register task (idempotent) ---
    row = cur.execute(
        "SELECT task_id, status FROM processing_tasks WHERE task_id='task_6_05'").fetchone()
    note = (f'Stage 6E manual_review.md build; script stage6e_build_manual_review.py '
            f'(idempotent); output {OUT}; checkpoint {CKPT}; started {now()}')
    if row is None:
        prev = cur.execute(
            "SELECT assigned_role FROM processing_tasks WHERE task_id='task_6_01'").fetchone()
        role = prev['assigned_role'] if prev else 'agent'
        cur.execute(
            "INSERT INTO processing_tasks (task_id, source_id, page_start, page_end, section, "
            "status, assigned_role, notes) VALUES (?,?,?,?,?,?,?,?)",
            ('task_6_05', None, None, None, 'stage6e_manual_review', 'running', role, note))
    else:
        cur.execute("UPDATE processing_tasks SET status='running', notes=? WHERE task_id='task_6_05'",
                    (note,))
    c.commit()

    rows, known_rules = load(cur)
    total = len(rows)
    assert total == 186, f'manual_review rows {total} != 186'
    by_sec = {}
    for r in rows:
        matched = False
        for prefix, _, _ in SECTIONS:
            if r['item_id'].startswith(prefix + '-'):
                by_sec.setdefault(prefix, []).append(r)
                matched = True
                break
        assert matched, 'unknown prefix: ' + r['item_id']
    for v in by_sec.values():
        v.sort(key=lambda r: num_key(r['item_id']))

    date_dist = {}
    for r in rows:
        ds = re.findall(r'\[(\d{4}-\d{2}-\d{2})', r['issue_description'] or '')
        if ds:
            date_dist[ds[-1]] = date_dist.get(ds[-1], 0) + 1

    L = []
    A = L.append
    A('# Manual Review — 人工复核与裁决记录')
    A('')
    A('> Stage 6E 产物。由 `stage6e_build_manual_review.py` 从 `workspace/rules_work.db` 的 '
      '`manual_review` 表全量幂等重建；事实来源为数据库，任何手工改动会被下次重建覆盖。')
    A('')
    A('- 构建时间: {}'.format(now()))
    A('- 条目总数: {} — **全部已正式关闭**（见每条 状态 字段与 裁定结论）。'.format(total))
    A('- 说明: 全部 186 项均已在各自阶段裁决关闭，本文件按已记录的裁决呈现，'
      '不存在待决项；正式关闭项不得被重新当作待决。裁定结论为追加在原始问题描述'
      '末尾的带日期结案记录，逐字保留。')
    A('')
    A('---')
    A('')
    A('## 汇总统计')
    A('')
    A('### 按批次（问题前缀）')
    A('')
    A('| 批次 | 数量 | 说明 |')
    A('| --- | ---: | --- |')
    for prefix, title, _blurb in SECTIONS:
        A('| {} | {} | {} |'.format(prefix, len(by_sec.get(prefix, [])), title))
    A('| **合计** | **{}** |  |'.format(total))
    A('')
    A('### 按最终关闭日期')
    A('')
    A('| 日期 | 数量 |')
    A('| --- | ---: |')
    for d in sorted(date_dist):
        A('| {} | {} |'.format(d, date_dist[d]))
    A('')
    A('- 无关联规则的来源级问题（rule_id 为 NULL）: {} 条'.format(
        sum(1 for r in rows if not r['rule_id'])))
    A('- rule_id 为旧规则编号而非当前 Rule Cluster ID（历史引用，非孤儿）: '
      '[MR-2D-0007 → 735.1.c]')
    A('')
    A('---')
    A('')

    written_ids = []
    closed_count = 0
    for idx, (prefix, title, blurb) in enumerate(SECTIONS, 1):
        sec = by_sec.get(prefix, [])
        A('## {}. {}（{} 条）'.format(idx, title, len(sec)))
        A('')
        A('> ' + blurb)
        A('')
        for r in sec:
            written_ids.append(r['item_id'])
            md, closed = md_entry(r)
            closed_count += 1 if closed else 0
            A(md)
    A('---')
    A('')
    A('*End of manual_review.md — {} entries, all formally closed. '
      '复核请回查 workspace/rules_work.db 的 manual_review 表。*'.format(total))

    text = '\n'.join(L) + '\n'
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)

    # ---------------- validation ----------------
    val = {}
    val['entries_written'] = len(written_ids)
    val['distinct_ids'] = len(set(written_ids))
    db_ids = {r['item_id'] for r in cur.execute("SELECT item_id FROM manual_review").fetchall()}
    val['count_match'] = (len(written_ids) == 186 and len(set(written_ids)) == 186)
    val['id_set_match'] = (set(written_ids) == db_ids)
    val['all_closed'] = (closed_count == 186)
    # 状态 presented per entry: exactly 186 已关闭, 0 待复盘
    entries_region = text[text.index('## 1. '):]
    val['status_closed_headers'] = entries_region.count('| 状态 | **已关闭**')
    val['status_pending_headers'] = entries_region.count('待复盘')
    # per-entry field presence
    miss = []
    for fl in ['| Issue ID |', '| Rule ID |', '| 状态 |', '| 来源 A |', '| 来源 B |',
               '**问题（原始记录）**', '**冲突点**', '**可能解释**', '**无法自动裁决原因**',
               '**裁定结论（关闭记录）**']:
        n = entries_region.count(fl)
        if n != 186:
            miss.append((fl, n))
    val['field_label_counts_ok'] = (len(miss) == 0)
    val['field_label_mismatches'] = miss[:5]
    text_ids = re.findall(r'^#### `(MR-\S+)`', text, flags=re.M)
    val['file_headers_match'] = (len(text_ids) == 186 and sorted(text_ids) == sorted(db_ids))
    # orphan check on R-* cluster ids; legacy rule numbers (e.g. 735.1.c) expected
    orphans, legacy = [], []
    for r in rows:
        rid = r['rule_id']
        if not rid:
            continue
        if rid.startswith('R-') and rid not in known_rules:
            orphans.append((r['item_id'], rid))
        elif not rid.startswith('R-'):
            legacy.append((r['item_id'], rid))
    val['orphan_rule_refs'] = sorted(orphans)
    val['legacy_rule_number_refs'] = sorted(legacy)
    val['file_size_bytes'] = os.path.getsize(OUT)
    val['section_counts'] = {p: len(by_sec.get(p, [])) for p, _, _ in SECTIONS}
    val['PASS'] = (val['count_match'] and val['id_set_match'] and val['all_closed']
                   and val['status_closed_headers'] == 186
                   and val['status_pending_headers'] == 0
                   and val['file_headers_match'] and not orphans
                   and val['field_label_counts_ok'])

    ckpt = {
        'task_id': 'task_6_05', 'stage': '6E', 'output': OUT, 'built_at': now(),
        'stats': {'items': total, 'all_closed': val['all_closed'],
                  'sections': val['section_counts'],
                  'close_date_distribution': date_dist,
                  'null_rule_id_items': sum(1 for r in rows if not r['rule_id']),
                  'legacy_rule_number_refs': len(legacy),
                  'file_size_bytes': val['file_size_bytes']},
        'validation': val,
    }
    os.makedirs(os.path.dirname(CKPT), exist_ok=True)
    with open(CKPT, 'w', encoding='utf-8') as f:
        json.dump(ckpt, f, ensure_ascii=False, indent=2)

    if val['PASS']:
        cur.execute(
            "UPDATE processing_tasks SET status='completed', notes=? WHERE task_id='task_6_05'",
            (f"Stage 6E manual_review.md build COMPLETED {now()}; script "
             f"stage6e_build_manual_review.py (idempotent); output {OUT}; entries 186 "
             f"(MR-2C 4 / MR-2D 15 / MR-3-CR 161 / MR-4A 6), all 186 formally closed "
             f"(closure trail verbatim), null rule_id 18, legacy-number ref 1 "
             f"(MR-2D-0007/735.1.c), validation PASS; checkpoint {CKPT}",))
    else:
        cur.execute(
            "UPDATE processing_tasks SET status='failed', notes=? WHERE task_id='task_6_05'",
            ('validation failed: ' + json.dumps(val, ensure_ascii=False),))
    c.commit()
    c.close()

    print(json.dumps({'stats': ckpt['stats'],
                      'validation': {k: v for k, v in val.items()
                                     if k not in ('section_counts', 'legacy_rule_number_refs')}},
                     ensure_ascii=False, indent=2))
    print('RESULT:', 'PASS - task_6_05 completed' if val['PASS'] else 'FAIL')
    sys.exit(0 if val['PASS'] else 1)

if __name__ == '__main__':
    main()
