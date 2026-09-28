# 阶段 2 架构设计（docs/architecture.md）

> 依据：AGENTS.md 阶段 2；输入：`spec/rule_semantics.yaml`（166 机制）、
> `spec/rule_dependencies.md`（判定/结算顺序）、`spec/rule_test_matrix.md`（134 案例）。
> 原则：训练优先 headless；规则可追溯；确定性；隐藏信息隔离；可视化只读且不进热路径。
> 本文件：模块边界、状态机、主循环、RNG、版本、实现顺序与里程碑、测试策略。
> 接口签名与字段见 `docs/api_contract.md`。

## 1. 技术栈与依赖边界

- **引擎核心**：纯 Python 3.12，标准库 only（dataclasses/enum/hashlib/json/copy），
  不依赖 numpy/torch/gymnasium——保证训练环境以任何框架包装。
- **训练适配层**（`rl/`）：可选 extras；编码器用 numpy（可选），
  Gymnasium/PettingZoo 兼容仅做薄包装，未安装时 core/runner 完全可用。
- **可视化**（阶段 4）：独立目录 `viewer/`，单文件离线 HTML+vanilla JS，只读 trace JSONL；
  引擎任何模块不得 import viewer。
- 方向锁定：`规则规格 → engine core → trace sink → runner → rl adapter → viewer`。

## 2. 模块布局（src/riftsim/）

```
src/riftsim/
  __init__.py
  version.py      # ENGINE_VERSION / RULESET_VERSION / SPEC_HASH / TRACE_SCHEMA_VERSION
  errors.py       # IllegalActionError / EngineInvariantError / ReplayMismatchError
  enums.py        # ZoneId/CardType/TurnStateMode/PhaseId/Keyword/Counter 等（规则锚定注释）
  rng.py          # RngStreams：seed→命名子流（setup_shuffle/battlefield/mulligan/recycle/effect…）
  cards.py        # CardDefinition + 骨架卡池注册表（阶段 4 接 cards_bilingual/KB canonical）
  objects.py      # GameObject/AttachmentStack/Counter/uid 分配器
  state.py        # GameState/PlayerState（含哈希与规范序列化）
  observation.py  # Observation 构造与私有过滤（observe()）
  actions.py      # Action/DecisionRequest/DecisionKind 定义与编码
  legality.py     # legal_actions：六门判定（依赖 rule_dependencies §3）
  engine.py       # step()/transition 主入口 + InvariantChecker
  phaser.py       # 阶段推进（315/316/317）与清理解释器（318..324）
  chain.py        # 结算链 + 任务队列 + FEPR 循环（325..340）+ 对决（341..348）
  playing.py      # 打出六步（349..359）与技能打出五步（401..406）
  effects.py      # 效果注册表：替换/延迟/持续 Layers 骨架（MVP 挂点，P1 补全）
  triggers.py     # 触发注册表与入链排序（382..385）
  combat.py       # 战斗三步（459..466）
  scoring.py      # 得分/终局/认输（467..472 / 649..652 / 193..196）
  snapshot.py     # snapshot/restore/clone/state_hash
  replay.py       # replay()/校验（动作日志→状态哈希链）
  fixture.py      # 注入式状态构造 DSL（测试专用；trace/训练不得依赖）
  trace/
    __init__.py
    schema.py     # EpisodeHeader/DecisionRecord/EventRecord/SnapshotRecord/EpisodeFooter
    sink.py       # TraceSink 协议：off/summary/sampled/debug + 批量写盘
  runner.py       # run_episode(policy_a, policy_b, seed, trace_level)
  policies.py     # RandomPolicy/ScriptedPolicy（runner 自举与回归用）
  rl/
    __init__.py   # 懒加载；缺依赖时 import 失败提示，不影响 core
    encoder.py    # Observation→特征表/Mask（接口 + numpy 参考实现）
    env.py        # RiftEnv（PettingZoo AEC 风格薄包装）
    vecenv.py     # 批量 episode 运行器（同步）
viewer/           # 阶段 4 交付；单文件 index.html；只读 traces/*.jsonl
tests/            # pytest；test_matrix 案例逐一映射 T-xxxx
```

## 3. 核心执行模型：需求驱动半自动机

规则自动执行与玩家决策统一为一个抽象：

- 引擎维护**任务队列**（Task：清理/FEPR 步/结算/等待玩家决策）。
- `step(state, action)` 的语义 = *对当前 `DecisionRequest` 提交回答*；
  规则可自动推进的部分（阶段子步骤、FEPR 无分支步、清理无选项步）在引擎内部消费，
  **只有必须玩家输入时引擎才停在请求点**（Bellman 意义上的决策点）：
  - `MAIN_ACTION`（自决行动：打出/激活/移动/待命/结束主阶段）
  - `REACTION_EXECUTE`（FEPR 执行窗口：加反应/让过，R-CR-338/339）
  - `SHOWDOWN_FOCUS`（对决焦点行动：打出/激活/让过焦点，R-CR-347）
  - `CHOOSE_*`（目标/位置/模式/分摊/多选一场对决或战斗/调度/触发排序/替换排序/洞察去留）
  - `COMBAT_ASSIGN`（战斗伤害分配，进攻方先、后防守方，R-CR-465.2）
