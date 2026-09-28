# 训练架构设计（docs/training_architecture.md）

> 阶段 2 交付物。目标：**PPO / 自博弈 / 批量训练**为首要消费者；
> 引擎语义唯一，训练侧只包装不重复规则。关联：接口 `docs/api_contract.md`；
> trace 字段 `docs/visualization_spec.md`。

## 1. 总体拓扑

```
policies(训练器/随机/脚本/冻结历史策略)
   │  act(obs_features, mask) → action_id
   ▼
rl/encoder.py ── rl/env.py（单局） ── rl/vecenv.py（N 局并行同步批量）
   │                                  │
   └────── engine step（唯一规则语义）─┘
                     │ TraceSink（等级可配，异步可开关）
                     ▼
              traces/*.jsonl → viewer / 评估器 / 失败样本挖掘
```

- 自博弈：vecenv 的对局双方由"策略提供器"配对（当前策略 vs 历史快照池），
  双方同政策纯由配置决定；引擎不感知 agent 身份，仅感知座位 0/1。
- 多 agent 建模：1v1 双人零和；`agent_id = f"{match_id}:seat{i}"`；
  每局对调先后的评估协议见 §6。

## 2. 观测编码（ObsEncoder 接口）

```python
class ObsEncoder(Protocol):
    obs_dim: tuple[int, ...]
    def encode(self, obs: Observation) -> ObsTensor: ...
    # ObsTensor = {"global": F[G], "objects": F[N, D], "mask_objects": B[N],
    #              "action_mask": B[A]}
```
- 参考实现（`rl/encoder.py:numpy`）：
  - global：回合号/阶段 one-hot/四态 one-hot/双方分数/符文池聚合/步数归一等。
  - objects：场上+手牌（自身）对象特征 `[F_card]`：def 类别 one-hot、战力(M)、伤害、
    休眠/眩晕/增益/贴附数、控制关系、位置（基地/B1/B2/链）、关键词位。
    隐藏对象只贡献"存在位"（存在位=1、其余特征=0 且 mask 标示隐藏），
    **不注入任何 def 内容**（泄漏防线 §7）。
  - action_mask：与动作空间同维的 0/1（由 legal_actions 生成，
    训练器不得自行从 obs 推断合法性）。
- 编码器可替换（图编码/集合编码）；接口保证替换不触碰引擎。

## 3. 动作编码（多头离散）

候选完备性由 `legal_actions` 列表保证；编码为**定长多头**：
```
(action_kind[12], source_slot[MAX_SRC], param0_slot, param1_slot, choice_slot)
```
- `source_slot`：对"来源槽"（场上物体+自己手牌槽）的索引；
  `param*`：目标槽/位置槽；`choice_slot`：CHOOSE_* 回答索引/伤害分配离散化
  （分配动作密度大：MVP 骨架无大单位，枚举全集；P1 需要时改"逐目标增量分配"子步）。
- 每头独立 mask，由 legal_actions 直接展开映射——训练前冻结槽位布局并记录于
  EpisodeHeader（`action_layout_version`）。布局变更=新 schema 版本。

## 4. 奖励与终止（RewardConfig，全部外置）

```python
@dataclass(frozen=True)
class RewardConfig:
    win: float = 1.0
    loss: float = -1.0
    draw_unused: float = 0.0            # 1v1 无平局（R-CR-194）；保留位
    truncated: float = 0.0              # TRUNCATED 时双方奖励
    score_shaping: float = 0.0          # 可选：经验分差系数（默认关，防塑造过强）
    per_turn: float = 0.0               # 可选：回合存活奖励（默认关）
    illegal_action: float = -1.0        # 非法提交（默认立即终局负奖励；可配为0+重采样）
```
- 引擎内部**不实现任何奖励计算**；EpisodeResult.reward 由 adapter 依 RewardConfig 填。
- 终止语义（engine）：SCORE / EFFECT_WIN / CONCEDE / BURNOUT（R-CR-431.3.c.1）。
  截断（max_steps）归 TRUNCATED 非规则终局。

## 5. Env / VecEnv 与 Policy 协议

```python
class Policy(Protocol):
    policy_id: str
    def act(self, obs: Observation, legal: list[Action], rng: Random) -> Action: ...
    # 训练器适配：act 内部做 encode→forward→argmax/sample→decode；策略权重不进引擎。

class RiftEnv:  # PettingZoo AEC 风格（可选薄包装；不装 pettingzoo 也可用）
    def reset(self, seed:int, config:GameConfig) -> None; 
    def observe(self, agent:str) -> Observation
    def action_mask(self, agent:str) -> list[bool]
    def step(self, action:Action) -> None  # 内部轮转 agent_selection
    def last(self) -> tuple[Observation, float, bool, bool, dict]  # obs, rew, term, trunc, info

class RiftVecEnv:  # 同步批量
    def __init__(self, n_envs:int, policy_provider:Callable[[str,int],Policy], 
                 base_seed:int, config:GameConfig)
    def run_batch(self, n_episodes:int, trace_level:TraceLevel) -> list[EpisodeResult]
```
- 并行策略：M1 单机进程池（`multiprocessing`，env 无共享状态、可 pickle）；
  训练 IO 瓶颈不在引擎语义层时再评估移植（无语义分叉原则见 architecture §8）。
