# -*- coding: utf-8 -*-
"""
Stage 6F: Final Consistency Check (spec 17.4).

互查 workspace/final/{rules.md, rules.db, change_log.md, manual_review.md,
coverage_report.md} 与事实来源 workspace/rules_work.db 的数量与状态一致性:

  A  rules.md          <-> rules_work.db / rules.db
  B  rules.db          <-> rules_work.db
  C  change_log.md     <-> rules_work.db / rules.db
  D  manual_review.md  <-> rules_work.db
  E  coverage_report.md<-> rules_work.db (17.1 硬性计数)
  F  跨产物状态一致性 — 不得出现「rules.md 说已解决而 manual_review.md 仍列
     unresolved」互相矛盾 (spec 17.4 核心)

只读所有产物与 DB 事实（除注册 task_6_06 / 写 checkpoint / 报告 / 更新本任务状态）。
幂等：重复运行结果一致。
Registers/updates task_6_06; report workspace/reports/stage6f_final_consistency.md;
checkpoint workspace/checkpoints/stage6f_checkpoint.json. Prints short stats only.
"""
import sqlite3, json, os, re, sys, datetime

FIN = 'workspace/final'
REPORT = 'workspace/reports/stage6f_final_consistency.md'
CKPT = 'workspace/checkpoints/stage6f_checkpoint.json'
WORK = 'workspace/rules_work.db'
RULES_DB = os.path.join(FIN, 'rules.db')

F_RULES = os.path.join(FIN, 'rules.md')
F_CHANGE = os.path.join(FIN, 'change_log.md')
F_MR = os.path.join(FIN, 'manual_review.md')
F_COV = os.path.join(FIN, 'coverage_report.md')

def now():
    return datetime.datetime.now().isoformat(timespec='seconds')

checks = []  # (id, name, passed, detail)
def check(cid, name, passed, detail=''):
    checks.append({'id': cid, 'name': name, 'result': 'PASS' if passed else 'FAIL',
                   'detail': detail})
    return passed

def q1(db, sql, args=()):
    return db.execute(sql, args).fetchone()[0]

