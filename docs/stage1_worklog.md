# 阶段工作日志（防上下文丢失）

> 最后更新：2026-09-28。**阶段 0、1、2、3 已全部完成并验收**（阶段 3 测试 54/54 绿）。按 AGENTS.md，下一步=阶段 4（最小只读对局可视化 + 卡牌数据库与效果系统），等用户指令。

## 阶段 3 交付物（最小核心引擎 M1）

- 代码 `src/riftsim/`（纯标准库）：version/errors/enums/rng/cards/decks/config/objects/state/
  events/snapshot/actions/legality/engine/observation/resources/cleanup_sys/phaser/setup/
  playing/chain_sys/movement/showdown/combat/scoring/trace(schema+sink)/runner/policies/replay
- 测试 `tests/`（54 通过）：smoke/decks/privacy/resources/play/move_showdown/combat/
  scoring_end/snapshot_replay_runner + helpers
- fixture trace：`runs/fixtures/*.jsonl`（4 场，含 score×3/burnout×1；`scripts/gen_fixture_traces.py` 可再生成，
  全部通过 `replay.trace_replay_check`）
- SPS 基线（决策步/秒，单人单进程，未优化）：off=239、debug=163（随机策略 30 局）

### 已实现（MVP 范围）
组卡校验全量、Setup+调度确定性、符文池（清空时点）/召出/抽牌/燃尽（含 431.3.c.1 即时胜利）、
阶段推进（唤醒/开始[据守计分]/召出/抽牌/主阶段/结束[3c/3d/3e]）、四态派生、
清理 323.1..14 全清单+迭代、链+HOT FEPR（确认序/立即结算分支/连续让过/最新结算/346 焦点传递）、
对决（焦点窗/关闭/348 控制确立）、打出六步（骨架卡+待命打出口径）、技能五步（获得资源即刻结算）、
移动（主阶段开环限定、休眠费、拥挤、游走、450 争夺）、召回、战斗三步（攻防/伤害分配枚举[壁垒/后排序、致少、溢出]/结算）、
得分（征服/据守、470、471.1.b 终分限制）、燃尽送分、胜负三路径、认输恒合法、
隐藏信息三级过滤、snapshot/restore/clone/replay、trace 四等级/off 热路径零格式化、
随机/脚本/EndTurn 策略 runner、非法动作拒改状态。

### 未实现（诚实清单，交接阶段 4+）
- 全部卡牌效果文本（骨架池空效果；514 R-CARD deferred）与效果原语系统
- P1：Layers 全量（挂点 ContinuousMod）、替换/延迟效果、触发注册表入链（383 挂点）、绝念入链（last_known 已备）、
  Token/计数标创建、增益来源、多类型；关键词：805/807/808/809/814/816/817（框架与注入位已就绪），810/811/815/826 已实现语义子集
- P2（OUT/随卡）：回响/装配/灵便/百炼/XP/狩猎/等级/强化/唯我/额外回合/另做选择/不可被选取/宣告/无视/燃烧（OPEN-1 占位）
- 多人模式条款（447.2.a/b 等）、效果文本贴附堆（ATTACH 动作底层已实现、贴附卡池未启用）
- 已知简化：pay_auto 自动支付（P1 改 PAYMENT_CHOICE）、FEPR 执行窗顺序近似（先非发起者）、跨区域不重实例化（last_known 近似）

## 阶段 2 交付物（docs/）

| 文件 | 内容要点 |
|---|---|
| `docs/architecture.md` | 技术栈与依赖方向；模块布局（src/riftsim，core 纯标准库、rl/viewer 隔离）；**需求驱动半自动机**（DecisionRequest 决策点）；GameState 字段（仅规则依据）；主循环不变量（任务→清理→FEPR→结算序，320/321 互斥）；RNG 命名子流；快照/哈希/回放策略；实现顺序 M1→M3；测试策略；VM-1/TM-1 验收定义 |
| `docs/api_contract.md` | 10 接口签名与语义；GameConfig/Observation/Action/StepResult/EpisodeResult 字段表；DecisionKind 全集；ActionKind 12 类 MVP 枚举；EventType 清单；非法约定（抛错不改状态）；版本矩阵（engine/ruleset/spec_hash/trace schema/action_layout） |
| `docs/training_architecture.md` | ObsEncoder/ObsTensor；多头离散动作编码+mask；RewardConfig（奖励全外置）；Policy/RiftEnv/RiftVecEnv 协议；指标口径（SPS/双口径胜率/非法率等）；信念采样协议；trace 四等级与 SPS 分层验证；失败样本→viewer 闭环；PPO 适配成本（不绑定框架） |
| `docs/visualization_spec.md` | trace schema rifttrace/1（Header/Decision/Event/Snapshot/Footer 逐字段 JSON）；存储布局与 retention；回放器 3.1 场面/3.2 时间轴/3.3 决策面板/3.4 视角切换/3.5 索引；hash 链与 completeness 复验；VM-1 验收步骤 |

