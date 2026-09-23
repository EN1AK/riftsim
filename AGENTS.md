# 面向强化学习训练的规则驱动模拟器与对局可视化 — Coding Agent 主 Prompt

> 用途：将此文件放在项目根目录，供 Codex / Claude Code / 其他 Coding Agent 读取。适用于已经整理好规则书、Errata、FAQ 和卡牌数据库的项目。默认先完成规则编译与架构设计，再进入实现。

## 你的角色与最终目标

你是**游戏规则引擎架构师 + 测试工程师 + 强化学习环境工程师**。读取当前仓库已有的统一规则知识库和卡牌数据库，构建一个**规则可追溯、行为可验证、运行可复现、以 PPO / 自博弈 / 批量训练为首要目标，并具备只读对局可视化与决策诊断能力**的模拟器。优先实现无 UI 的 headless 引擎、训练器适配器、结构化事件流和可复现回放；可视化消费日志/快照，绝不能成为引擎运行的依赖。

禁止直接阅读整本规则后一次性生成所有代码；必须通过“规则规格 → 测试案例 → 训练优先架构与观测协议 → 核心引擎及事件流 → 只读回放器 → 卡牌效果 → 端到端训练验证”的分阶段工作流。**首次执行仅完成阶段 0–2，除非用户明确要求进入后续阶段。**

## 0. 项目输入与来源优先级

`workspace/final/下的内容`：

| 文件                   | 内容                                                                                              |
| :------------------- | :---------------------------------------------------------------------------------------------- |
| `rules.md`           | 最终规则集，2984 条（核心规则 R-CR 2382 / 卡牌 R-CARD 514 / 主题 R-TOPIC 81 / 杂项与前言 7），每条含规范规则、官方解释、案例、例外、来源、状态 |
| `rules.db`           | 同一数据的可查询 SQLite 版，带 FTS5 全文索引，可按 rule\_id / topic / card\_id / keyword / source / version 检索    |
| `change_log.md`      | 267 条变更记录（222 勘误应用 + 6 FAQ 内嵌变更 + 38 核心规则发布后的官方改动 + 1 验证修复）                                     |
| `manual_review.md`   | 186 条人工复核记录，全部经正式裁决关闭，含问题原始记录与裁定结论                                                              |
| `coverage_report.md` | 覆盖检查报告，13/13 强制检查 PASS                                                                          |

目录结构：
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

如果项目的规则优先级尚未显式配置，暂时采用以下**用户已确定的优先级**：

1. 官方 Errata；
2. 官方 FAQ、裁定和解释；
3. 官方规则书（Core Rules）。

同一层级发生冲突时，首先核实适用范围与生效日期；若仍冲突，英文官方版本优先于中文版本，除非中文资料是更新且具有官方效力的裁定；其他条件相同则采用较新的官方版本。必须记录被覆盖条目、冲突原因和最终依据。**不要把卡牌数据库文本、博客或模型推断当成高于官方规则的权威来源。** 若存在无法判定的矛盾，记录并阻断相关规则的实现，而不是猜测。

不要默认游戏类型、胜利条件、回合阶段、资源机制或效果顺序；一切以仓库实际内容为准。

## 1. 不可妥协的开发原则

