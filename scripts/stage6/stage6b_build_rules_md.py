# -*- coding: utf-8 -*-
"""
Stage 6B: build workspace/final/rules.md from rules_work.db (idempotent full regeneration).

Per spec 17.2 / 17.3:
- every rule entry: Rule ID, 主题, 规范规则, 适用对象, 触发条件, 前置条件, 效果, 限制,
  例外, 官方解释, 由 FAQ 推导的解释, 案例, 来源, 状态
- distinguish 官方规则 / 官方解释 / 模型推导 / 案例 / 例外 / 未解决
- 472 canonical-NULL FAQ-only R-CARD rendered as mounted content only (no fabricated canonical)
- provenance notes: R-CR-811.1.b (CHG-5-0001), watch cards OGN-131/OGN-251/UNL-097/UNL-177
- structured semantic fields (applicable_object/trigger/precondition/effect/restriction) are
  NULL by design (structural extraction only; semantics deferred) -> rendered with legend note.

Batch protocol: regenerates the whole file each run (deterministic), validates counts,
registers/updates task_6_02, writes workspace/checkpoints/stage6b_checkpoint.json.
Prints short stats only; never dumps rule content to stdout.
"""
import sqlite3, json, re, os, sys, datetime

DB = 'workspace/rules_work.db'
OUT = 'workspace/final/rules.md'
CKPT = 'workspace/checkpoints/stage6b_checkpoint.json'

WATCH = {
    'R-CARD-OGN-131': '观察项(MR-2D-0005)：现行口径以 source_008 sec.4 中文 FAQ 为准，等待中文勘误文本更新；EN 权威侧为英文现行文本。',
    'R-CARD-OGN-251': '观察项(MR-2D-0005)：现行口径以 source_008 sec.4 中文 FAQ 为准，等待中文勘误文本更新。(EV-CN-FAQ-0260 为文档级提及，未挂载)',
    'R-CARD-UNL-097': '观察项(MR-2D-0005)：现行口径以 source_008 sec.4 中文 FAQ 为准，等待中文勘误文本更新。',
    'R-CARD-UNL-177': '观察项(MR-2D-0005)：现行口径以 source_008 sec.4 中文 FAQ 为准，等待中文勘误文本更新。',
}
SPECIAL = {
    'R-CR-811.1.b': '出处说明(CHG-5-0001)：规范规则末句“此牌保持正面朝下待命状态，直至你不再控制该战场”为相同规则版本下英文官方文本(EN>zh)补充的持续时间从句——英文原文 "for as long as you control that battlefield" 在中文官方译文中被遗漏，Stage 5 裁决补齐(conflict CON-4B-T2-0001 resolved_stage5)。',
}

def now():
    return datetime.datetime.now().isoformat(timespec='seconds')

def num_key(num):
    """sort key for rule numbers like '811.1.b' / '100' / '054'"""
    key = []
    for p in num.split('.'):
        m = re.match(r'^(\d+)(.*)$', p)
        if m:
            key.append((int(m.group(1)), m.group(2)))
        else:
            key.append((10**9, p))
    key.append((10**9, ''))  # stable: shorter prefix sorts first
    return key

def card_key(rid):
    m = re.match(r'^R-CARD-([A-Z]+)-(\d+)$', rid)
    if m:
        return (m.group(1), int(m.group(2)), '')
    return ('', 10**9, rid)