阶段 2 新增裁决点：`docs/unresolved_rules.md` OPEN-5（符文池/分数隐私级，暂定公开待确认——链上项目公开已确认有 108 子条款锚点）。

阶段 2 过程中对 spec 的修订：MECH-PRIVACY 公开项补"结算链项目"（108 锚点）；`scripts/spec/build_rules_spec.py --check` 复核全绿（MVP 1684/P1 414/P2 215/OUT 69/cards 514/meta 88；933 规则关联案例；ambiguous 0）。

## 0. 阶段 1 交付物（全部落盘并通过生成器校验）

| 文件 | 内容 | 校验 |
|---|---|---|
| `spec/rule_semantics.yaml` | 166 条机制级语义条目，covers 区间覆盖全部 R-CR 无重叠 | 解析/引用/覆盖校验通过 |
| `scripts/spec/build_rules_spec.py` | 生成器：语义层+rules_work.db→rules_spec；支持 `--check`；幂等 | 运行通过，0 ERR/0 WARN |
| `spec/rules_spec.yaml` | 2984 条规则规格（rule_id/title/tier/status/mechanism_ref/source/additional_sources/五语义字段/test_ids）；tier：MVP 1684/P1 414/P2 215/OUT 69/cards 514/meta 88；status：verified 2470/deferred 514/ambiguous 0 | 933 条规则已关联测试案例锚点 |
| `spec/rule_dependencies.md` | 状态/阶段/窗口/行动/结算/效果依赖顺序 9 节，含实现顺序锁定 | — |
| `spec/rule_test_matrix.md` | 134 个案例（T-0001..T-0134），normal/illegal/edge；fixture F-DECK-A/B、F-STATE-SETUP/MAIN；含覆盖声明与维护规程 | 生成器 test_ids 回填成功 |
| `docs/rule_conflicts.md` | 效力层级协议（锚点 R-CR-508/509/510）+ 4 项已关闭冲突 + 非冲突差异 + 处理流程 | KB 无开放冲突 |
| `docs/unresolved_rules.md` | OPEN-1..4（燃烧占位/战斗分配粒度/R-MISC-019 桶/待命目标细则）+ CLOSED 记录；均为精度暂缓非规则歧义 | 未污染 verified |

## 1. 当前位置

- 工作流：AGENTS.md 分阶段交付，**仅授权阶段 0–2**，阶段 2 完成后停止等指令。
- 阶段 0：已完成（`docs/source_inventory.md`、`docs/implementation_scope.md`）。
- 阶段 1：进行中。todo 1.1–1.4 已完成（规则精读完毕），**当前任务是 1.5：手写 `spec/rule_semantics.yaml`（机制级语义层）**。

## 2. 已完成的事（阶段 1）

### 2.1 规则精读（1.2–1.4 全部读完）

已从 `workspace/rules_work.db` 逐条精读以下核心规则区段（zh canonical）：
- 000 黄金/白银法则（0–2、50–56）；101–206 组卡/Setup/区域/物体/属性/符文/战场/传奇/控制/胜负/位置/费用
- 301–348 回合/四态/优先权焦点/阶段/清理/链/任务 FEPR/对决
- 349–359 打出六步；360–406 技能全类型（被动/替换/主动/触发/内嵌/延迟/关联）+ 技能打出五步（402–406）
- 407–444 全部 31 个动作原子；445–458 移动/召回；459–466 战斗三步；467–472 得分
- 473–480 Layers（三层：特质/技能/加减计算；依赖与时间戳）；481–489 模式（仅 485 精读）；649–652 认输
- 700–725 增益/强力/额外伤害/贴附/未激活；800–829 关键字全部 25 条术语