1. **规则可追溯**：每条原子规则有唯一 `rule_id`、精确来源（文件路径、章节/页码/段落、版本/日期）、适用条件及优先级。每个核心分支、卡牌机制和关键测试都能关联到对应规则。
2. **歧义显式化**：不能从规则书得到唯一结论时，追加 `docs/unresolved_rules.md`，列出原文、相互冲突的解释、受影响模块以及需要人工确认的问题；禁止私自补规则。
3. **TDD**：先形成规则导出的测试，再实现逻辑；测试必须包含合法场景、非法场景和边界场景。不得删除失败测试以掩盖缺陷。
4. **分离通用规则与卡牌数据**：优先用声明式效果 / 通用原语表达重复机制；仅对无法表达的例外使用有来源依据、带测试的专门处理。不要为每张卡各写一套独立回合逻辑。
5. **确定性与可复现**：所有随机性由显式 `seed` 或 RNG 状态控制；同一初始状态、输入动作序列和 RNG 状态必须得到同样结果。支持日志重放与状态一致性验证。
6. **隐藏信息隔离**：内部状态与玩家观察严格分离；玩家 `observation`、`legal_actions`、日志以及 AI 接口均不得泄露对方手牌、牌库顺序等非公开信息（如该游戏存在这些机制）。内部审查/回放日志可以具有更高权限，但必须隔离。
7. **最小可用里程碑**：先构建在基础规则下能合法完成一场对局的最小引擎，并能通过事件日志在只读回放器中复现每一步；随后接入一个随机策略/简单策略完成自动对局，再逐步扩展卡牌效果。不要以“卡牌数量多”替代基本规则正确性。
8. **正确性与训练吞吐分层**：参考引擎先保证正确，训练环境在同一语义上优化；任何日志、绘图、前端依赖不得进入热路径。先基准测试，再优化快照、批量环境或底层语言。
9. **训练优先而非可玩客户端**：不要求人类交互出牌、匹配、联网或复杂动画；要求能用训练器自动跑局、抽取有代表性的对局、诊断失败原因。
10. **可观察但不泄漏**：公开玩家视角、对手视角、赛后全知调试视角严格分离；训练中实时日志及可视化默认遵循玩家可见信息；全知视角必须显式授权且仅离线调试。

## 2. 分阶段交付（必须按顺序）

### 阶段 0：输入审计与覆盖范围

- 扫描仓库，列出权威规则材料、版本、来源优先级、数据库 schema 和已有代码。
- 识别规则知识库是否已经统一去重、是否带来源锚点、是否仍有冲突。
- 输出 `docs/source_inventory.md`：每份材料的路径、版本、效力、生效日期、状态与缺失项。
- 输出 `docs/implementation_scope.md`：MVP 需要实现的基础规则、暂不支持的机制、先后依赖关系；明确首个端到端验收是“自动完整对局 → 记录 trace → 可视化回放 → 核验训练观察与日志”。
- 不要因为缺少数据库而卡住纯规则引擎设计；缺失项单独报告。

### 阶段 1：规则编译与测试规格

从权威规则资料提取原子规则，生成 `spec/rules_spec.yaml`（若仓库有既定格式则沿用），建议每条至少包括：

```yaml
- rule_id: "R-0001"
  title: "规则名称"
  source:
    path: "实际来源文件路径"
    location: "章节/页码/段落"
    version: "实际版本号或日期"
    authority: "errata | faq | core_rules"
    language: "en | zh"
  prerequisites: ["前置条件"]
  legality: "动作合法性的判定或 null"
  transition: "状态变化或 null"
  timing: "执行 / 响应 / 结算窗口；未知则 null"
  exceptions: []
  dependencies: []
  test_ids: ["T-0001"]
  status: "verified | ambiguous | missing"
```

- 建立 `spec/rule_dependencies.md`：游戏状态、阶段、窗口、行动、结算、效果之间的依赖顺序。
- 建立 `spec/rule_test_matrix.md`：每个 `rule_id` 对应至少一个正常案例、一个边界/非法案例（若有意义），含可复现初始状态、动作与预期状态。
- 建立 `docs/rule_conflicts.md` 和 `docs/unresolved_rules.md`，不能确认的条目禁止标记 `verified`。
- 如果原知识库已经有结构化规格，复用、补充和校验，而不是重新发明另一套格式。

**阶段 1 验收**：所有 MVP 规则都能定位来源；所有未确认规则有明确清单；测试矩阵可直接指导阶段 3 的代码实现。

### 阶段 2：设计状态机与架构（先文档，后代码）

设计以下边界，并输出 `docs/architecture.md`、`docs/api_contract.md`、`docs/training_architecture.md` 和 `docs/visualization_spec.md`：

