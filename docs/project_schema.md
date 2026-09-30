# 项目 Schema 总览（新会话快速上手）

> → README → AGENTS.md（分阶段交付规程）→ 本文档（数据模式速查）。
> 最后更新：2026-09-29。**数据管线 COMPLETE（2026-09-22）；工程线阶段 0/1/2/3 验收；阶段 4 首轮完成（回放器 VM-1 通过 + 卡牌效果地基，测试 121 绿，覆盖 reports/card_coverage.md）**，进展见 docs/stage1_worklog.md。

## 1. 项目是什么

两条线共用一份权威数据：

1. **规则知识库管线（已完成）**：20 份中英文官方 PDF（核心规则/勘误/FAQ/Patch Notes）→ 多阶段可恢复 SQLite 管线 → `workspace/final/` 5 份最终产物（rules.md 2984 条、rules.db、change_log.md、manual_review.md、coverage_report.md）。
2. **RL 模拟器工程线（进行中，AGENTS.md 主导）**：头无 UI 的 headless 引擎（`src/riftsim/`，纯标准库）→ trace → 只读回放 → RL。阶段 0–3 已完成：规则规格 2984 条 + 最小核心引擎 M1（54 测试全绿、4 个 fixture trace、SPS off=239/debug=163）。**阶段 4 未开始**：卡牌效果（514 R-CARD 全部 deferred，骨架池空效果）与回放 UI。

**效力优先级**：官方 Errata > 官方 FAQ/裁定 > 核心规则书；同层级取更新版本；同版本英文 > 中文。卡牌数据库**不是**规则来源，只做实体识别。

## 2. 数据库速查

### 2.1 `workspace/final/rules.db`（~8 MB，查询入口，只读）

| 表 | 行数 | 关键列 | 用途 |
|---|---|---|---|
| `rules` | 2984 | rule_id PK, topic, proposed_canonical_rule, trigger/precondition/effect/restriction/exception（语义五字段，**全 NULL**）, official_interpretation, derived_interpretation, example, status, needs_verification, verification_status | 最终规则集；canonical NULL 472 条=FAQ 挂载型（有意为之） |
| `rule_sources` | 6353 | rule_id, evidence_id, relationship, source_id/document/type/language, version, date, page, section, rule_number | 规则→原始证据回查（含页码） |
| `rule_cards` | 7046 行 / 661 rules | rule_id, card_id, origin | 规则↔卡牌多对多（含 T/R/SP 前缀 token/rune/special id） |
| `rule_keywords` | 885 | rule_id, keyword, source_field | 括号关键字**启发式抽取，有噪音，勿当语义来源** |
| `rule_verification` | 393 | verification_id, rule_id, status, stage4_conclusion, verification_conclusion, ... | 独立验证记录（392 verified + 1 verified_with_changes） |
| `rule_changes` | 267 | change_id PK, rule_id, original/new_content, modification_type, ... | 变更记录（222 勘误 + 6 FAQ 内嵌 + 38 核心发布后 + 1 验证修复） |
| `rules_fts` | 2984 | rule_id, text | FTS5 全文索引；**中文分词不可靠**，精确查 rule id 用 JOIN |
| `meta` | 9 | k, v | 构建元数据 |

```sql
-- 某牌全部规则
SELECT rule_id FROM rule_cards WHERE card_id='OGN-131';
-- 某规则回查原文页码
SELECT evidence_id, source_document, page FROM rule_sources WHERE rule_id='R-CR-811.1.b';
```

### 2.2 `workspace/rules_work.db`（~8.5 MB，**事实来源**；final/ 由它幂等重建，见 README「复现」节）