### 2.2 关键确认数据（写规格时直接用，勿重新推导）

- 章节边界探针输出：`.tmp/chapter_boundaries.txt`（每个整数主编号的规则数与首条标题，covers 区间据此划分）。
- 组卡（103）：传奇 1 张（决定符文特性）；主牌堆 ≥40 张含 1 张选定英雄（英雄单位、英雄标签与传奇一致）；同名卡 ≤3（含选定英雄位；不同名称的同角色卡各占名额）；同英雄标签专属卡全卡组 ≤3；符文牌堆 12 张须符合符文特性；战场数量按模式、同名战场 ≤1。
- Setup（110–118）：传奇入传奇区(111)→选定英雄入英雄区(112)→战场搁置(113)→两牌堆分别洗牌(114)→随机定回合顺序(115，循环队列)→各抽 4(116)→按回合序调度(117：最多 2 张搁置→补抽同数→搁置卡回收)→起始玩家开回合(118)。
- 符文（163–168）：法力无特性；符能有特性；[C]=牌自身特性，[A]=任意；基本符文技能 `[E]：[反应]—[获得][1]`、回收 `[反应]—[获得][C]`；符文池在**每名玩家主阶段开始**与**回合结束**清空（167）。
- 回合四态（308–310）：普通/法术对决 × 开环/闭环。优先权(312)与焦点(313)各至多一人持有。
- 阶段（315–317）：唤醒→开始阶段（开始时触发+得分步骤据守）→召出 2 符文→抽牌（空牌堆=燃尽 431）→主阶段（清符文池→触发→自决行动）→回合结束（结束触发→特殊清理 3c/3d/3e→FEPR）。
- HOT FEPR（334–340）：先未决任务，再 确认(337，按加入顺序)→执行(338)→让过(339)→结算(340 最新已确认项)；全员连续让过才结算。
- 清理（319–324）：解锁条件 319.1-8；14 项清单 323（1 胜利检查/3b 致命伤害摧毁/6-10 争夺与对决战斗触发）；清理中无 FEPR(320)、结算中无清理(321)、清理事件发生则完成后再清(322)。
- 打出六步（354–359，技能五步 402–406 平行）：入链→做选择(355，目标选取例外 355.10.a-f、分摊 355.14)→定总费(356)→支付(357，可 [反应] 获得资源)→合法性检查(358，失败全撤销)→继续/确认(359；法术结算目标失效 359.3.e)。
- 触发顺序（383）：同玩家自选，跨玩家从回合玩家起按回合序；具名触发五类（打出/指目标/征服/据守/攻守触发，攻守每场战斗仅检一次）。
- 战斗（459–466）：步骤1 战斗法术对决（争夺发起者=进攻方得焦点；触发入链 进攻→非防守方→防守）→步骤2 伤害（总战力、进攻方先分配、先致命再摊分、壁垒/后排约束 465.2.c.6-9、分配后同时造成）→步骤3 结算（战斗清理插 3c 移除伤害/3d 防守在则召回进攻方；确立控制清争夺→征服；移除攻防身份）。
- 得分（467–472）：征服+据守；每战场每回合每玩家限 1 分；终分限制 471.1.b（仅征服时当前分≥胜利分-1，须本回合已在每个战场得分否则改抽 1）；胜利分 485 模式=8；胜利检查在清理 323.1。
- Layers（473–480）：三层顺序 1 特质（含战力赋值、复制）→2 技能（贴附效果文本在此入层）→3 加减计算（增值先、减值后；贴附战力加成在此；非被动带限制的快照）；每效果每次序列限应用一次、循环至无变更(476)；依赖关系 478–479（被依赖先应用）；无依赖按时间戳(480，未激活失时间戳)。
- 关键字 tier 划分方案（结合 implementation_scope §3）：MVP=806 迅捷、813 反应（打出权限核心）；P1=805 急速、807 强攻、808 绝念、809 法盾、810 游走、811 待命、814 坚守、815 壁垒、816 瞬息、817 预知、822 伏击、826 后排；P2=812 鼓舞、818 装配、819 灵便、820 回响、821 百炼、823 狩猎、824 等级、825 唯我、827 强化、828 已强化、829 流转。