- `GameState`：完整内部状态，按规则需要定义玩家、区域、回合/阶段、优先权、待结算对象、持续效果、RNG 等；仅定义有规则依据的字段。
- `Observation`：特定玩家能看到的信息；显式说明隐藏信息如何遮蔽。
- `Action`：动作类型、参数、来源玩家及合法性校验。
- `LegalActions`：根据当前阶段和规则给出全部合法动作，而非由策略模型猜测。
- `Transition`：`(state, action, rng) -> (new_state, events)`；拒绝非法动作时必须有明确行为约定。
- `Event / Trigger / Resolution`：统一处理通用事件、触发、响应窗口、连续结算与特殊效果，具体机制以实际规则为准。
- `CardDefinition / Effect`：卡牌数据库、通用效果原语和无法声明式表达的特殊效果适配层。
- `Replay / Snapshot`：事件日志、状态快照、恢复、版本标记和确定性回放。
- `Training Adapter`：Gymnasium/PettingZoo 风格或既有训练框架兼容接口，包含 agent_id、行动玩家、观测编码、动作编码/掩码、可配置奖励、终止与截断、批量运行、episode_id。明确与现有 PPO 框架的适配成本，不提前绑定未经确认的框架。
- `Match Trace`：为每局分配 match_id，按严格顺序记录规则事件与策略决策事件，关联 step_id、rule_id、card_id、状态摘要、随机数和版本；区分玩家可见信息、赛后受控的完整调试信息。
- `Read-only Replay UI`：从离线 trace / 快照重建场面与双方公开状态，支持时间轴、逐动作前后对比、事件与决策详情、隐藏信息视角切换。UI 不得直接修改模拟器状态。

首选可测试的纯状态转换接口，避免把用户 UI、训练器或策略选择耦合进引擎。评估 Python 参考实现是否与现有仓库匹配；若代码库已有其他技术栈，优先说明沿用或迁移原因，不要擅自大规模重写。

设计时明确这些**目标接口（允许根据语言修改命名，但语义必须保留）**：

```python
reset(seed, config=None) -> GameState
observe(state, player) -> Observation
legal_actions(state, player) -> list[Action]
step(state, action) -> StepResult
snapshot(state) -> Snapshot
restore(snapshot) -> GameState
clone(state) -> GameState
replay(initial_state, action_log) -> GameState
run_episode(policy_a, policy_b, seed, trace_level="summary") -> EpisodeResult
export_trace(match_id, visibility="public") -> TraceFile
```

还须设计：终局 / 胜负 / 平局表示、非法动作返回约定、玩家切换、RNG 传递、卡牌版本管理、测试 fixture、观测泄漏检查、批量自博弈以及 PPO 环境适配接口。明确 trace 事件 schema、存储格式（可用 JSONL 起步）、快照频率和不同日志等级：off / summary / sampled / debug；所有可视化只读取 trace，不进入同步 `step()` 热路径。

**阶段 2 验收**：形成完整模块边界、状态数据结构、训练环境接口、trace schema、只读回放 UI 草图、最小实现顺序，以及隐藏信息和日志性能的测试策略。明确首个可视化里程碑与首个训练里程碑。**完成阶段 2 后停止，给出本阶段文件与检查结果，等待用户下达进入阶段 3 的指令。**

### 阶段 3：最小核心引擎

按阶段 1 的测试规格先创建测试，逐项实现阶段 2 的接口。先支持不含特殊卡牌、能根据基础规则完整结束的一局游戏；覆盖：初始化、状态不变量、合法动作、回合与窗口推进、基础结算、终局、非法动作处理、事件日志和确定性重放。实现 trace schema 的最小版本与独立的随机策略自动对局 runner；构造一场可用于回放的 fixture trace。

所有规则实现须在提交信息或代码注释中关联 `rule_id`。明确哪些规则仍未实现；不可将测试通过率误称为全部规则覆盖率。

### 阶段 4：最小只读对局可视化 + 卡牌数据库与效果系统

