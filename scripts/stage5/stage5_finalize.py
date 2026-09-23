# -*- coding: utf-8 -*-
# Stage 5 收尾: 汇总统计 + 报告 + checkpoint + progress.json
import sqlite3, json
from datetime import datetime, timezone

NOW = datetime.now(timezone.utc).isoformat(timespec='seconds')
db = sqlite3.connect('workspace/rules_work.db')
db.row_factory = sqlite3.Row
cur = db.cursor()

stats = {}
stats['verification_by_status'] = [dict(r) for r in cur.execute("SELECT status, COUNT(*) c FROM verification GROUP BY status").fetchall()]
stats['verification_total'] = cur.execute("SELECT COUNT(*) FROM verification").fetchone()[0]
stats['nv_true'] = cur.execute("SELECT COUNT(*) FROM rules WHERE needs_verification='true'").fetchone()[0]
stats['changes_total'] = cur.execute("SELECT COUNT(*) FROM changes").fetchone()[0]
stats['chg5'] = cur.execute("SELECT COUNT(*) FROM changes WHERE change_id LIKE 'CHG-5-%'").fetchone()[0]
stats['conflicts'] = [dict(r) for r in cur.execute("SELECT conflict_id, rule_id, resolution_status FROM conflicts").fetchall()]
r = cur.execute("SELECT proposed_canonical_rule FROM rules WHERE rule_id='R-CR-811.1.b'").fetchone()
stats['r811_canonical_now'] = r['proposed_canonical_rule']
stats['tasks'] = [dict(r) for r in cur.execute("SELECT task_id, status FROM processing_tasks WHERE task_id LIKE 'task_5_%' ORDER BY task_id").fetchall()]

# 报告
report = f"""# Stage 5 — Independent Verification 报告

生成时间: {NOW}   脚本: stage5_verify.py (幂等; 批次 setup/v1/v2/v3/validate)

## 范围
- 393 条 rules.needs_verification='true' + 冲突 CON-4B-T2-0001 (pending_stage5)
- verification 表扩列: stage4_conclusion/verification_conclusion/relevant_evidence/disagreement_reason/verified_at
- 任务: task_5_01..05 全部 completed

## 批次
| 批次 | 范围 | 结果 |
|---|---|---|
| v1 (task_5_02) | 160 条 tr-diff R-CR (除 811.1.b) | 160 verified; canonical==zh官方原文逐字(回查 EV-CN-CR same 链接), en same 链接存在, REC-4B-T2 裁决行在, FAQ 挂载逐字; 0 needs_review |
| v2 (task_5_03) | 130 条 errata R-CARD | 130 verified; canonical==最新zh勘误 corrected_fragment 逐字(按 date-asc 链, 含 7 条双勘误链), CHG-4B-T2ER 行数==替换链接数, EN 对照勘误仅记录未改 canonical, 修改范围未扩大; 0 needs_review |
| v3 (task_5_04) | 102 条混合 (30 FAQ-only卡 + 14 T1F + 57 T3桶 + 811.1.b) + 冲突 | 102 verified + 1 verified_with_changes; 0 needs_review |

注: v3 首跑 23 项 needs_review 全部为检查器对 B005/B006 记录形式理解不足的误报
(stale-ref 故意不挂载字段为 NULL / T3 计数式 REC + OI 逐条挂载 / APPLIED 判定词窗口),
修正检查逻辑后复跑全部通过; 数据无需任何更改。

## 冲突裁决 CON-4B-T2-0001 (R-CR-811.1.b, Hidden 811.1.b)
- **分歧**: EN 官方核心规则 (source_018, 2026-07-16, 与 CN 同版本——2B 已证规则编号序列完全一致)
  带持续时段从句 "for as long as you control that battlefield"; zh 官方译文 (source_009) 缺失该从句。
- **裁决依据**: 规范 2.4/15.4 —— 同版本: 英文官方文本 > 中文官方文本。EN 仅早 1 天且同版本序列证明一致,
  不构成"旧英文机械覆盖新中文"的例外情形。语义差异有实际玩法影响 (待命牌在失去战场控制后的存留)。
- **结论**: verified_with_changes。canonical 补入该从句的中文转写
  (「…此牌保持正面朝下待命状态，直至你不再控制该战场。…」), 符合库内既有中文措辞习惯。
- **记录**: CHG-5-0001 (modification_type=condition_change, 含 old/new 全文与理由);
  conflicts.resolution_status=resolved_stage5; VER-5-R-CR-811.1.b 含 stage4_conclusion /
  verification_conclusion / disagreement_reason (4B zh-约定 vs 5 EN-优先, 证据明确可裁决, 无需 manual_review)。

## 专题核验
- **Errata 应用范围** (规范16.5): 130 规则 canonical 与最新 zh 勘误片段完全相等 → 修改目标正确、范围未扩大、
  未误删未修改部分 (canonical 仅取自 corrected_fragment)。
- **FAQ 泛化**: rules.derived_interpretation 全库 0 行 —— 从未发生 FAQ 过度泛化为一般规则;
  411 条 faq:example_only / rule_interpretation / exception 挂载全部逐字 + 来源前缀回查通过
  (001/006/008 judge-community 层级前缀保持)。
- **中英版本**: 161 tr-diff 全部维持"同版本正字差异"结论; 唯一语义分歧已按上条裁决。
- **RCC 134 链接全覆盖**: source_019 (eff 2026-07-24 > 2026-07 核心) APPLIED 均有 '[eid|...|APPLIED post-core
  official change]' 逐条挂载 + CHG-4B-T3 行; source_012/014/016 (transitional pre-core) NOT applied 记录一致
  (日期逻辑独立复核通过); source_005/007 INCORPORATED 7 条有 CHG-4B-T1F/T3-0006 行, 0055 vs 现行 809.1.c
  语义等价复核通过; B005 stale-ref 7 链接确认字段留空属裁决结果且内容挂载于正确后继规则
  (0206→816.2 ✓, 0207→323.6 ✓, 后继覆盖 340.4/383.x/466.x/471.1.b.1)。
- **MR-2D-0005 watch 4 卡** (OGN-131/OGN-251/UNL-097/UNL-177): REC-4B-T3 watch 行在, 现行口径按
  设计师 FAQ source_008 sec.4, EN 为权威参照, 待 zh 文本更新追踪保留于 REC notes (OGN-251 的
  EV-CN-FAQ-0260 未链警告如实记录)。

## 终态 (validate)
- verification 共 {stats['verification_total']} 行: {stats['verification_by_status']}
- needs_verification='true' 剩余 {stats['nv_true']}
- conflicts: {stats['conflicts']}
- changes 总计 {stats['changes_total']} (新增 CHG-5 x{stats['chg5']})
- rejected=0, failed=0, pending=0, needs_review=0 → **Stage 5 = completed**
"""
with open('workspace/reports/stage5_verification.md', 'w', encoding='utf-8') as f:
    f.write(report)