- `legal_actions(state, player)` 永远是"当前请求下该玩家的全部合法回答"，
  由六门判定求值（窗口门→时机权限门→对象门→位置门→费用门→结算复核见 legality 文档）。
  非请求玩家的合法集为空（终局后全员为空）。
- 不变量：同一 `state_hash` + 同一 action → 同一新 `state_hash` + 同一事件序列
  （事件含 rng 消耗引用；重放校验据此逐条核对）。

**为什么不把阶段推进也做成 Action**：阶段/清理/FEPR 的强制部分是规则驱动的任务，
做成玩家动作会让策略空间被无意义选择淹没，违背训练吞吐目标；保留"结束主阶段"
（唯一由规则授权的自决过渡，R-CR-305/335）为显式动作。

## 4. GameState 结构（仅含规则依据字段）

```text
GameState
├─ meta: {engine_version, ruleset_version, spec_hash, card_pool_version,
│         match_id, seed, config(GameModeConfig: players=2, win_score=8,
│         decklists, battlefield_options, trace_level...)}
├─ progression: {turn_player:int(座位), turn_number:int,
│   phase:PhaseId(AWAKEN/BEGIN/CHANNEL/DRAW/MAIN/ENDING/CLEANUP...),
│   sub_step:枚举, ended:bool, winner:int|None, termination:枚举|None}
├─ derived 缓存（可重算）: turn_state(mode×link) ← chain 非空 / 对决·战斗中；
│   priority_player:int|None; focus_player:int|None
├─ players[2]: {hand:[uid], main_deck:[uid](有序=隐秘), rune_deck:[uid],
│   trash:[uid], banish:[uid], hero_zone:[uid], legend_zone:[uid],
│   rune_pool:{energy:int, power:{R:int,G:int,...}},
│   score:int, score_markers:{(battlefield_uid):得分回合号集},
│   conceded:bool, prepared_ready:int(首回合召出数修正=3/2)}
├─ battlefields[2]: {uid, card_def, controller:int|None, contested:bool,
│   showdown_pending:bool, combat_pending:bool,
│   showdown_active:bool, combat:CombatContext|None,
│   hidden_slot:[uid](≤1), occupants:[uid]}
├─ base[2]: {occupants:[uid]}  # 基地（含符文落的落点按模式）
├─ chain: [ChainItem]           # 结算链（空=不存在，R-CR-330）
│   ChainItem: {id, kind:CARD|ABILITY|TRIGGER|REFLEXIVE, source_uid, controller,
│     status:PENDING|FINALIZED, choices(已锁定), targets, total_cost, paid,
│     origin_zone, created_seq, trigger_meta(最后状态快照等)}
├─ tasks: TaskQueue             # cleanup(FEPR 抑制中)/fepr_step/resolution 等
├─ effects: {replacements:[], delayed:[], continuous:[],
│   timestamps:Counter, suppressions:set(text_id),
│   granted_keywords:{uid:{kw:expire}}, empower:set(uid)}
├─ triggers: 注册表（常驻牌/传奇技能按 uid 索引；攻守触发每场战斗计数）
├─ objects: {uid:GameObject}    # 卡牌实例/符文/传奇/战场/指示物/计数标
│   GameObject: {uid, def_id, owner, controller, zone, zone_index,
│     damage:int, exhausted:bool, stunned:bool, face_down:bool,
│     keywords_base:set, attachments:[uid]/attached_to:uid|None(top-card 模型),
│     counters:{type:count}, last_known_info(离场后绝念结算用)}
├─ rng: RngStreams{各流状态}
├─ stats: {step_id, event_seq, invalid_action_count, cleanups_run}
└─ current_request: DecisionRequest|None   # 当前等待的回答
```

派生不存：回合四态、致命判定、强力判定、Layers 重算后的"有效属性"（读取口
`view_of(uid)` 现算，P1 Layers 就位后接缓存）。

## 5. 主循环不变量（step 内部）

```
on step(action):
  assert action ∈ legal_actions(current_request)
  apply(action)                       # 合法回答，原子提交
  loop:                               # 规则自动推进直到下一个请求点或终局
    run due TASK in priority order:   # rule_dependencies §4 次序
      cleanup? → cleanup()            # 323.1..323.14 + 322 迭代；抑制窗口互斥 320/321
      fepr?    → fepr_step()          # 337..340；含 337.2/400.2/429.2 立即结算分支
      showdown/combat pending & allowed → 开启（323.12/13/14；回合玩家多场次选择 = 请求点）
      combat.step2 需要分配 → 请求点（COMBAT_ASSIGN）
      resolution → 触发注册表收殖（383 入链序）→ 完全静默
    if any TASK produced: continue
    break
  if next_phase_edge: 推进阶段/回合（315/316/317；唤醒/召出/抽牌含燃尽 431）
  emit events; state_hash; trace
return StepResult(...)
```