- `policy_provider(match_id, seat) -> Policy` 支持：当前 vs 当前（同体自博弈）、
  当前 vs 历史快照（league 雏形）、双人 exploit 评估。

## 6. 指标与口径（落盘即分析就绪）

| 指标 | 口径 |
|---|---|
| SPS | 引擎 step/s；标注 trace 等级、n_envs、CPU/机器、引擎版本 |
| episode_length | step 数（决策步，非自动步）与回合数双口径 |
| return | 每座位累计奖励；与 RewardConfig 一并记录 |
| win_rate | 必须按**先后手分开**与合并两口径；对手策略版本成对记录 |
| invalid_action_rate | `invalid_action_count / decision_steps`；>0 即采样失败局 dump |
| policy_entropy / KL / value_loss | 训练器侧记录；trace 仅在其愿意时挂 `policy_metrics` 引用 |
| burnout_rate / concede_rate | 终止原因分布（长度异常局挖掘入口） |
| matchup winrate 矩阵 | （策略版本 × 策略版本 × 先后手）频次与置信区间 |

- **采样窗口纪律**：任何汇报胜率须注明（策略版本 A vs B、样本局数、seed 区间、
  trace 等级、引擎版本）。checkpoint 关联：DecisionRecord.policy_version/checkpoint_id
  由训练器写入（缺失即省略字段，禁止虚构）。

## 7. 隐藏信息与信念采样协议

- 训练观测与 mask 永不包含对手私有内容（§2 编码防线；单测断言 uid 交集）。
- 特权信息两条合法用途：
  1. 赛后离线分析（`export_trace(privileged)`，显式授权、独立文件）；
  2. **信念采样搜索**（未来）：内部可信执行者 clone/snapshot 后，
     从"与公开历史一致"的假想隐藏状态展开——特权状态必须被显式标注为
     `belief_sampled=True` 且该路径的 trace 不得进公开集。
- 反事实 rollout 的合法性根：`replay`/`simulate` 均复用同一引擎语义。

## 8. Trace 等级与性能分层（与 SPS 的强验证）

| 等级 | 内容 | 预期用途 | 写入 |
|---|---|---|---|
| off | 仅 EpisodeResult（内存） | 大规模训练 | 无 |
| summary | Header/Footer+决策记录（无逐步快照） | 默认训练采样 | 局末批量 |
| sampled | summary + 每 K 步公共快照（K 可配，默认 20） | 抽检/回放稀疏帧 | 局末批量 |
| debug | 全事件+逐步快照+rng 引用 | 失败局复现/回放精度验证 | 缓冲滚动落盘 |

- 事件在单局内顺序稳定（event_seq 严格递增）；异步写盘时 Footer 携带
  `trace_completeness`（事件计数核对）——丢失即标记，viewer 显示"未知"不编造。
- TraceSink 为注入式协议；引擎热路径**零格式化**（仅在等级需要时构造记录对象）。
- `bench/sps_bench.py`（阶段 6 交付）测 4 等级 × n_envs;结果进 reports。

## 9. 失败样本→可视化闭环

- 训练监控对异常局（非法、超长、burnout、entropy 塌缩时的局）导出
  match_id 清单（含 seed/policy 版本/异常类型）。
- viewer 索引页按（match_id/checkpoint/胜负/长度/异常/规则事件）筛选定位；
  该流程约定为 TM-1 后的标准调试动线。

## 10. PPO 适配成本评估（不绑定框架）

- 已提供：ObsEncoder/动作多头+mask/RewardConfig/VecEnv 协议/EpisodeResult 指标。
- 训练器需自带：采样器（rollout buffer）、PPO 损失、checkpoint 管理、
  （可选）self-play league 加層。适配面=实现 `Policy.act`
  （encode→net→decode）与回调写 DecisionRecord 策略字段。预计两类框架：
  - 自研/轻量 PPO：直接消费 RiftVecEnv；
  - 现成库（未选型）：PettingZoo AEC 兼容层或 SB3 MaskablePPO 的
    env/mask 包装（`rl/env.py` 预留 gym 注册点）。
- 不在本阶段选型；选型输入=TM-1 指标与接口摩擦记录。
