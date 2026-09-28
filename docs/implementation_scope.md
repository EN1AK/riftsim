# 阶段 0 交付 2：实现范围（Implementation Scope）

> 生成：2026-09-28，阶段 0 输入审计。本文划定 MVP 规则边界、暂不支持的机制与先后依赖，
> 是阶段 1（规则规格 `spec/rules_spec.yaml` 与测试矩阵）的输入。所有规则号均指
> 2026-07 核心规则编号空间（R-CR-\*），版次认定见 `docs/source_inventory.md`。

## 1. 规则集版本锁定（ruleset_version）

固定为以下组合，作为引擎与 trace 的 `ruleset_version` 标识：

- **2026-07 核心规则**（source_009 zh 2026-07-17 为 canonical；source_018 en 2026-07-16 为同版本参照，
  冲突时同版本英文优先——唯一实例 R-CR-811.1.b 已按此裁决）；
- **post-core 官方改动**：source_019 Vendetta Patch Notes（生效 2026-07-24，37 条已应用 + 1 条 incorporated 记录）；
- **卡牌勘误**：截至 source_010（zh，2026-07-24）与 source_020（en，2026-07-23），共 156 条（zh 137 应用 / en 85 记录）；
- **解释层（不改规则文本）**：官方 FAQ source_005/007/011、官方解释 source_012/014/016（过渡性，仅记录），
  裁判 FAQ source_001/006/008（裁判社区层级）；
- **被取代/不采用**：EV-CN-FAQ-0089/0090（superseded）；source_012/014/016 的 90 条 pre-core 改动（已被核心取代）。

## 2. MVP 总边界

- **游戏模式**：仅 1v1 Duel（规则 485）。486/487/488/489（Match、FFA3、FFA4、2v2）暂不实现
  （多人优先权轮转、团队共享战场等语义不同，混入会破坏最小状态机）。
- **玩家人数**：2；隐藏信息按规则 128（Privacy）建模，训练观察严格隔离。
- **卡牌范围（阶段 3 MVP 引擎）**：**不含卡牌文本效果** —— 仅用无文本/近无文本单位、基本符文
  （规则 164）、合法战场与传奇的空效果骨架跑通完整对局；卡牌效果系统在阶段 4 才按覆盖优先级扩展。
  此约定来自 AGENTS.md 最小里程碑原则，避免以卡牌数量替代基础规则正确性。
- **端到端首验收**（阶段 3 尾/阶段 4 初）：一场在基础规则下**合法打完**的 1v1 对局
  （含组卡校验、洗牌 seed、回合/阶段/清理、优先权传递、链与对决、战斗、得分、胜负）→
  产出含 match_id 的 trace → 只读回放器逐步复现公开场面 → 训练观察/动作掩码/日志三方一致。

## 3. 核心规则章节盘点与 MVP 分级

R-CR 共 2382 条聚类（含 FRONT 1）；编号空间不连续（共 421 个整数空号属正常设计）。
分级：**MVP** = 首个可完结对局必需；**P1** = 卡牌效果扩展前必需；**P2** = 随卡牌覆盖按需启用。