- 终局检查只在清理 323.1 / 效果获胜 / 认输 / 燃尽 431.3.c.1 四处判定。
- 非法动作：**不修改状态**，抛 `IllegalActionError`，由调用方（runner）在
  `EpisodeResult.invalid_action_count` 归因记录；引擎内部不产生半状态。

## 6. RNG 设计

- 单一入口 seed（int）。`RngStreams.from_seed(seed)` 按用途派生命名子流
  （`random.Random(hash(seed, name))`），用途固定且**消费顺序在主循环内确定**：
  `battlefield_pick` → `shuffle_main_a/b` → `shuffle_rune_a/b` → `mulligan` →
  `recycle_random_order` → `effect_random`（效果随机，如随机弃置/分发）。
- snapshot 保存各流 `getstate()`；trace 的 `rng_state_ref` 记录（流名, 消费计数）。
- 所有随机选择（燃尽洗牌、调度回收置底顺序 416.5、战场随机选定 485）
  必须经由这些流；引擎代码禁用全局 random。

## 7. 确定性、快照与哈希

- `state_hash(state)`：规范序列化（字段剔除派生缓存与 trace 挂钩点）后 sha256；
  快照/事件前后双哈希写入 EventRecord。
- `snapshot(state)` → JSON-safe dict + `snapshot_version`；
  `restore()` 校验版本；`clone()` = deepcopy（仅搜索/调试可信执行者）。
- `replay(initial_snapshot_or_config, action_log)`：逐步重放并比对
  每步 after_hash 与 trace 记录；不一致抛 `ReplayMismatchError(step_id)`。
- 观测泄漏检查（测试）：`observe(p)` 输出中的对象引用集 ∩ 对手私有/隐秘 uid = ∅。

## 8. 实现顺序（阶段 3 任务分解；每步配测试矩阵案例）

M1 骨架引擎（首个里程碑）：
1. `enums/objects/state/rng` + `fixture.py`（T-0015）  2. 组卡校验+Setup（T-0001..T-0013）
3. 阶段推进/回合队列（T-0012/0035/0038/0039/0042/0043）
4. 符文池/召出/抽牌/燃尽（T-0028..T-0034/0040/0041）
5. 链+FEPR+四态派生（T-0045..T-0057/0036）
6. 打出六步框架（无效果文本骨架卡，T-0023/0025/0026/0061）
7. 移动/召回（T-0077..T-0082/0100） 8. 对决（T-0058..T-0060/0078/0094）
9. 战斗三步（T-0083..T-0093） 10. 得分/终局/认输（T-0014/0095..T-0099/0101）
11. 随机策略 + runner + 收敛测（T-0134/0132/0133/0131）
12. trace sink minimal + 回放校验（T-0131）→ **fixture trace 产出**
M2（阶段 4）：回放器 VM-1 + 增益/贴附/关键词子集（T-0102..T-0124）。
M3（阶段 6）：RL adapter TM-1（批量 100 局+指标+UI 抽检一致）。

性能预算说明：M1 不做任何向量化；热路径禁 JSON dump（trace 批量缓冲）；
引用引擎与"优化版"若未来分歧，必须同过全矩阵并对拍固定 seed 局。

## 9. 测试策略

- **TDD 映射**：`tests/test_matrix/test_t0001_deck.py` … 文件名含 T-xxxx；
  每个案例 fixture 构造 → 执行 → 断言 expect；illegal 用例断言 `IllegalActionError`
  且状态哈希不变。
- **fixture DSL**（`fixture.py`）：声明式注入（区域成员/伤害/符文池/控制/持续效果/
  待处理项），禁止手搓内部结构绕过不变量；fixture 构建后强制 `InvariantChecker` 全检。
- **不变量集**：区域排他、uid 唯一、链状态机合法演进、隐私隔离（观察差集断言）、
  分数单调区间、符文池清空时点（事件序断言）。
- **确定性与回放**：固定 seed × N 局哈希链比对；snapshot/restore 后等价演化（T-0133）。
- **泄漏测试**：每次 `observe`/`export_trace(public)` 后执行对手私有 uid 交集断言。
- **性能哨兵**（阶段 6 激活）：`bench/sps_bench.py` 记录 trace 各等级 SPS/内存/磁盘。

## 10. 首个可视化里程碑 VM-1 与首个训练里程碑 TM-1（验收定义）

- **VM-1**（阶段 4 初）：加载 M1 产出的 fixture trace，UI 能按 step 展示双方公开场面
  （基地/战场/待命区/废牌堆计数/符文池/分数/回合阶段/行动玩家）、事件时间轴、
  前后差异、终局结果；隐藏区打码；不进行任何引擎调用。
- **TM-1**（阶段 6 初）：随机/脚本策略在 adapter 下批量跑 100 局；
  指标（SPS、回合长度、胜率含先后手口径、非法率）落盘；抽样 5 局 match_id 于 UI
  逐帧与引擎公开观察一致；trace 等级 off/summary/debug 的 SPS 对比记录。
