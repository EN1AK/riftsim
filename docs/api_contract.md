# API 契约（docs/api_contract.md）

> 阶段 2 交付物。引擎对外接口签名、数据结构字段、行为约定。
> 命名可按实现微调，**语义不得偏离**（AGENTS.md 阶段 2 接口清单）。
> 关联：状态结构见 `docs/architecture.md` §4/§5；trace 逐字段 schema 见
> `docs/visualization_spec.md` §2；训练编码见 `docs/training_architecture.md`。

## 1. 十接口总表

```python
reset(seed: int, config: GameConfig | None = None) -> GameState
observe(state: GameState, player: int) -> Observation
legal_actions(state: GameState, player: int) -> list[Action]
step(state: GameState, action: Action) -> StepResult
snapshot(state: GameState) -> Snapshot
restore(snap: Snapshot) -> GameState
clone(state: GameState) -> GameState
replay(initial: Snapshot | GameConfig, action_log: Sequence[Action], *,
       seed: int | None = None) -> GameState
run_episode(policy_a: Policy, policy_b: Policy, seed: int,
            *, trace_level: TraceLevel = "summary",
            config: GameConfig | None = None) -> EpisodeResult
export_trace(match_id: str, *, visibility: Visibility = "public",
             out_dir: str | None = None) -> TraceFile
```

约定：
- `player`/`actor` 为座位号 `0|1`；`agent_id` 训练层另行映射（见 training 文档）。
- 所有函数对引擎核心零 IO；唯一写盘点是 TraceSink（异步/批量，可关）。
- 非法动作：`step` **不改状态**并抛 `IllegalActionError(step_id, player, action_digest, reason, legal_digest)`；
  测试用 `pytest.raises`；runner 归因到 `invalid_action_count`。

## 2. GameConfig / GameModeConfig

```python
@dataclass(frozen=True)
class GameConfig:
    mode: str = "duel_1v1"          # 仅支持 duel_1v1（R-CR-485）
    win_score: int = 8              # R-CR-485
    decks: tuple[DeckList, DeckList]  # F-DECK-A/B 或骨架池卡组描述
    battlefield_pool: tuple[list[str], list[str]]  # 各 3 个，setup 随机选 1
    trace_level: TraceLevel = "summary"
    max_steps: int = 5000           # 截断阈值（训练用；deadlock 哨兵 T-0134）
    match_id: str | None = None     # None → runner 生成
    spec_version: str | None = None # 启动时断言与 rules_spec.yaml hash 一致
```
- 卡组经 `MECH-DECK-CONSTRUCTION` 全量校验（T-0001..T-0006）；
  校验失败 `reset` 抛 `DeckValidationError(violations)`。
- 骨架卡池（阶段 3）：`skeleton-v1`＝无文本单位/装备/法术＋基本符文＋空效果战场/传奇；
  `card_db_version` 记池标识与内容哈希。

## 3. Observation（单玩家视角）

```python
@dataclass
class Observation:
    viewer: int
    match_id: str
    step_id: int
    turn: TurnView          # turn_player, turn_number, phase, sub_step
    turn_state: TurnState   # mode(normal|showdown) × link(open|closed)（派生）
    acting: ActingInfo      # 当前请求与本玩家关系；request_kind | None
    public: PublicBoard     # 基地×2、战场×2（uid、def_id、控制、争夺、伤害/休眠/增益等公开属性）
    hidden_public: HiddenPublic  # 待命区存在性与归属（内容打码）
    self_private: SelfPrivate    # 自己手牌详情（uid、def_id）、自己待命牌内容
    counts: Counts          # 双方：手牌数 牌堆数 废牌堆数 放逐数；符文池双方（见 OPEN-5）
    scores: tuple[int, int]
    legal: LegalView        # legal_action_ids（int）+ mask(bitarray 序列化)
    request: DecisionRequestView | None  # 当前请求的公开参数化
    version: ObsVersion     # obs_schema 版本号
```
私有过滤（T-0130）：对手手牌/牌堆内容/待命内容**绝不进入**；
`Observation` 中 uid 只允许公开或本玩家私有 uid 两类；uid 不是 def 内容的通道
（def_id 仅对公开/自身对象暴露，隐藏对象统一 `face_down` 占位）。

## 4. Action / DecisionRequest 协议

```python
@dataclass(frozen=True)
class Action:
    kind: ActionKind        # 见 §6 枚举
    actor: int              # 必须 == current_request.player
    source_uid: int | None = None      # 卡牌/技能来源
    params: dict[str, Any] = None      # 目标 uid 列表/位置/分摊表/选择索引…（schema 依 kind）
```
- `DecisionRequest`：引擎停在决策点时生成，`{kind, player, options}`；
  `legal_actions` 对 `options` 做全量展开（实例化候选 Action）。
- 请求种类（DecisionKind）：`MAIN_ACTION / REACTION_EXECUTE / SHOWDOWN_FOCUS /
  CHOOSE_TARGETS / CHOOSE_LOCATION / CHOOSE_MODE / ASSIGN_DAMAGE /
  CHOOSE_BATTLEFIELD_NEXT / MULLIGAN / ORDER_TRIGGERS / ORDER_REPLACEMENTS /
  SCOUT_KEEP / PASS_PRIORITY(SHOWDOWN 内让过通过 SHOWDOWN_FOCUS 表达)`。
- 结构约束：`step()` 前行不变量 `state.current_request is not None`；
  `action.actor == state.current_request.player`（否则非法）。

## 5. StepResult / EpisodeResult