### 2.3 语义层设计决策（1.5 的依据，已定稿勿重推）

- 机制级条目 ~165 条，字段：`mechanism_id / title / tier(MVP|P1|P2|OUT) / covers / semantics{prerequisites,legality,transition,timing,exceptions,dependencies} / test_hints`。
- `covers` 语法：主编号整数区间 `"R-CR-160..R-CR-168"`（含全部子条款 164.2.a 之类）或显式 `"R-CR-128"`；FRONT 单独。生成器据此把语义继承给每条规则。
- 覆盖目标：全部 R-CR 2382 条 + FRONT 都被某机制 covers；R-TOPIC 81 条生成器默认 tier=meta、status=verified（主题聚合无执行语义）；R-CARD 514 条默认 tier=cards、status=deferred（阶段 4 逐卡实现，FAQ 挂载型语义随卡）。
- 生成器 source 策略：rules ↔ rule_evidence ↔ evidence ↔ sources 四表已确认（本目录 `.tmp/schema_probe.py` 输出）；每条规则主来源取 relationship='same' 优先级最高（核心规则=source_009 zh core_rules），errata/faq 类 evidence 进 `additional_sources`；authority 映射 rule→core_rules、errata→errata、faq→faq。
- title 策略：章节标题规则直接用 canonical；普通规则取 canonical 首句截断（生成器处理，≤60 字）。
- 工具已备好：`.tmp/dump_rules.py <lo> <hi> [--en]`（按区间导出）、`.tmp/dump_pick.py <id>...`（按 ID 导出）、`.tmp/chapter_boundaries.py`、`.tmp/schema_probe.py`。
- pyyaml 6.0.3 已确认可用；Python 3.12.10、pytest 9.1.1。

## 3. 待办（阶段 1 剩余交付物）

| todo | 交付物 | 状态 |
|---|---|---|
| 1.5 | `spec/rule_semantics.yaml`（~165 条机制，按 §2.3 设计） | **进行中** |
| 1.6 | `scripts/spec/build_rules_spec.py` → 生成 `spec/rules_spec.yaml`（含校验：rule_id 存在、covers 全覆盖无重叠、MVP 行为规则有 test_id 或显式 n/a） | 未开始 |
| 1.7 | `spec/rule_dependencies.md`（状态/阶段/窗口/行动/结算/效果依赖顺序，可从 implementation_scope §5 拓扑扩写） | 未开始 |
| 1.8 | `spec/rule_test_matrix.md`（T-xxxx：每 MVP 规则一正常+一边界/非法案例，含可复现初始状态/动作/预期） | 未开始 |
| 1.9 | `docs/rule_conflicts.md`、`docs/unresolved_rules.md`（KB 内 1 冲突已裁决 CON-4B-T2-0001；R-CR-811.1.b 英文优先裁决，均须记录） | 未开始 |
| 1.10 | 跑生成器+校验，按 AGENTS.md §3 格式汇报阶段 1，**停止等待指令** | 未开始 |

### YAML 条目模板（生成器与手写共用约定）

```yaml
- mechanism_id: MECH-RUNE-POOLS
  title: 符文池
  tier: MVP
  covers: ["R-CR-165..R-CR-168"]
  semantics:
    prerequisites: "玩家拥有符文池；资源只能由含「获得法力/符能」表述的效果加入。"
    legality: "支付费用时从符文池扣除；符文池资源不构成手牌等实体区域。"
    transition: "获得动作将法力/符能加入池；支付动作扣除；清空事件移除全部资源。"
    timing: "每名玩家的主阶段开始时、每个回合结束时，所有玩家的符文池清空（167）。"
    exceptions: []
    dependencies: ["MECH-RUNES", "MECH-ACT-ADD", "MECH-ACT-PAY"]
  test_hints: ["清空时点跨回合玩家边界", "支付与获得同回合多次叠加"]
```

## 4. 已知坑（复读防踩）

- DB 结构化五字段（trigger/effect 等）**全 NULL**，语义只能手写，勿试图从 DB 读。
- 终端大输出会截顶：先重定向到 `.tmp/*.txt` 再 Read。
- PowerShell：单引号字面串；复杂命令写 `.tmp/*.py` 再运行，禁内联引号。
- FTS 中文分词不可靠、rule_keywords 启发式有噪音——规格不准从这两处取语义。