| 章节（规则数） | 内容 | 分级 | 说明 |
|---|---|---|---|
| 000 Golden/Silver Rules（19） | 黄金/白银法则、"Can't beats Can"（054–056） | MVP | 效果冲突仲裁总原则，贯穿效果系统 |
| 101–103 组卡（含于 100） | 40 张主牌堆、传奇、领域同一性、符文牌堆、上限 | MVP | 无官方牌表（见 §6 缺失项），需按此构建合法测试卡组 |
| 104/110–118 Setup（含于 100） | 摆放战场、初始手牌、调度(mulligan)、先后手 | MVP | reset() 的规则依据 |
| 105–109 Spaces/Zones/Hand；108 非盘区域（含于 100） | 棋盘/手牌/牌堆/弃牌/放逐/链等区域与隐私 | MVP | GameState 区域模型与隐藏信息隔离依据 |
| 119–139 游戏物体/卡牌属性（含于 100） | 永久物、卡牌面、费用、名称、类别、领域、规则/效果文本、战力加成 | MVP | CardDefinition / 游戏物体模型 |
| 140–159 Units/Gear/Spells（含于 100） | 三类主牌堆卡牌语义 | MVP | Spell 需链结算；Gear 需附着框架 |
| 160–168 Runes/Rune Pools（含于 100） | 符文、基本符文、能量/rune power 资源 | MVP | 费用支付与资源引擎 |
| 169–176 Battlefields/Legends（含于 100） | 战场控制与得分载体、传奇在场唯一性 | MVP | 得分与胜利核心 |
| 177–187 多类型/Tokens（含于 100） | Token 生成与离场消亡 | P1 | 随首批产 token 卡牌启用 |
| 188–192 Control（含于 100） | 控制权、控制权变更 | MVP | 隐藏关键词(811)与战场争夺依赖 |
| 193–196 Winning（含于 100） | 8 分、最终分数差异化、检查时点 | MVP | 终局判定 |
| 197–200 Locations；201–206 Costs（24） | 位置/移动端点；费用、额外费用、替代费用 | MVP | 移动(445)与出牌流程(353)依赖 |
| 301–310 Turn/States of the Turn（含于 300） | 回合结构、回合状态（开放/闭合等） | MVP | 状态机主干 |
| 311–313 Priority and Focus（含于 300） | 优先权、焦点、连续通过 | MVP | legal_actions 生成与链推进核心 |
| 314–317 Phases；318–324 Cleanups（含于 300） | 开始/主阶段/结束阶段；清理、特殊清理、战斗清理 | MVP | 回合推进与死亡/伤害清理 |
| 325–348 Chains and Showdowns（含于 300） | 链、待定项、四步结算（Finalize/Execute/Pass/Resolve）、对决 | MVP | 全游戏最核心结算机制 |
| 349–359 Playing Cards / Process of Play（含于 300） | 出牌六步（含 402–406）、可选/额外费用、Splitting | MVP | step() 的合法性校验与状态迁移模板 |
| 360–406 Abilities（含于 300/400） | 被动、替代效果(367–375)、起动(376–381)、触发(382–385)、反射触发(386–388)、延迟(389–392)、链接技能(393–401) | MVP 框架 + P1 内容 | 框架（注册/触发/入链/结算顺序）MVP 必备；具体技能内容随卡牌 |
| 402–406 Play steps（含于 400） | 选择、总费用、支付、合法性复检、执行 | MVP | 与 349–359 同一流程 |
| 407–458 Game Actions（含于 400） | 41 个原子游戏动作（Draw/Exhaust/Ready/Recycle/Deal/Heal/Play/Move/Hide/Discard/Stun/Reveal/Counter/Buff/Banish/Kill/Add/Channel/Burn Out/Double/Swap/Attach/Detach/Predict/Prevent/Replace/Create/Burn/Empower/Disempower/Skip/Pay、Movement 445–453、Recalls 454–458） | MVP 子集 + P1 全量 | MVP 优先：Draw/Exhaust/Ready/Recycle/Deal/Heal/Play/Move/Discard/Kill/Buff/Attach/Detach/Pay/Movement；其余随效果原语启用 |
| 459–466 Combat；467–472 Scoring（含于 400） | 战斗三步、伤害分配、清理、征服/占领得分 | MVP | 胜负闭环 |
| 473–480 Layers（含于 400） | 持续效果层级、时间戳 | P1 | 首张带持续效果/增益互动作战卡前必须就绪；框架在阶段 2 预留 |
| 481–489 Modes（含于 400） | 游戏模式 | 仅 485 MVP；486–489 暂不支持 | 见 §2 |
| 649–652 Conceding（24） | 认输 | MVP | 作为合法动作 + 终局原因 |
| 700–733 Additional（含于 700） | Buffs(701)、Mighty(706)、Bonus Damage(712)、Attachment(716)、Inactive(720)、Dependent Keywords(726)、XP(728) | 701/706/712/716/720 MVP；726/728 P2 | XP(728) 等仅特定系列卡使用 |
| 739–766（含于 700） | Special Terms、Counters(741)、Making New Choices(750)、Untargetability(756)、Naming(759)、Ignoring(764) | 739/741 P1；750/756/759/764 P2 | 依首批卡牌文本需求启用 |
| 800–829 Keywords（321） | 关键字总章 + 25 条术语（805 Accelerate … 829 Flow） | MVP 子集 + P1 全量 | MVP 子集依所选卡池常用关键字（如 806 Action / 813 Reaction / 816 Temporary / 811 Hidden / 805 Accelerate / 822 Ambush / 815 Tank / 814 Shield 等，阶段 1 按卡池统计确定）；无卡使用的关键字降级 P2 |