```python
@dataclass
class StepResult:
    state: GameState
    events: list[GameEvent]   # 本步产生的事件（见 §7）
    request: DecisionRequest | None  # 下一个决策点；终局 None
    done: bool
    info: dict                # {score_delta, cleanup_count, chain_depth_peak...}

@dataclass
class EpisodeResult:
    match_id: str
    winner: int | None                # 1v1 无平局："None"仅在截断/异常
    termination: TerminationReason    # SCORE|EFFECT_WIN|CONCEDE|BURNOUT|TRUNCATED|ERROR
    length_steps: int
    final_scores: tuple[int, int]
    reward: dict[int, float]          # 由 RewardConfig 计算，默认 {winner:+1, loser:-1}
    invalid_action_count: int
    final_state_hash: str
    trace_path: str | None            # trace_level=off 时 None
    config: GameConfig
    started_at: str                   # ISO8601
```
- 1v1 无平局定义（R-CR-194）：分数并列→对局继续；截断不产生胜者语义，
  `reward` 按 RewardConfig.truncated 处理（默认 0/0）。

## 6. ActionKind 枚举（MVP 全集）

| kind | 规则锚 | 说明 |
|---|---|---|
| `PLAY_CARD` | R-CR-349 | 打出（手牌/待命/英雄区/废牌堆[流转]），params=目标/位置/额外费用选择 |
| `ACTIVATE_ABILITY` | R-CR-401/377 | 激活主动技能（params=技能索引+选择） |
| `STD_MOVE` | R-CR-144/447 | 标准移动（params=单位 uid+终点位置） |
| `HIDE` | R-CR-421/811.1.b | 待命（params=卡 uid+战场） |
| `END_MAIN` | R-CR-305/335 | 结束主阶段 |
| `EXECUTE_REACTION` | R-CR-338 | 执行窗口：加反应（嵌套 PLAY/ACTIVATE）或 NOTHING |
| `PASS` | R-CR-339/347 | 让过/让过焦点 |
| `RESOLVE_CHOICE` | CHOOSE_* | 统一"选择回答"：MULLIGAN/目标/位置/模式/触发序/替换序/洞察去留/选场次 |
| `ASSIGN_DAMAGE` | R-CR-465.2 | 分配表（unit_uid→amount），合法集合由分配器枚举 |
| `CONCEDE` | R-CR-650 | 认输（恒合法，任何请求态可用） |

## 7. 事件类型（GameEvent，引擎产生，UI 不推断）

```python
@dataclass
class GameEvent:
    match_id: str
    event_seq: int            # 局内严格递增
    step_id: int
    type: EventType           # 见下
    rule_ids: list[str]       # 锚定（可为多个）
    card_ids: list[str]       # 涉及的 card_def/uid（公开部分）
    public: dict              # 公开负载（双方可见事实）
    privileged: dict | None   # 特权负载（仅 privileged trace）
    before_hash: str
    after_hash: str
```
EventType（MVP）：`SETUP / MULLIGAN / PHASE_ENTER / READY / CHANNEL / DRAW /
BURNOUT / POOL_CLEAR / PLAY_STEP(1..6) / PAID / FINALIZE / EXECUTE / PASS / RESOLVE /
TRIGGER_QUEUED / COUNTERED / MOVE / RECALL / CONTEST / SHOWDOWN_START / SHOWDOWN_END /
COMBAT_START / COMBAT_DAMAGE_ASSIGNED / COMBAT_DAMAGE / COMBAT_END / SCORE / WIN /
CLEANUP_START/CLEANUP_ITEM / KILL / DAMAGE / HEAL / BUFF / ATTACH / DETACH /
RETURN / DISCARD / RECYCLE / BANISH / CONCEDE / END_TURN / ERROR`
（阶段 3 可按实现裁剪，trace schema 以字符串承载、向后兼容新增值）。

## 8. Snapshot / TraceFile / Visibility

```python
Snapshot = {
  "snapshot_version": "riftsnap/1",
  "engine_version": str, "ruleset_version": str, "spec_hash": str,
  "state": <规范序列化 dict>,   # 含 rng 各流状态
  "state_hash": str,
}
Visibility = Literal["public", "privileged"]   # 默认 public；privileged 显式参数化（离线）
TraceFile: JSONL 文件路径 + 头校验信息（schema_version / match_id / 完整性标记）
```
- `clone()` 仅供可信内部（搜索/调试），其产物不得直接喂给玩家策略
  （训练文档 §7 信念状态协议）。

## 9. 非法动作与鲁棒性约定

- 任何 `action ∉ legal_actions(state, actor)` → `IllegalActionError`，状态哈希不变；
  runner 捕获→record→（训练默认终止该局为 ERROR；评测模式可配置忽略并重采样）。
- 引擎内部矛盾（不变量校验失败）→ `EngineInvariantError`，附带 step_id 与最小 trace 前缀，
  runner 将 match_id+seed+动作日志导出供回放定位（T-0131 流程）。
- `max_steps` 到限且未终局 → TRUNCATED（防死循环；理论上应不可达，出现即 bug 上报）。

## 10. 版本与兼容

- `ENGINE_VERSION`（semver）；`RULESET_VERSION="core-2026-07-zh+patch-2026-07+errata-2026-07"`
  与 `spec/rule_semantics.yaml:meta.ruleset_version` 一致；`SPEC_HASH` = rules_spec.yaml sha256 前 12 位。
- `TraceFile` 携带 `schema_version="rifttrace/1"`；旧版回放：读取器按 schema 迁移表
  升级或拒绝（不允许静默错读）。
- 卡牌池：阶段 3 `skeleton-v1`；阶段 4 起 `card_db_version` = 卡池内容哈希 +
  来源（`cards_bilingual.db` / KB canonical 规则）标注。