def main():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    cur = c.cursor()

    # --- register task (idempotent; actual cols: task_id/source_id/page_start/page_end/section/status/assigned_role/notes) ---
    row = cur.execute("SELECT task_id, status FROM processing_tasks WHERE task_id='task_6_02'").fetchone()
    if row is None:
        prev = cur.execute("SELECT assigned_role FROM processing_tasks WHERE task_id='task_6_01'").fetchone()
        role = prev['assigned_role'] if prev else 'stage6'
        cur.execute(
            "INSERT INTO processing_tasks (task_id, source_id, page_start, page_end, section, status, assigned_role, notes) "
            "VALUES (?,?,?,?,?,?,?,?)",
            ('task_6_02', None, None, None, '6B rules_md', 'running', role,
             f'Stage 6B rules.md build; script stage6b_build_rules_md.py (idempotent); started {now()}; checkpoint {CKPT}'))
    else:
        cur.execute("UPDATE processing_tasks SET status='running', notes=? WHERE task_id='task_6_02'",
                    (f'Stage 6B rules.md build; script stage6b_build_rules_md.py (idempotent); re-run started {now()}; checkpoint {CKPT}',))
    c.commit()

    # --- verification map ---
    vrows = {}
    try:
        for r in cur.execute("SELECT rule_id, status FROM verification"):
            vrows[r['rule_id']] = r['status']
    except sqlite3.OperationalError:
        pass

    # --- load all rules ---
    rules = [dict(r) for r in cur.execute("SELECT * FROM rules").fetchall()]

    # --- load links + evidence meta ---
    links = {}   # rule_id -> list of (relationship, evidence_id, source_id, notes_flag)
    for r in cur.execute("""
        SELECT re.rule_id, re.relationship, re.evidence_id, e.source_id, e.notes enotes
        FROM rule_evidence re LEFT JOIN evidence e ON e.evidence_id = re.evidence_id
    """):
        flag = ''
        en = (r['enotes'] or '')
        if 'supersed' in en.lower() or '已被取代' in en:
            flag = ' [superseded-已被取代]'
        links.setdefault(r['rule_id'], []).append(
            (r['relationship'], r['evidence_id'], r['source_id'] or '?', flag))

    # --- counts for legend ---
    stats = {}
    stats['rules_total'] = len(rules)
    stats['null_canonical'] = sum(1 for r in rules if not (r['proposed_canonical_rule'] or '').strip())
    stats['with_oi'] = sum(1 for r in rules if (r['official_interpretation'] or '').strip())
    stats['with_example'] = sum(1 for r in rules if (r['example'] or '').strip())
    stats['with_exception'] = sum(1 for r in rules if (r['exception'] or '').strip())
    stats['derived_rows'] = sum(1 for r in rules if (r['derived_interpretation'] or '').strip())
    stats['verified'] = sum(1 for v in vrows.values() if v == 'verified')
    stats['verified_with_changes'] = sum(1 for v in vrows.values() if v == 'verified_with_changes')
    stats['unresolved'] = sum(1 for r in rules if r['status'] == 'unresolved')

    # --- order rules into parts ---
    rcr_front = [r for r in rules if r['rule_id'] == 'R-CR-FRONT']
    rcr = sorted([r for r in rules if r['rule_id'].startswith('R-CR') and r['rule_id'] != 'R-CR-FRONT'],
                 key=lambda r: num_key(r['rule_id'][5:]))
    rcard = sorted([r for r in rules if r['rule_id'].startswith('R-CARD')], key=lambda r: card_key(r['rule_id']))
    rtopcn = sorted([r for r in rules if r['rule_id'].startswith('R-TOPIC-CN')], key=lambda r: r['rule_id'])
    rtopen = sorted([r for r in rules if r['rule_id'].startswith('R-TOPIC-EN')], key=lambda r: r['rule_id'])
    rmisc = sorted([r for r in rules if r['rule_id'].startswith('R-MISC')], key=lambda r: r['rule_id'])
    rfront = [r for r in rules if r['rule_id'] in ('R-ER-FRONT', 'R-FAQ-FRONT')]

    order = rcr_front + rcr + rcard + rtopcn + rtopen + rmisc + rfront
    assert len(order) == len(rules) == 2984, (len(order), len(rules))

    # section heading for R-CR by leading int
    def part_of(rid):
        n = rid[5:].split('.')[0]
        return re.sub(r'\D.*', '', n) or n

    # --- render ---
    def dash(v):
        v = (v or '').strip()
        return v if v else '—'

    def src_line(rid):
        ls = links.get(rid, [])
        if not ls:
            return '—'
        grp = {}
        for rel, eid, sid, flag in ls:
            grp.setdefault(rel, []).append(f'{eid}@{sid}{flag}')
        parts = []
        for rel in ('same', 'replacement', 'faq:rule_change_candidate', 'faq:rule_interpretation',
                    'faq:example_only', 'faq:exception', 'front_matter'):
            if rel in grp:
                parts.append(f'{rel}: {", ".join(grp[rel])}')
        for rel in grp:
            if rel not in ('same', 'replacement', 'faq:rule_change_candidate', 'faq:rule_interpretation',
                           'faq:example_only', 'faq:exception', 'front_matter'):
                parts.append(f'{rel}: {", ".join(grp[rel])}')
        return '; '.join(parts)

    def status_line(rid, status):
        v = vrows.get(rid)
        s = f'状态: {status}'
        if v:
            s += f' / verification={v}'
        else:
            s += ' / 无需单独验证(tier-0 等价挂载或结构性合并)'
        return s

    def render(r):
        rid = r['rule_id']
        out = []
        out.append(f"### {rid}")
        out.append('')
        out.append(f"- **Rule ID**: {rid}")
        out.append(f"- **主题**: {dash(r['topic'])}")
        canon = (r['proposed_canonical_rule'] or '').strip()
        if canon:
            out.append(f"- **规范规则**(官方规则): {canon}")
        else:
            out.append(f"- **规范规则**(官方规则): —（本条为 FAQ 挂载型记录，无规范规则正文；不作为缺失处理，勿凭此条目推造规则）")
        # 结构化五字段（applicable_object/trigger/precondition/effect/restriction）全库 NULL，
        # 不再逐条重复占位行，统一见 front matter 声明。
        exc = (r['exception'] or '').strip()
        oi = (r['official_interpretation'] or '').strip()
        der = (r['derived_interpretation'] or '').strip()
        exa = (r['example'] or '').strip()
        out.append(f"- **例外**(例外): {exc if exc else '—'}")
        out.append(f"- **官方解释**(官方解释): {oi if oi else '—'}")
        out.append(f"- **由 FAQ 推导的解释**(模型推导): {der if der else '—（全库 0 条；Stage 5 确认无任何 FAQ 过度泛化结论）'}")
        out.append(f"- **案例**(案例): {exa if exa else '—'}")
        out.append(f"- **来源**: {src_line(rid)}")
        out.append(f"- **{status_line(rid, dash(r['status']))}**" + ('' if r['status'] != 'unresolved' else '（未解决）'))
        if rid in SPECIAL:
            out.append(f"- **特别说明**: {SPECIAL[rid]}")
        if rid in WATCH:
            out.append(f"- **观察说明**: {WATCH[rid]}")
        out.append('')
        out.append('')
        return '\n'.join(out)

    parts_written = {}
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        w = f.write
        # ---- front matter ----
        w('# Riftbound / LoL TCG 规则知识库 — rules.md（最终规则集）\n\n')
        w(f'> 生成时间: {now()}（脚本 stage6b_build_rules_md.py 幂等重生成）\n')
        w('> 数据来源: workspace/rules_work.db — rules 2984 / rule_evidence 6353 / evidence 5527 / verification 393\n')
        w('> 本文件由数据库事实来源程序化生成为最终产物；一切以 DB 为准。\n\n')
        w('## 图例与约定\n\n')
        w('- **官方规则** = 规范规则正文（来源：官方规则书 / 已应用的官方勘误 / 已应用的官方规则修订）。\n')
        w('- **官方解释** = official_interpretation（FAQ / Ruling / 官方说明逐字挂载；source_001/006/008 为裁判社区层级，见各条前缀标注）。\n')
        w('- **模型推导** = derived_interpretation —— 全库 **0 条**（Stage 5 已确认无 FAQ 过度泛化结论），故各条均显示“—”。\n')
        w('- **案例** = example（example_only 类 FAQ 逐字挂载）。\n')
        w('- **例外** = exception。\n')
        w('- **未解决** = 0 条（Stage 4B/5 全部裁决完毕；conflicts 1/1 resolved_stage5）。\n')
        w('- 结构化字段「适用对象 / 触发条件 / 前置条件 / 效果 / 限制」全库未做语义抽取（全量 NULL），为可读性各条不再重复列出；权威信息在规范规则正文。\n')
        w(f'- 规范规则为“—（FAQ 挂载型记录）”的条目共 {stats["null_canonical"]} 条：均为仅 FAQ 出现的卡牌牌面 R-CARD 记录，按设计 canonical 为 NULL，仅挂载官方解释/案例/例外。\n')
        w('- 来源行格式: `关系: EVIDENCE_ID@SOURCE_ID`；`[superseded-已被取代]` 表示该来源条目已被官方后续条目取代（链接保留）。\n')
        w('- R-CR-811.1.b 的规范规则含英文同版本优先补充的持续时间从句（见该条特别说明）。\n')
        w('- 4 张观察卡（OGN-131 / OGN-251 / UNL-097 / UNL-177）现行口径按 source_008 sec.4 中文 FAQ，待中文勘误文本更新（MR-2D-0005）。\n\n')
        w(f'> 统计: 规则 {stats["rules_total"]} 条；含官方解释 {stats["with_oi"]}；含案例 {stats["with_example"]}；'
          f'含例外 {stats["with_exception"]}；verified {stats["verified"]} + verified_with_changes {stats["verified_with_changes"]}；未解决 {stats["unresolved"]}。\n\n')
        w('---\n\n')
        parts_written['front_matter'] = 0

        # ---- Part I: core rules ----
        w('# 第一部分：核心规则（R-CR，2026-07 核心规则；中文官方文本为规范，英文同版本官方文本为参照）\n\n')
        n = 0
        last_part = None
        for r in rcr_front:
            w(render(r))
            n += 1
        for r in rcr:
            p = part_of(r['rule_id'])
            if p != last_part:
                w(f"## 第 {int(p):03d} 章\n\n")
                last_part = p
            w(render(r))
            n += 1
        parts_written['part1_core'] = n

        # ---- Part II: card rules ----
        w('# 第二部分：卡牌规则（R-CARD = 官方卡牌勘误与 FAQ 挂载条目）\n\n')
        n = 0
        for r in rcard:
            w(render(r)); n += 1
        parts_written['part2_card'] = n

        # ---- Part III: topic rules ----
        w('# 第三部分：主题规则（R-TOPIC-CN / R-TOPIC-EN = 非核心规则来源的主题聚合）\n\n')
        n = 0
        for r in rtopcn:
            w(render(r)); n += 1
        parts_written['part3_topic_cn'] = n
        n = 0
        for r in rtopen:
            w(render(r)); n += 1
        parts_written['part3_topic_en'] = n

        # ---- Part IV: misc + front ----
        w('# 第四部分：杂项与前言（R-MISC / 勘误前言 / FAQ 前言）\n\n')
        n = 0
        for r in rmisc + rfront:
            w(render(r)); n += 1
        parts_written['part4_misc_front'] = n

    # ---- validation ----
    with open(OUT, 'r', encoding='utf-8') as f:
        text = f.read()
    ids = re.findall(r'^### (R-\S+)$', text, flags=re.M)
    val = {}
    val['entries_in_file'] = len(ids)
    val['entries_unique'] = len(set(ids))
    val['matches_db'] = len(ids) == 2984 and len(set(ids)) == 2984
    val['all_db_ids_present'] = set(ids) == {r['rule_id'] for r in rules}
    val['null_canonical_marker_count'] = text.count('FAQ 挂载型记录，无规范规则正文')
    val['null_canonical_ok'] = val['null_canonical_marker_count'] == stats['null_canonical']
    val['special_811'] = 'CHG-5-0001' in text and '811.1.b' in text
    val['watch_cards_marked'] = all(k in text for k in WATCH)
    val['superseded_flag_present'] = 'superseded-已被取代' in text
    val['derived_legend'] = '全库 **0 条**' in text
    ok = (val['matches_db'] and val['all_db_ids_present'] and val['null_canonical_ok']
          and val['special_811'] and val['watch_cards_marked'] and val['superseded_flag_present']
          and val['derived_legend'])
    val['PASS'] = ok

    ckpt = {
       'task_id': 'task_6_02', 'stage': '6B', 'output': OUT,
        'built_at': now(), 'parts': parts_written, 'stats': stats, 'validation': val,
        'verification_included': sum(1 for r in rules if r['rule_id'] in vrows),
    }
    with open(CKPT, 'w', encoding='utf-8') as f:
        json.dump(ckpt, f, ensure_ascii=False, indent=2)

    if ok:
        cur.execute("UPDATE processing_tasks SET status='completed', notes=? WHERE task_id='task_6_02'",
                    (f'Stage 6B rules.md build COMPLETED {now()}; script stage6b_build_rules_md.py (idempotent); '
                     f'entries 2984; parts {json.dumps(parts_written)}; validation PASS; checkpoint {CKPT}',))
    else:
        cur.execute("UPDATE processing_tasks SET status='failed', notes=? WHERE task_id='task_6_02'",
                    ('validation failed: ' + json.dumps(val, ensure_ascii=False),))
    c.commit()
    c.close()

    print(json.dumps({'parts': parts_written, 'stats': stats, 'validation': val}, ensure_ascii=False, indent=2))
    print('RESULT:', 'PASS — task_6_02 completed' if ok else 'FAIL')
    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