| 表 | 行数 | 说明 |
|---|---|---|
| `sources` | 20 | source_id（source_001..020）、source_type（rule/errata/faq/official_explanation）、language、date/effective_date、date_confidence |
| `evidence` | 5527 | evidence_id（EV-CN-CR-*/EV-EN-*/EV-CN-ER-*/EV-CN-FAQ-*/EV-EN-OE-*），原文 original_text + 勘误段（target_rule_candidate/corrected_fragment/modification_type）+ FAQ 段（faq_question/answer/classification）+ card_ids |
| `alignments` | 2445 | 中英对齐（2382 AL-CR 核心对 + 63 AL-ER 勘误对） |
| `rules` | 2984 | 与 final/rules.db 同构（少 verification_status 列） |
| `rule_evidence` | 6353 | 规则↔证据多对多，relationship=same/replacement/faq:*/front_matter |
| `reconciliations` | 2996 | 4B 裁决记录（REC-4B-T0/T1/T1F/T2/T2ER/T3） |
| `changes` 267 / `conflicts` 1 / `verification` 393 / `manual_review` 186 / `processing_tasks` 69 | — | 变更 / 冲突（1 项已裁决）/ 验证 / 人工复核（全部已关闭）/ 任务队列 |

### 2.3 `cards_bilingual.db`（~1 MB，合并后卡表，1267 行）

`cards` 表（card_key PK，如 `OGN-017`，变体加后缀 `OGN-066a`）：

| 分组 | 列 |
|---|---|
| 标识 | card_key PK, set_id, number, variant（base 1052/alt 148/star 45/token 16/sp 6） |
| 名称/类型 | name_en, name_cn, sub_title_cn, type_en（Unit 629/Spell 233/Legend 127/Gear 114/Battlefield 66/Rune 18/NULL 80）, type_cn, super_type（Champion 303/Signature 51/Token 14/Basic 18） |
| 属性 | domain_en（6 特性+混色+Colorless）, color_cn, energy, rune_power, might, might_bonus, hero_cn, region_cn |
| 文本 | text_en, text_cn, flavor_cn, errata_cn（非空 99 条，**不含勘误后全文，勿当 canonical**） |
| 其他 | rarity_*/extend_rarity_cn, tags_en, image_url/image_path |

系列前缀：OGN 364 / SFD 312 / UNL 300 / VEN 253 / OGS 24 / ARC 6 / FND 5 / SGN 3。**卡面占位符中英不同体系**：CN 用 `{{关键词}}`/`{{S}}`/`{{A}}`/`{{1}}`（如 `{{迅捷}}`、`{{横置}}`）；EN 用 `:rb_might:`/`:rb_exhaust:`/`:rb_energy_N:`/`:rb_rune_*:`。ARC 系列无英栏。

原始抓取库（一般不用直接查）：`cards_cn/cards.db`（1261 行，中文官网全字段+json）、`cards_en/cards.db`（1189 行，英文官网）。

## 3. ID / 编号体系

| 前缀 | 含义 | 规模 |
|---|---|---|
| `R-CR-*` / `R-CR-FRONT` | 核心规则 | 2381 + 1（中英编号序列一致，同版本 2026-07） |
| `R-CARD-*` | 卡牌规则（130 勘误 + 384 FAQ 挂载） | 514 |
| `R-TOPIC-CN/EN-*` | 主题聚合桶 | 17 + 64 |
| `R-MISC-*` / `R-ER-FRONT` / `R-FAQ-FRONT` | 杂项与前言 | 5 + 2 |
| `EV-*` | evidence（EV-CN-CR/EV-EN-CR/EV-CN-ER/EV-EN-ER/EV-CN-FAQ/EV-EN-OE） | 5527 |
| `MR-2C/2D/3-CR/4A-*` | 人工复核（全部已关闭） | 186 |
| `CHG-4B-T2ER/T1F/T3-*`、`CHG-5-0001` | 变更记录 | 267 |
| `REC-4B-*`、`CON-4B-T2-0001`（已裁决） | 裁决 / 冲突记录 | 2996 / 1 |
| `MECH-*` | spec/rule_semantics.yaml 机制条目 | 166 |
| `T-0001..0134` | spec/rule_test_matrix.md 测试案例 | 134 |
| 卡 id | `SET-NNN[a-z]`，token/rune/special 带 T/R/SP 前缀 | 1267 |

## 4. 目录与产物地图