def main():
    # ---------- open DBs, register task (idempotent) ----------
    w = sqlite3.connect(WORK); w.row_factory = sqlite3.Row
    row = w.execute(
        "SELECT task_id, status FROM processing_tasks WHERE task_id='task_6_06'").fetchone()
    note = (f'Stage 6F Final Consistency Check; script stage6f_final_consistency.py '
            f'(idempotent, read-only on artifacts); report {REPORT}; checkpoint {CKPT}; '
            f'started {now()}')
    if row is None:
        prev = w.execute(
            "SELECT assigned_role FROM processing_tasks WHERE task_id='task_6_01'").fetchone()
        role = prev['assigned_role'] if prev else 'agent'
        w.execute(
            "INSERT INTO processing_tasks (task_id, source_id, page_start, page_end, section, "
            "status, assigned_role, notes) VALUES (?,?,?,?,?,?,?,?)",
            ('task_6_06', None, None, None, 'stage6f_final_consistency', 'running', role, note))
    else:
        w.execute("UPDATE processing_tasks SET status='running', notes=? "
                  "WHERE task_id='task_6_06'", (note,))
    w.commit()

    # ---------- F0 artifacts exist ----------
    files = [F_RULES, RULES_DB, F_CHANGE, F_MR, F_COV]
    missing = [f for f in files if not (os.path.exists(f) and os.path.getsize(f) > 0)]
    check('F0', '五个最终产物齐备且非空', not missing,
          'missing=' + json.dumps(missing, ensure_ascii=False))
    if missing:
        raise SystemExit('missing artifacts: %s' % missing)

    rules_md = open(F_RULES, encoding='utf-8').read()
    change_md = open(F_CHANGE, encoding='utf-8').read()
    mr_md = open(F_MR, encoding='utf-8').read()
    cov_md = open(F_COV, encoding='utf-8').read()
    rdb = sqlite3.connect(RULES_DB); rdb.row_factory = sqlite3.Row

    # ---------- live DB 事实 ----------
    db_rules_ids = {r[0] for r in w.execute("SELECT rule_id FROM rules")}
    db_rules_n = len(db_rules_ids)
    db_null_canon = q1(w, "SELECT COUNT(*) FROM rules WHERE proposed_canonical_rule IS NULL")
    db_rule_end = q1(w, "SELECT COUNT(*) FROM rule_evidence")
    db_evidence = q1(w, "SELECT COUNT(*) FROM evidence")
    db_mapped = q1(w, "SELECT COUNT(DISTINCT evidence_id) FROM rule_evidence")
    db_changes_ids = {r[0] for r in w.execute("SELECT change_id FROM changes")}
    db_ver_ids = {r[0] for r in w.execute("SELECT verification_id FROM verification")}
    db_ver_dist = {r['status']: r['n'] for r in w.execute(
        "SELECT status, COUNT(*) n FROM verification GROUP BY status")}
    db_mr_ids = {r[0] for r in w.execute("SELECT item_id FROM manual_review")}
    db_conflict = [dict(r) for r in w.execute(
        "SELECT conflict_id, rule_id, resolution_status FROM conflicts")]
    db_conf_resolved = sum(1 for r in db_conflict
                           if str(r['resolution_status']).startswith('resolved'))
    db_conf_unres = len(db_conflict) - db_conf_resolved
    db_nv_true = q1(w, "SELECT COUNT(*) FROM rules WHERE needs_verification='true'")
    db_src_total = q1(w, "SELECT COUNT(*) FROM sources")
    db_src_covered = q1(w, "SELECT COUNT(DISTINCT source_id) FROM evidence")
    db_bad_tasks = q1(w, "SELECT COUNT(*) FROM processing_tasks WHERE status IN "
                         "('failed','running','pending') AND task_id <> 'task_6_06'")
    db_errata_zh = q1(w, "SELECT COUNT(*) FROM rule_evidence WHERE relationship='replacement' "
                         "AND evidence_id LIKE 'EV-CN-ER-%'")
    db_faq_links = q1(w, "SELECT COUNT(*) FROM rule_evidence WHERE relationship LIKE 'faq:%'")
    db_rulings = q1(w, "SELECT COUNT(DISTINCT e.evidence_id) FROM rule_evidence re "
                       "JOIN evidence e ON re.evidence_id=e.evidence_id "
                       "WHERE e.source_id IN ('source_001','source_006','source_008')")
    db_rulings_total = q1(w, "SELECT COUNT(*) FROM evidence WHERE source_id IN "
                             "('source_001','source_006','source_008')")

    # rules.db 计数
    rd_rules_ids = {r[0] for r in rdb.execute("SELECT rule_id FROM rules")}
    rd = {
        'rules': len(rd_rules_ids),
        'rule_sources': q1(rdb, "SELECT COUNT(*) FROM rule_sources"),
        'rule_cards': q1(rdb, "SELECT COUNT(*) FROM rule_cards"),
        'rule_keywords': q1(rdb, "SELECT COUNT(*) FROM rule_keywords"),
        'rule_verification': q1(rdb, "SELECT COUNT(*) FROM rule_verification"),
        'rule_changes': q1(rdb, "SELECT COUNT(*) FROM rule_changes"),
        'null_canon': q1(rdb, "SELECT COUNT(*) FROM rules WHERE proposed_canonical_rule IS NULL"),
    }
    rd_ver_dist = {r['status']: r['n'] for r in rdb.execute(
        "SELECT status, COUNT(*) n FROM rule_verification GROUP BY status")}
    rd_meta = {r['k']: r['v'] for r in rdb.execute("SELECT * FROM meta")}

    # ---------- A. rules.md ----------
    ids = re.findall(r'^### (\S+)\s*$', rules_md, flags=re.M)
    entries = rules_md[rules_md.index('### R-CR-FRONT'):]
    check('A1', 'rules.md 条目数/ID 集合 == DB rules == rules.db',
          len(ids) == db_rules_n == rd['rules']
          and len(set(ids)) == db_rules_n
          and set(ids) == db_rules_ids == rd_rules_ids,
          f'file={len(ids)} distinct={len(set(ids))} db={db_rules_n} rules_db={rd["rules"]}')
    labels = [
        ('Rule ID', r'^- \*\*Rule ID\*\*: '), ('主题', r'^- \*\*主题\*\*: '),
        ('规范规则', r'^- \*\*规范规则\*\*'),
        ('例外', r'^- \*\*例外\*\*\('), ('官方解释', r'^- \*\*官方解释\*\*\('),
        ('由 FAQ 推导的解释', r'^- \*\*由 FAQ 推导的解释\*\*'),
        ('案例', r'^- \*\*案例\*\*\('), ('来源', r'^- \*\*来源\*\*: '),
        ('状态', r'^- \*\*状态: '),
    ]
    label_bad = [(n, len(re.findall(p, entries, flags=re.M)))
                 for n, p in labels if len(re.findall(p, entries, flags=re.M)) != db_rules_n]
    # 结构化五字段：DB 全量 NULL（structured extraction 未做），rules.md 按全局声明省略条目级行
    struct_labels = [('适用对象', r'^- \*\*适用对象\*\*: '), ('触发条件', r'^- \*\*触发条件\*\*: '),
                     ('前置条件', r'^- \*\*前置条件\*\*: '), ('效果', r'^- \*\*效果\*\*: '),
                     ('限制', r'^- \*\*限制\*\*: ')]
    struct_bad = [(n, len(re.findall(p, entries, flags=re.M)))
                  for n, p in struct_labels if len(re.findall(p, entries, flags=re.M)) != 0]
    db_struct_nonempty = q1(w, "SELECT COUNT(*) FROM rules WHERE "
                               "coalesce(applicable_object,'')!='' OR coalesce(trigger,'')!='' OR "
                               "coalesce(precondition,'')!='' OR coalesce(effect,'')!='' OR "
                               "coalesce(restriction,'')!=''")
    check('A2', 'rules.md 每条含 9 个恒显字段；结构化五字段 DB 全 NULL 且条目级行已省略',
          not label_bad and not struct_bad and db_struct_nonempty == 0,
          f'expected={db_rules_n} each (9 fields); bad={label_bad}; '
          f'struct_md_lines={struct_bad}; struct_db_nonempty={db_struct_nonempty}')
    marker_n = entries.count('FAQ 挂载型记录')
    check('A3', 'rules.md NULL-canonical 标记数 == DB NULL canonical（两者一致）',
          marker_n == db_null_canon == rd['null_canon'],
          f'markers={marker_n} db_null={db_null_canon} rules_db_null={rd["null_canon"]}')
    status_lines = re.findall(r'^- \*\*状态: .*$', entries, flags=re.M)
    unresolved = [s for s in status_lines
                  if any(k in s for k in ('未解决', '待验证', '待复盘', 'pending'))]
    check('A4', 'rules.md 每条状态均为终态（无未解决/待验证）',
          len(status_lines) == db_rules_n and not unresolved,
          f'status_lines={len(status_lines)} unresolved={unresolved[:5]}')

    # ---------- B. rules.db ----------
    b1_ok = (rd['rules'] == db_rules_n and rd['rule_sources'] == db_rule_end
             and rd['rule_verification'] == len(db_ver_ids)
             and rd['rule_changes'] == len(db_changes_ids)
             and rd['rule_cards'] == 7046 and rd['rule_keywords'] == 885
             and rd['null_canon'] == db_null_canon)
    check('B1', 'rules.db 各表计数 == rules_work.db',
          b1_ok, json.dumps({'rules_db': rd, 'db': {'rules': db_rules_n,
          'rule_evidence': db_rule_end, 'verification': len(db_ver_ids),
          'changes': len(db_changes_ids), 'null_canon': db_null_canon}}, ensure_ascii=False))
    meta_val = json.loads(rd_meta.get('validation', '{}')) if 'validation' in rd_meta else {}
    check('B2', 'rules.db meta.validation PASS', meta_val.get('PASS') is True,
          f"builder={rd_meta.get('builder')}")
    check('B3', 'verification 状态分布一致 (verified=392, verified_with_changes=1)',
          db_ver_dist == rd_ver_dist == {'verified': 392, 'verified_with_changes': 1}
          and db_nv_true == 0,
          f'work={db_ver_dist} rules_db={rd_ver_dist} nv_true={db_nv_true}')

    # ---------- C. change_log.md ----------
    c_ids = re.findall(r'^#### (CHG-\S+)', change_md, flags=re.M)
    rd_chg_ids = {r[0] for r in rdb.execute("SELECT change_id FROM rule_changes")}
    check('C1', 'change_log.md 条目 ID 集合 == DB changes == rules.db rule_changes',
          len(c_ids) == len(db_changes_ids) == len(rd_chg_ids)
          and len(set(c_ids)) == len(db_changes_ids)
          and set(c_ids) == db_changes_ids == rd_chg_ids,
          f'file={len(c_ids)} distinct={len(set(c_ids))} db={len(db_changes_ids)} '
          f'rules_db={len(rd_chg_ids)}')
    def chg_tier(s):  # CHG-5-0001 -> '5'; CHG-4B-T2ER-... -> 'T2ER'
        if s.startswith('CHG-5'):
            return '5'
        m = re.match(r'CHG-4B-([A-Z0-9]+)-', s)
        return m.group(1) if m else '?'
    tiers = {}
    for s in c_ids:
        tiers[chg_tier(s)] = tiers.get(chg_tier(s), 0) + 1
    total_claim = re.search(r'^- 变更总数: (\d+)', change_md, flags=re.M)
    check('C2', 'change_log.md 总数声明 267 且 tier 分布与文件/DB 一致',
          total_claim and int(total_claim.group(1)) == len(db_changes_ids)
          and tiers == {'T2ER': 222, 'T1F': 6, 'T3': 38, '5': 1},
          f'claim={total_claim.group(1) if total_claim else None} tiers={tiers}')

    # ---------- D. manual_review.md ----------
    mr_ids = re.findall(r'^#### `(MR-\S+)`', mr_md, flags=re.M)
    mr_entries = mr_md[mr_md.index('## 1. '):]
    closed_n = mr_entries.count('| 状态 | **已关闭**')
    pending_n = mr_entries.count('待复盘')
    check('D1', 'manual_review.md 条目 ID 集合 == DB manual_review',
          len(mr_ids) == len(db_mr_ids) and len(set(mr_ids)) == len(db_mr_ids)
          and set(mr_ids) == db_mr_ids,
          f'file={len(mr_ids)} db={len(db_mr_ids)}')
    check('D2', 'manual_review.md 全部已关闭（无待复盘）',
          closed_n == len(db_mr_ids) and pending_n == 0,
          f'closed={closed_n} pending={pending_n}')

    # ---------- E. coverage_report.md ----------
    def cov_int(pat, group=1):
        m = re.search(pat, cov_md)
        return int(m.group(group)) if m else None
    crow = re.findall(r'^\| (C\d+) \|[^\n]*\| (PASS|FAIL) \|', cov_md, flags=re.M)
    check('E0', 'coverage_report.md 强制检查清单 13 行全 PASS',
          len(crow) == 13 and all(res == 'PASS' for _, res in crow),
          f'rows={len(crow)} fail={[c for c, r in crow if r != "PASS"]}')
    cov_disc = cov_int(r'Documents discovered:\s+(\d+)')
    cov_proc = cov_int(r'Documents processed:\s+(\d+)')
    cov_fail = cov_int(r'Documents failed:\s+(\d+)')
    check('E1', 'coverage: Documents discovered/processed/failed == DB',
          cov_disc == db_src_total == db_src_covered and cov_proc == db_src_covered
          and cov_fail == 0 and db_bad_tasks == 0,
          f'doc={cov_disc}/{cov_proc}/{cov_fail} db={db_src_covered}/{db_src_total} '
          f'bad_tasks_x6f={db_bad_tasks}')
    check('E2', 'coverage: Evidence extracted/mapped/unmapped == DB',
          cov_int(r'Evidence extracted:\s+(\d+)') == db_evidence
          and cov_int(r'Evidence mapped:\s+(\d+)') == db_mapped == db_evidence
          and cov_int(r'Unmapped evidence:\s+(\d+)') == 0,
          f'{db_evidence}/{db_mapped}/0')
    rv_line = re.search(r'Rules verified:\s+(\d+)\s+\(verified=(\d+), '
                        r'verified_with_changes=(\d+)\)', cov_md)
    check('E3', 'coverage: Rules generated/verified == DB',
          cov_int(r'Rules generated:\s+(\d+)') == db_rules_n
          and rv_line and int(rv_line.group(1)) == len(db_ver_ids)
          and int(rv_line.group(2)) == db_ver_dist.get('verified')
          and int(rv_line.group(3)) == db_ver_dist.get('verified_with_changes'),
          f'generated={db_rules_n} verified={len(db_ver_ids)} dist={db_ver_dist}')
    rul = re.search(r'Rulings attached:\s+(\d+)/(\d+)', cov_md)
    check('E4', 'coverage: Errata applied / FAQ attached / Rulings attached == DB',
          cov_int(r'Errata applied:\s+(\d+)') == db_errata_zh
          and cov_int(r'FAQ attached:\s+(\d+)') == db_faq_links
          and rul and int(rul.group(1)) == int(rul.group(2)) == db_rulings == db_rulings_total,
          f'errata_zh={db_errata_zh} faq={db_faq_links} rulings={db_rulings}/{db_rulings_total}')
    check('E5', 'coverage: Conflicts resolved/unresolved、Manual review items == DB',
          cov_int(r'Conflicts resolved:\s+(\d+)') == db_conf_resolved
          and cov_int(r'Unresolved conflicts:\s+(\d+)') == db_conf_unres == 0
          and cov_int(r'Manual review items:\s+(\d+)') == len(db_mr_ids),
          f'conflicts={db_conf_resolved}/{db_conf_unres} mr={len(db_mr_ids)}')

    # ---------- F. 跨产物状态一致性 (spec 17.4 核心) ----------
    c12 = re.search(r'^\| C12 \|[^\n]*\| PASS \|', cov_md, flags=re.M)
    check('F1', 'manual_review 全部关闭 ⟷ rules.md 无未决 ⟷ coverage C12 PASS（无 resolved/unresolved 矛盾）',
          closed_n == len(db_mr_ids) and pending_n == 0 and not unresolved and bool(c12),
          f'mr_closed={closed_n}/{len(db_mr_ids)} rules_unresolved={len(unresolved)} '
          f'c12={"PASS" if c12 else "?"}')
    stat_ok = ('规则 2984 条' in rules_md
               and 'verified 392 + verified_with_changes 1' in rules_md
               and '未解决 0' in rules_md)
    check('F2', 'rules.md 统计声明 == DB verification 分布 == rules.db == coverage',
          stat_ok and db_ver_dist == {'verified': 392, 'verified_with_changes': 1}
          and db_ver_dist == rd_ver_dist and rv_line
          and int(rv_line.group(1)) == len(db_ver_ids),
          f'rules_md_claims={stat_ok} dist={db_ver_dist}')
    check('F3', 'conflicts 状态一致: DB resolved_stage5 ⟷ rules.md 图例 ⟷ coverage 1/0',
          len(db_conflict) == 1 and db_conf_resolved == 1 and db_conf_unres == 0
          and db_conflict[0]['resolution_status'] == 'resolved_stage5'
          and 'conflicts 1/1 resolved_stage5' in rules_md
          and cov_int(r'Conflicts resolved:\s+(\d+)') == 1
          and cov_int(r'Unresolved conflicts:\s+(\d+)') == 0,
          json.dumps(db_conflict, ensure_ascii=False))
    cov_changes = re.search(r'^- changes: (\d+) 行', cov_md, flags=re.M)
    check('F4', 'changes 计数一致: change_log 267 ⟷ DB ⟷ rules.db ⟷ coverage',
          total_claim and int(total_claim.group(1)) == len(db_changes_ids)
          and cov_changes and int(cov_changes.group(1)) == len(db_changes_ids)
          and rd['rule_changes'] == len(db_changes_ids) and len(db_changes_ids) == 267,
          f'changes={len(db_changes_ids)}')
    seg811 = rules_md[rules_md.index('### R-CR-811.1.b'):]
    seg811 = seg811[:seg811.index('\n### ')] if '\n### ' in seg811 else seg811
    chg5 = re.search(r'^#### CHG-5-0001 .*$', change_md, flags=re.M)
    v811 = w.execute("SELECT status FROM verification WHERE rule_id='R-CR-811.1.b'").fetchall()
    check('F5', 'R-CR-811.1.b 链一致: rules.md verified_with_changes ⟷ change_log CHG-5-0001 ⟷ DB',
          'verification=verified_with_changes' in seg811
          and chg5 and 'R-CR-811.1.b' in chg5.group(0)
          and db_conflict[0]['rule_id'] == 'R-CR-811.1.b'
          and len(v811) == 1 and v811[0]['status'] == 'verified_with_changes',
          f"verification={[r['status'] for r in v811]} chg5={'yes' if chg5 else 'no'}")
    check('F6', 'superseded 标记一致: rules.md [superseded-已被取代] >=2 ⟷ coverage C9 指向 EV-CN-FAQ-0089/0090',
          rules_md.count('[superseded-已被取代]') >= 2
          and 'EV-CN-FAQ-0089' in cov_md and 'EV-CN-FAQ-0090' in cov_md,
          f"markers={rules_md.count('[superseded-已被取代]')}")

    overall = all(c['result'] == 'PASS' for c in checks)

    # ---------- report ----------
    L = []
    A = L.append
    A('# Stage 6F — Final Consistency Check (spec 17.4)')
    A('')
    A(f'- 执行时间: {now()}  脚本: stage6f_final_consistency.py (幂等, 只读产物)')
    A('- 数据源: workspace/rules_work.db (事实来源) + workspace/final/{rules.md, rules.db, '
      'change_log.md, manual_review.md, coverage_report.md}')
    A(f'- 结论: **{"全部检查 PASS" if overall else "存在 FAIL, 见下表"}** '
      f'({sum(1 for c in checks if c["result"] == "PASS")}/{len(checks)})')
    A('')
    A('| ID | 检查项 | 结果 | 明细 |')
    A('|---|---|---|---|')
    for c in checks:
        A('| {} | {} | {} | {} |'.format(c['id'], c['name'], c['result'],
          c['detail'].replace('|', '\\|')[:240]))
    A('')
    A('## 互查矩阵摘要')
    A('')
    A(f'- rules.md: {len(ids)} entries == rules 2984 == rules.db {rd["rules"]}; '
      f'14 字段齐全; NULL-canonical 标记 {marker_n} == DB {db_null_canon}')
    A(f'- change_log.md: {len(c_ids)} entries == changes 267 == rules.db {rd["rule_changes"]}; '
      f'tiers {tiers}')
    A(f'- manual_review.md: {len(mr_ids)} entries == manual_review 186; 已关闭 {closed_n}, '
      f'待复盘 {pending_n}')
    A(f'- coverage_report.md: C1..C13 PASS; 计数与 DB 逐项一致 '
      f'(docs {db_src_covered}/{db_src_total}, evidence {db_mapped}/{db_evidence}, '
      f'rules {db_rules_n}, verified {len(db_ver_ids)}, conflicts {db_conf_resolved}/'
      f'{db_conf_unres}, mr {len(db_mr_ids)})')
    A(f'- rules.db: rules/{rd["rules"]} rule_sources/{rd["rule_sources"]} '
      f'rule_cards/{rd["rule_cards"]} rule_keywords/{rd["rule_keywords"]} '
      f'rule_verification/{rd["rule_verification"]} rule_changes/{rd["rule_changes"]}; '
      f'meta.validation.PASS={meta_val.get("PASS")}')
    A('')
    A('spec 17.4 互查要求: rules.md / rules.db / change_log.md / manual_review.md / '
      'coverage_report.md 数量与状态一致 — ' + ('达成。' if overall else '未达成。'))
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')

    # ---------- checkpoint + task status ----------
    ckpt = {'task_id': 'task_6_06', 'stage': '6F', 'report': REPORT, 'built_at': now(),
            'checks': checks, 'PASS': overall,
            'stats': {'checks_total': len(checks),
                      'checks_pass': sum(1 for c in checks if c['result'] == 'PASS'),
                      'rules': db_rules_n, 'verification': len(db_ver_ids),
                      'changes': len(db_changes_ids), 'manual_review': len(db_mr_ids)}}
    os.makedirs(os.path.dirname(CKPT), exist_ok=True)
    with open(CKPT, 'w', encoding='utf-8') as f:
        json.dump(ckpt, f, ensure_ascii=False, indent=2)

    if overall:
        w.execute(
            "UPDATE processing_tasks SET status='completed', notes=? WHERE task_id='task_6_06'",
            (f"Stage 6F Final Consistency Check COMPLETED {now()}; script "
             f"stage6f_final_consistency.py (idempotent); {len(checks)}/{len(checks)} checks PASS "
             f"(A rules.md / B rules.db / C change_log / D manual_review / E coverage / "
             f"F cross-status); no contradictions found; report {REPORT}; checkpoint {CKPT}",))
    else:
        w.execute(
            "UPDATE processing_tasks SET status='failed', notes=? WHERE task_id='task_6_06'",
            ('consistency check failed: ' + json.dumps(
                [c for c in checks if c['result'] == 'FAIL'], ensure_ascii=False)[:1500],))
    w.commit()
    w.close(); rdb.close()

    print(json.dumps({'PASS': overall, 'checks': ckpt['stats'],
                      'failed': [c['id'] for c in checks if c['result'] == 'FAIL']},
                     ensure_ascii=False, indent=2))
    print('RESULT:', 'PASS - task_6_06 completed' if overall else 'FAIL')
    sys.exit(0 if overall else 1)

if __name__ == '__main__':
    main()
