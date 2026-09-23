# Riftbound 规则知识库（riftsim）

将《符文战场》（Riftbound / LoL TCG）的中英文官方资料——核心规则、卡牌勘误、官方 FAQ、
裁判 FAQ、Patch Notes——系统性整理为一套**统一、可追溯、可验证**的规则知识库。

项目不是一次性的文本汇总，而是一条**多阶段、可恢复的数据管线**：
所有正式成果落盘于 SQLite，任何结论都可以回查到原始 PDF 的某一页某一条。

**当前状态：管线 COMPLETE（2026-09-22）**，20/20 来源处理完毕，无未决事项。

## 最终产物（`workspace/final/`）

| 文件 | 内容 |
|---|---|
| `rules.md` | 最终规则集，2984 条（核心规则 R-CR 2382 / 卡牌 R-CARD 514 / 主题 R-TOPIC 81 / 杂项与前言 7），每条含规范规则、官方解释、案例、例外、来源、状态 |
| `rules.db` | 同一数据的可查询 SQLite 版，带 FTS5 全文索引，可按 rule_id / topic / card_id / keyword / source / version 检索 |
| `change_log.md` | 267 条变更记录（222 勘误应用 + 6 FAQ 内嵌变更 + 38 核心规则发布后的官方改动 + 1 验证修复） |
| `manual_review.md` | 186 条人工复核记录，全部经正式裁决关闭，含问题原始记录与裁定结论 |
| `coverage_report.md` | 覆盖检查报告，13/13 强制检查 PASS |

事实来源是 `workspace/rules_work.db`；`final/` 下的产物全部由它程序化生
成，可幂等重建。

## 数据来源

- `loltcg_pdfs/`：中文官方 PDF 11 份（核心规则、勘误汇总、官方/裁判 FAQ）
- `riftbound_en_rules/`：英文官方 PDF 9 份（Core Rules、Errata、Patch Notes）
- `cards_bilingual.db`：双语卡牌库（`scripts/cards/card_scraper.py` + `cards_cn_scraper.py`
  抓取官网卡表后由 `build_bilingual_db.py` 合并），**仅用于卡牌实体识别，不作为规则来源**

中英文核心规则编号序列完全一致，已确认为同一规则版本（2026-07）。

## 管线概览

处理规范定义在 `riftbound_rules_multisession_prompts_v2_resumable.md`，核心原则：

1. **证据优先**：原文 → Evidence Store → 各阶段处理，任何结论可回查原文，禁止"总结的总结"。
2. **分批 + 原子落盘**：单条 item 处理完即 COMMIT，中断后新会话可从 checkpoint 无损恢复。
3. **官方内容与推导内容严格分层**：官方规则 / 官方解释 / 模型推导 / 案例 / 例外 / 未解决
   分别标注（最终全库模型推导 0 条、未解决 0 条）。
4. **来源效力有序**：Errata 只修改其明确覆盖的范围；FAQ 默认只做解释/补充/例外，不默认
   覆盖规则书；同版本下英文官方文本优先于中文译文。

```
Stage 0   项目初始化（workspace、schema、progress 持久化）
Stage 1   来源清点 + PDF 预处理        → 20 份来源登记
Stage 2A/B 中/英文核心规则证据抽取      → 2382 + 2382 条 evidence
Stage 2C  勘误抽取                     → 156 条勘误 + 3 前言
Stage 2D  FAQ / 官方解释抽取           → 594 条 + 10 前言
Stage 3   实体识别 + 中英对齐           → 2445 组 alignment
Stage 4A  规则聚类                     → 2984 个 rule cluster
Stage 4B  规则裁决（canonical 生成）    → 2984/2984 reconciled
Stage 5   独立验证                     → 393 条高风险规则逐条回查
Stage 6   最终构建 + 一致性检查         → 5 份产物，6F 检查 24/24 PASS
```

每个阶段的脚本以 `stage<编号>_*.py` 命名，按阶段归档在 `scripts/` 子目录下，正式阶段脚本
均幂等可重跑；同名 `*_probe/*_peek/*_inspect` 脚本为一次性排查工具（见 `scripts/debug/`）。
过程报告在 `workspace/reports/`，批次检查点在 `workspace/checkpoints/`。
所有脚本均从**仓库根目录**执行（如 `python scripts/stage6/stage6f_final_consistency.py`）。

## 目录结构