```
AGENTS.md                # ★ 工程线总规程（阶段 0–6 交付，先读后动）
docs/project_schema.md   # 本文档
docs/
  source_inventory.md / implementation_scope.md        # 阶段 0
  architecture.md / api_contract.md / training_architecture.md / visualization_spec.md  # 阶段 2
  rule_conflicts.md / unresolved_rules.md (OPEN-1..6) / stage1_worklog.md（进展主入口）
spec/
  rules_spec.yaml        # 2984 条规格（tier: MVP 1684/P1 414/P2 215/OUT 69/cards 514/meta 88；
                         # status: verified 2470/deferred 514；生成器 scripts/spec/build_rules_spec.py --check）
  rule_semantics.yaml    # 166 条机制语义（手写，covers 全覆盖 R-CR）
  rule_dependencies.md / rule_test_matrix.md            # 依赖序 / 134 测试案例
src/riftsim/             # 引擎（纯标准库，27 模块；engine/state/observation/actions/legality/
                         # phaser/chain_sys/showdown/combat/scoring/trace/replay/runner/policies…）
tests/                   # 54 通过（含 privacy/snapshot_replay_runner）
runs/fixtures/           # 4 个 fixture trace（rifttrace/1，scripts/gen_fixture_traces.py 再生成）
workspace/
  rules_work.db          # ★ 管线事实来源
  final/                 # ★ 5 份最终产物（rules.md / rules.db / change_log.md / manual_review.md / coverage_report.md）
  README_STATE.md        # 管线状态（COMPLETE）与全量裁决编年
  checkpoints/  reports/ progress.json
  rag/                   # RAG 向量索引（gitignore，可重建；scripts/rag/）
scripts/                 # stage*/ 管线脚本（幂等，从仓库根执行）＋ cards/ ingest/ rag/ spec/ rulings/ debug/
.tmp/                    # 一次性探针与输出（大输出先重定向到这里再 Read）
loltcg_pdfs/  riftbound_en_rules/  extracted/  kb/     # 原始 PDF、抽取文本、早期产物(非权威)
cards_en/  cards_cn/  cards_bilingual.db               # 卡牌库（非规则来源）
```

## 5. 已知坑（勿重复踩）

- **语义五字段（trigger/effect/…）在 DB 里全 NULL**：语义在 `spec/rule_semantics.yaml` + rules_spec.yaml（生成自语义层），stage 1 手写的。
- **FTS 中文分词不可靠、rule_keywords 启发式有噪音**：spec 不从这里取语义。
- card `errata_cn` 不是勘误后全文（31/130 缺）；卡牌 canonical 在 rules_work.db 的 `reconciliations.corrected_fragment`（最新 zh 勘误）。
- 4 张观察卡 OGN-131/OGN-251/UNL-097/UNL-177：zh 牌面待官方更新，现行口径＝source_008 破限裁判 FAQ 第 4 节。
- R-CR-811.1.b：中文漏译持续从句，按同版本英文优先补入（CHG-5-0001）。
- 中文裁判 FAQ（source_001/006/008）非官方，效力层级=裁判社区，条目前缀已标注。
- 终端大输出会截顶：重定向 `.tmp/*.txt` 再读；PowerShell 单引号字面串，复杂命令写 `.tmp/*.py`。
- 环境：Python 3.12 / pytest 9.1（`requirements.txt`）；RAG 需项目内 `.venv`（torch-cpu + sentence-transformers，~3 GB）。

## 6. 常用命令

```powershell
# 引擎测试
python -m pytest tests -q          # 54 passed
# 规格校验（语义层改动后必跑）
python scripts/spec/build_rules_spec.py --check
# trace 回放一致性
python scripts/gen_fixture_traces.py
# 规则检索（FTS 仅辅助；精确查 id 用 rules.db JOIN）
python -c "import sqlite3;print(sqlite3.connect('workspace/final/rules.db').execute('SELECT rule_id,topic FROM rules_fts WHERE rules_fts MATCH ''反制'' LIMIT 5').fetchall())"
```