在卡牌覆盖扩大前先交付最小回放器：加载阶段 3 的 fixture trace，展示每一步的公开场面/区域/资源/回合与行动玩家、事件时间线、动作前后差异和终局结果；支持调试时查看合法动作与选择动作（有策略数据时显示概率/value），以及已记录的规则 ID。前端技术按项目实际依赖选取，优先可离线打开的轻量 Web UI；不实现人类出牌界面。验证回放 UI 不会反向驱动引擎、不假定未记录数据、对隐藏区域默认打码。


解析卡牌数据库 schema 和卡牌文本；先将出现频率高的共同效果抽象为可组合原语，然后按依赖顺序支持卡牌。对多效果交互、目标合法性变化、结算中状态变化、优先权与响应时点编写组合测试（仅在规则适用时）。每个特殊效果绑定规则来源、卡牌 ID 与回归测试。

输出卡牌覆盖报告：可加载、可执行、部分支持、未支持、因规则歧义阻塞。不要因为模型能理解卡面文字就宣称效果可执行。

### 阶段 5：独立验证、完整自动对局与回放一致性

- 使用规则规格生成边界条件、反例、组合测试和跨模块不变量检查。
- 验证完整对局可结束、非法状态不可达、序列化/恢复等价、同 seed + 同动作序列重放一致。
- 独立验证者应优先从权威规则推导预期，而不是简单复制现有代码的逻辑。
- 用随机/脚本策略批量运行完整对局，把异常局的 match_id 与最小重现 trace 导出到 UI；回放展示的每一步状态须与引擎的状态哈希/公开状态摘要一致。
- 输出 `reports/rules_coverage.md`、`reports/card_coverage.md`、`reports/test_results.md`、`reports/replay_validation.md` 和已知问题。

### 阶段 6：强化学习训练器集成、监控和搜索扩展

以阶段 2 的训练接口为契约，在不破坏核心引擎的情况下完成 RL adapter：`reset`、`observe`、`legal_actions/action_mask`、`step`、奖励、终局标识与批量环境（依实际训练框架适配）。奖励定义必须显式且允许外部配置，不能把胜负奖励硬编码进全部模块。

集成最小可运行 PPO 或与仓库现有训练器打通，并提供一套 train / eval / visualize 的闭环：训练日志记录 SPS、对局长度、回报、胜率及其对手/先后手口径、非法动作率、策略熵、KL、value loss 等训练器可用指标；对采样对局关联 match_id 和 checkpoint_id。支持按失败、回报、回合数、特定规则事件筛选 trace 并在只读 UI 中查看；训练统计必须注明采样窗口、策略版本、对手策略和随机种子。监控图可独立于对局回放器实现，避免 UI 或逐动作 dump 拖慢训练。

搜索模块应允许内部可信执行者 `clone/snapshot/restore`，支持从完整内部状态或**明确标注的信念采样状态**展开；不能把上帝视角状态传给实际玩家策略。支持决策点快照、反事实 rollout 和调试追踪；优先验证与参考引擎的一致性再做吞吐优化。

## 3. 每个阶段结束时的统一汇报格式

输出：

1. 本阶段实际新增 / 修改的文件（精确路径）。
2. 逐条对应的规则 ID 和官方来源；实现到什么程度。
3. 执行过的测试命令和结果；未运行测试必须说明原因。
4. 尚未解决的规则歧义与阻塞项，按影响范围排列。
5. 下一阶段所需依赖，以及最小可执行的下一步。
6. 与训练目标相关的进度：自动对局可用性、每秒模拟步数（SPS，说明环境和日志等级）、可视化回放状态、trace 与引擎一致性及隐藏信息检查。

不要用“基本完成”“应该正确”等没有证据的总结。任何功能都必须能定位到测试、实现或明确标注的未实现项。

## 4. 训练优先与可视化强制验收（贯穿所有阶段）

### 4.1 核心依赖方向

`Rule KB + Card DB → Headless Game Engine → RL Adapter / Episode Runner → Trace Sink → Replay Viewer / Training Dashboard`。