```
riftsim/
├── README.md
├── riftbound_rules_multisession_prompts_v2_resumable.md   # 管线处理规范
├── loltcg_pdfs/           # 中文官方 PDF（11 份）
├── riftbound_en_rules/    # 英文官方 PDF（9 份）
├── extracted/             # PDF → 纯文本（PyMuPDF）
├── cards_en/, cards_cn/   # 官网卡牌库抓取结果
├── cards_bilingual.db     # 合并后的双语卡表
├── kb/                    # 早期预处理产物（非权威，以 evidence 表为准）
├── .pylibs/               # 随仓库携带的 PyMuPDF 依赖
├── workspace/
│   ├── rules_work.db      # ★ 事实来源数据库
│   ├── README_STATE.md    # 管线状态与恢复入口
│   ├── progress.json      # 机器可读进度
│   ├── source_manifest.json
│   ├── checkpoints/       # 各批次 checkpoint
│   ├── reports/           # 各阶段过程报告
│   └── final/             # ★ 最终产物（见上表）
└── scripts/               # 全部管线脚本（从仓库根目录执行）
    ├── ingest/            # 下载、PDF 抽取、建库、任务队列（Stage 0/1）
    ├── cards/             # 卡牌库抓取与合并
    ├── stage2/            # 证据抽取（2A 中文规则 / 2B 英文规则 / 2C 勘误 / 2D FAQ）
    ├── stage3/            # 实体识别与中英对齐
    ├── stage4/            # 规则聚类（4A）与规则裁决（4B）
    ├── stage5/            # 独立验证
    ├── stage6/            # 最终构建（6A-6F，幂等重建最终产物）
    ├── rulings/           # 人工裁定辅助脚本（Group A/B/C 等一次性裁决）
    └── debug/             # 一次性探针与中间输出（仅审计用）
```

## 查询示例（`workspace/final/rules.db`）

```sql
-- 全文检索（FTS5）
SELECT rule_id, text FROM rules_fts WHERE rules_fts MATCH '反制' LIMIT 10;

-- 查某张牌相关的全部规则与解释
SELECT rule_id FROM rule_cards WHERE card_id = 'OGN-131';

-- 查某条规则的来源（可回查到 evidence 与原始文档）
SELECT evidence_id, relationship, source_document, page
FROM rule_sources WHERE rule_id = 'R-CR-811.1.b';

-- 查某关键字相关规则
SELECT rule_id FROM rule_keywords WHERE keyword = '迅捷';   -- 括号关键字启发式抽取
```

## 复现 / 重建

最终产物可从 `workspace/rules_work.db` 幂等重建，无需重跑整条管线：

```powershell
python scripts/stage6/stage6a_coverage_check.py      # 6A 覆盖检查
python scripts/stage6/stage6b_build_rules_md.py      # 6B rules.md
python scripts/stage6/stage6c_build_rules_db.py      # 6C rules.db
python scripts/stage6/stage6d_build_change_log.py    # 6D change_log.md
python scripts/stage6/stage6e_build_manual_review.py # 6E manual_review.md
python scripts/stage6/stage6f_final_consistency.py   # 6F 五产物 × DB 一致性检查（只读）
```

早期阶段脚本（downloader / extract_pdfs / card_scraper / stage2x–stage5x）保留用于审计
与未来资料增量，当前语料下无需重跑。

## RAG 查询（本地 BGE-M3）

基于最终规则库的自然语言问答：**BGE-M3 向量召回 + 关键词（规则号/卡号/官方术语）
召回 → RRF 融合 → OpenAI 兼容 API 生成带引用的回答**。本地 CPU 即可，无需 GPU。

```powershell
# 环境准备（项目内 venv，依赖约 3 GB：CPU 版 torch + sentence-transformers + 模型权重）
python -m venv .venv
.\.venv\Scripts\python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python -m pip install sentence-transformers openai

# 构建向量索引（2984 条规则 → workspace/rag/，首次自动下载 BGE-M3 权重 ~2.2 GB）
.\.venv\Scripts\python scripts/rag/build_rag_index.py

# 检索 + 生成
.\.venv\Scripts\python scripts/rag/rag_query.py "反制堆叠有上限吗"

# 只看召回质量（不接 LLM，无需任何密钥）
.\.venv\Scripts\python scripts/rag/rag_query.py "OGN-131 现行怎么处理" --retrieve-only
```

生成端通过环境变量配置（任意 OpenAI 兼容服务）：
`OPENAI_API_KEY`、`OPENAI_BASE_URL`（如 `https://api.deepseek.com/v1`）、
`RAG_LLM_MODEL`（如 `deepseek-chat`）。回答中每条结论标注 [rule_id] 引用，
可回查 `workspace/final/rules.md` / `rules.db`。

向量产物在 `workspace/rag/`（已 gitignore，可随时用 build 脚本幂等重建）。

## 关键统计

| 指标 | 数量 |
|---|---|
| 来源文档 | 20（zh 11 / en 9） |
| Evidence | 5527（100% 已映射） |
| 规则 | 2984（全部 reconciled，来源覆盖率 100%） |
| 规则-证据链接 | 6353 |
| 变更记录 | 267 |
| 独立验证 | 393（392 verified + 1 verified_with_changes） |
| 冲突 | 1（R-CR-811.1.b 中文漏译从句，已按同版本英文优先原则裁决） |
| 人工复核 | 186（全部正式关闭） |

## 已知且有意保留的事项

- 4 张观察卡（OGN-131 / OGN-251 / UNL-097 / UNL-177）中文牌面待官方更新，现行口径按
  source_008 破限裁判 FAQ 第 4 节，watch 记录保留在 reconciliation notes 中。
- R-CR-811.1.b 的规范规则含按"同版本英文优先"补入的持续时间从句（CHG-5-0001），
  rules.md 中已标注。
- EV-CN-FAQ-0260 未链接到 R-CARD-OGN-251 的文档级警告如实保留。
- 中文裁判 FAQ（source_001/006/008）非官方 FAQ，按"裁判社区"效力层级挂载，
  各条前缀已标注。