## 4. 暂不支持机制（明确排除，防范围蔓延）

1. 多人与团队模式（486–489）及由此衍生的优先权/攻击对象语义。
2. 全卡池 1267 张卡的效果；阶段 3 仅"无文本骨架卡 + 基本符文"，阶段 4 起按依赖顺序扩展，
   每张可执行卡必须绑定规则来源与回归测试。
3. 依赖具体卡牌才出现的机制：额外回合(734–738)、XP(728–733)、Prediction(436)等，归入 P2。
4. 观察卡 4 张（OGN-131/251、UNL-097/177）：按 source_008 sec.4 现行口径实现并显式标注，
   不等待中文官方文本更新。
5. 卡面文本的双语双实现：引擎卡定义以 **zh canonical（含已应用勘误）为单一权威文本源**，
   EN 文本/EN 勘误仅作注释与校验参照，避免双语效果解析分叉。
6. RAG 服务（scripts/rag）与训练/回放 UI 不属于引擎依赖；UI 一律只读 trace。

## 5. 依赖顺序（实现拓扑，阶段 3–4 的路线图基础）

```
区域/隐私模型(105-109,128) → 游戏物体/卡定义(119-139) + 组卡校验(101-103)
  → Setup(104,110-118) → 资源(160-168) + 费用(201-206)
  → 回合状态机(301-310) + 优先权/焦点(311-313) + 阶段/清理(314-324)
  → 链与对决(325-348) + 出牌流程(349-359,402-406) + 动作原子(407-458 子集)
  → 移动(445-453) → 战斗(459-466) → 得分/胜负(193-196,467-472)
  → Buffs/Attachment/Inactive(701-725) → Layers(473-480，首个持续效果前)
  → 关键字(800-829 子集) → 卡牌效果原语（阶段 4）→ 观察卡特例（标注）
```

横切依赖：黄金/白银法则与 Can't-beats-Can（000 章）作用于所有效果冲突；事件/触发框架
（382–401）在链框架定稿后即固定接口，卡牌内容只注册不改动。

## 6. 阶段 1 可直接消费的数据与已知坑

- 规则文本/来源/案例/例外：`workspace/final/rules.db`（rules + rule_sources + rule_cards +
  rule_changes + rule_verification）；追溯`rule_id → evidence_id → 文件/页码`完整存在。
- **结构化五字段全 NULL**：阶段 1 的 `rules_spec.yaml` 语义字段（trigger/legality/transition/timing）
  必须人工+脚本从 canonical 正文规格化，标注 `status: verified|ambiguous`；不能从 DB 直接读取语义。
- 歧义处理通道已就绪：`conflicts` 表 1/1 已关；后续新发现的引擎级歧义写入
  `docs/unresolved_rules.md`（AGENTS.md 约定），不得私自补规则。
- 判例参考库：`manual_review.md` 186 条裁定结论（中英差异 161、勘误链、旧编号映射 735.1.c→809.1.c 等），
  阶段 1 编写规格时可用于规避已知陷阱（VERIF-FLAG 类旧编号引用已有继任映射）。
- 卡组数据缺失（source_inventory §7.1）：需规则化地构造 2 套合法测试卡组
  （确定性 seed、遵守 101–103 上限与领域约束），或用户提供官方预组牌表。

## 7. 阶段 0 验收自检

- 权威材料、版本、效力、生效日期、状态与缺失项 → 已列于 `docs/source_inventory.md` §2–§7。
- 规则库已统一去重（2984 聚类）、带来源锚点（rule_sources 6353 行）、无未解决冲突 → 已确认。
- MVP 基础规则/暂不实现机制/依赖关系 → 本文 §2–§5。
- 首个端到端验收定义 → 本文 §2（自动完整对局 → trace → 回放 → 观察/日志核验）。
- 纯规则引擎设计未被任何缺失项阻塞（卡组构造有规则化兜底方案）。