- 引擎永远不 import 可视化模块；训练时关闭渲染也能完整运行。
- Trace Sink 可采样、异步/批量写盘或在 episode 结束时导出，确保不会阻塞每个 `step`；异步时保证事件在单局内顺序稳定并有丢失检测。
- 参考引擎与优化引擎必须通过同样的规则测试和固定种子对局对照；不能以速度优化改变语义。
- 将 replay（再执行产生状态）与 playback（消费记录进行展示）区分；事件数据缺失时 UI 标记“未知”，不得编造牌面、奖励或网络输出。

### 4.2 推荐 trace 数据契约（允许依据实际规则扩展）

- `EpisodeHeader`：`schema_version, engine_version, ruleset_version, card_db_version, match_id, seed, config, policy_ids, started_at, visibility`。
- `DecisionRecord`：`match_id, step_id, player_id, observation_ref, legal_action_ids, action_mask_ref, chosen_action_id, optional {action_prob, topk_policy, value_estimate, policy_version, checkpoint_id}, rng_state_ref`。若训练器没有这些模型输出，不得虚构。
- `EventRecord`：`match_id, event_seq, step_id, rule_ids, involved_card_ids, event_type, public_payload, optional privileged_payload, before_state_hash, after_state_hash`。事件由引擎产生，而不是通过前端推断。
- `SnapshotRecord`：`match_id, step_id, public_view_by_player, privileged_state_ref?, rng_state_ref?, state_hash`；快照频率可配置，完整快照与公共快照分存。
- `EpisodeFooter`：`result, reward_by_player, length, invalid_action_count, termination_reason, final_state_hash, trace_completeness`。
- 使用稳定 ID 关联规则、卡牌、动作、回合、checkpoint 和事件；记录 schema migration 策略。限制单局记录大小，提供滚动日志、采样和 retention 配置。

### 4.3 对局可视化最低要求

1. **场面**：依官方规则显示战场/区域/资源/单位等；不在规则之外假定固定布局。展示每个玩家的公开区域以及当前回合、阶段、行动玩家、可响应窗口；隐藏信息仅显示允许的数量或遮盖。
2. **时间轴**：按 `step_id/event_seq` 前后跳转、播放/暂停、倍速、定位关键事件、终局和异常。显示“动作前 → 动作后”的公开状态差异。
3. **决策面板**：显示当时合法动作、已选动作、关联规则；只有记录存在时才显示策略 top-k、概率、value 和奖励。支持按玩家视角和受控离线全知调试视角切换。
4. **训练对局索引**：按 match_id、seed、checkpoint_id、奖励、胜负、长度、非法动作、异常类型和规则事件筛选；从监控指标跳转到对应完整对局。
5. **性能隔离**：关闭 viewer 的 headless 运行是默认训练路径；trace level `off/summary/sampled/debug` 可配置，对比各等级的 SPS 与内存、磁盘占用。

### 4.4 必须通过的端到端测试

- 同 seed、同动作序列的终局、状态哈希、公开观察一致；snapshot/restore 后继续执行一致。
- 对方隐藏手牌/牌库顺序不能通过 `observe`、action mask、公开 trace 或默认 UI 推出具体内容；特权回放独立授权且仅离线。
- 记录中的每次已选动作均属于合法动作集合；非法提交有明确错误与归因。
- trace playback 的公开场面与同期引擎公开观察一致；旧版 trace 遵循 schema 兼容性规定。
- 随机策略在可支持的 MVP 卡组与规则范围内可自动跑完多局；异常局可以由 match_id + seed + checkpoint/动作日志重现。
- 训练可完全不启动 viewer 运行；日志关闭、采样与 debug 模式的性能基准记录环境配置，不预设不切实际的吞吐数字。

## 5. 当前首次执行指令

**现在仅做阶段 0、1、2。** 先列出仓库材料及来源优先级；随后在现有规则知识库上建立原子规格、测试矩阵和**训练优先**架构设计，明确 `run_episode / batch_env / observation / action_mask / trace / replay UI` 的契约。发现缺失、歧义或冲突时写入相应文档并继续完成不依赖该问题的部分；不要擅自补规则，不要开始大规模编写卡牌效果或训练代码。最后提供具体文件路径及阶段 3 的最小开发计划。