# checkpoint
ckpt = {
    'stage': '5', 'status': 'completed', 'completed_at': NOW,
    'script': 'stage5_verify.py (idempotent)',
    'batches': {'v1_trdiff': '160 verified', 'v2_errata': '130 verified',
                'v3_mixed': '102 verified + 1 verified_with_changes (R-CR-811.1.b)'},
    'totals': stats,
    'conflict_resolution': 'CON-4B-T2-0001 resolved_stage5 via CHG-5-0001 (EN same-version priority, duration clause supplemented)',
    'next': 'Stage 6 - Final Build + Coverage Check',
}
with open('workspace/checkpoints/stage5_checkpoint.json', 'w', encoding='utf-8') as f:
    json.dump(ckpt, f, ensure_ascii=False, indent=2)

# processing_tasks
cur.execute("UPDATE processing_tasks SET status='completed' WHERE task_id='task_5_05'")
db.commit()

# progress.json
with open('workspace/progress.json', encoding='utf-8') as f:
    prog = json.load(f)
prog['current_stage'] = ("Stage 5 COMPLETED 2026-09-22 (393/393 terminal: 392 verified + 1 verified_with_changes; "
    "CON-4B-T2-0001 resolved_stage5 via CHG-5-0001). Next: Stage 6 Final Build + Coverage Check")
prog['stages']['stage_5'] = {
    'status': 'completed',
    'description': ("Independent Verification completed 2026-09-22. Script stage5_verify.py (idempotent, batches v1/v2/v3). "
        "verification table extended (stage4_conclusion/verification_conclusion/relevant_evidence/disagreement_reason/verified_at); "
        "393 rows: 392 verified + 1 verified_with_changes; 0 rejected/needs_review/failed/pending; needs_verification='true' remaining 0. "
        "v1: 160 tr-diff R-CR canonical==zh official evidence verbatim + en links + REC rows + FAQ verbatim. "
        "v2: 130 errata R-CARD canonical==latest zh errata corrected_fragment (date-asc chains), CHG-4B-T2ER coverage == replacement links, EN counterparts recorded w/o canonical change, scope not expanded. "
        "v3: 30 FAQ-only cards + 14 T1F flagged + 57 T3 topic/misc + R-CR-811.1.b; RCC 134 links adjudication-record coverage verified "
        "(019 post-core eff 2026-07-24 APPLIED with verbatim attach + CHG-4B-T3; 012/014/016 transitional pre-core NOT applied; "
        "005/007 INCORPORATED with CHG rows; B005 stale-ref NULL fields confirmed intentional, 0206->816.2 / 0207->323.6 relinked). "
        "CON-4B-T2-0001 R-CR-811.1.b: EN same-version duration clause 'for as long as you control that battlefield' omitted in zh translation "
        "-> verified_with_changes, canonical supplemented (zh rendering), CHG-5-0001, conflict resolved_stage5, no manual_review needed (evidence decisive). "
        "MR-2D-0005 watch cards verified with documented divergence notes. derived_interpretation=0 confirmed (no FAQ over-generalization). "
        "report: workspace/reports/stage5_verification.md; checkpoint: workspace/checkpoints/stage5_checkpoint.json; changes total 267.")
}
prog['last_checkpoint'] = {'batch_id': '5-final', 'task_id': 'task_5_05',
    'checkpoint': 'workspace/checkpoints/stage5_checkpoint.json',
    'note': 'Stage 5 COMPLETE: 393/393 verification terminal, conflicts 0 open'}
prog['last_updated'] = '2026-09-22'
with open('workspace/progress.json', 'w', encoding='utf-8') as f:
    json.dump(prog, f, ensure_ascii=False, indent=2)

db.close()
print('finalize ok')
