# 规则测试矩阵（spec/rule_test_matrix.md）

> 阶段 1 交付物。每条 MVP 行为规则至少 1 正常 + 1 边界/非法案例，直接指导阶段 3 的 TDD。
> 案例格式对生成器可见：`### T-xxxx` 开头，`- rules:` 列出关联规则（逗号分隔），
> 生成器据此把 test_ids 回填进 spec/rules_spec.yaml。
> type 取值：`normal`=合法场景；`illegal`=非法场景（须被拒且不产生部分状态）；`edge`=边界。

## 0. 通用构造（fixture）与豁免

- **F-DECK-A/B**：合法 1v1 卡组（MECH-DECK-CONSTRUCTION）——传奇 L-A（特性 [R]、英雄标签"测试英雄"）；
  选定英雄 H-A（英雄单位、标签"测试英雄"）；主牌堆 40 张 = H-A + 39 张无文本骨架卡
  （单位 U2=2[R]/2[M]、U3=3[R]/3[M]、装备 G1=1[R]、法术 S1=1[R]，同名≤3）；
  符文牌堆 12 张基本符文 [R]；战场 3 个不同名。F-DECK-B 同构（英雄标签"测试英雄乙"）。
- **F-STATE-SETUP**：`reset(seed)` 完成 Setup（含调度 0 张）后状态：P1 回合玩家、回合 1、
  双方手牌 4、符文池空、场上仅有各自传奇/英雄、战场 B（每方随机选定 1 个，seed 固定）。
- **F-STATE-MAIN**：从 F-STATE-SETUP 推进至 P1 主阶段行动窗口、链空、普通开环。
- **豁免（无行为语义，不给案例）**：MECH-GAME-CONCEPTS、MECH-SETUP-OVERVIEW、MECH-CARDS、
  MECH-FLAVOR-ILLUSTRATION、MECH-PLAYING-GAME、MECH-PHASES、MECH-ABILITIES-OVERVIEW（总述）、
  MECH-MODES-OVERVIEW、MECH-ADDITIONAL-HEADER、MECH-FRONT-MATTER 及全部 meta 类规则——
  其正确性由章节归属规则的案例间接覆盖；生成器以 test_hints/结构性 n/a 处理。

## 1. 组卡与 Setup（T-0001..T-0014）

### T-0001 合法卡组通过校验
- type: normal
- rules: R-CR-103.1, R-CR-103.2, R-CR-103.2.b, R-CR-103.3.a, R-CR-103.4.c
- mechanism: MECH-DECK-CONSTRUCTION
- setup: 构造 F-DECK-A（传奇 1、主牌堆 40 含选定英雄、同名≤3、符文 12、战场 3 不同名、全特性 [R] 匹配）。
- actions: deck_validate(F-DECK-A)
- expect: 校验通过；选定英雄计入同名名额（H-A 计为 1/3）。

### T-0002 同名 4 张非法
- type: illegal
- rules: R-CR-103.2.b, R-CR-103.2.b.1
- mechanism: MECH-DECK-CONSTRUCTION
- setup: F-DECK-A 变体：H-A(选定英雄) + 3 张同名 U2 改为 4 张同名 U2。
- actions: deck_validate
- expect: 拒绝，违规项=同名卡 >3。

### T-0003 特性不匹配非法
- type: illegal
- rules: R-CR-103.1.b.3, R-CR-103.1.b.4, R-CR-103.3.a.1
- mechanism: MECH-DECK-CONSTRUCTION
- setup: F-DECK-A 变体：(1) 主牌堆混入 1 张纯 [G] 卡；(2) 混入 1 张 [R][G] 双特性卡；(3) 符文堆混入 1 张 [G] 符文。
- actions: deck_validate × 3
- expect: 三者均拒绝（单特性须同、多特性须全部同、符文同受约束）。

### T-0004 专属卡 4 张非法、选定英雄标签不符非法
- type: illegal
- rules: R-CR-103.2.d, R-CR-103.2.d.1, R-CR-103.2.a.2
- mechanism: MECH-DECK-CONSTRUCTION
- setup: (1) 4 张同英雄标签专属卡；(2) 选定英雄的英雄标签与传奇不一致。
- actions: deck_validate × 2
- expect: 均拒绝；专属卡合计上限 3；英雄标签必须匹配传奇。

### T-0005 符文堆数量错误非法
- type: illegal
- rules: R-CR-103.3.a
- mechanism: MECH-DECK-CONSTRUCTION
- setup: F-DECK-A 变体：符文牌堆 11 张。
- actions: deck_validate
- expect: 拒绝，违规项=符文牌堆须为 12。

### T-0006 同名战场 2 个非法
- type: illegal
- rules: R-CR-103.4.c
- mechanism: MECH-DECK-CONSTRUCTION
- setup: F-DECK-A 变体：战场含 2 个同名战场。
- actions: deck_validate
- expect: 拒绝。

### T-0007 Setup 全流程与初始落位
- type: normal
- rules: R-CR-110, R-CR-111, R-CR-112, R-CR-113, R-CR-114, R-CR-116, R-CR-118
- mechanism: MECH-SETUP-PROCESS
- setup: 两套 F-DECK-A/B，seed=42。
- actions: reset(seed=42)
- expect: 传奇/选定英雄各入其区；牌堆 36/40-4；手牌各 4；回合队列定且 P1 开回合；两次 reset(42) 产生完全同构状态（确定性）。

### T-0008 战场随机选定（1v1）
- type: normal
- rules: R-CR-485, R-CR-485.1
- mechanism: MECH-MODE-DUEL
- setup: F-DECK-A/B 各备 3 战场。
- actions: reset(seed=42) 与 reset(seed=43)
- expect: 每次 Setup 每方从其 3 战场中确定 1 个上场（共 2 个战场）；选择随 seed 变且可复现；胜利分=8。

### T-0009 后手补偿
- type: normal
- rules: R-CR-485, R-CR-315.4, R-CR-430.1
- mechanism: MECH-START-OF-TURN
- setup: F-STATE-SETUP，推进至后手玩家 P2 的首回合召出阶段。
- actions: 执行召出
- expect: P2 首个召出阶段召出 3 张符文（2+1 补偿）；P2 其后回合召出 2 张。

### T-0010 调度 0/1/2 张
- type: normal
- rules: R-CR-117, R-CR-117.1, R-CR-117.2, R-CR-117.3, R-CR-416.1
- mechanism: MECH-SETUP-PROCESS
- setup: Setup 至调度窗口（P1 手牌 4：c1..c4）。
- actions: P1 调度搁置 {c1}；P2 调度搁置 {}（0 张）
- expect: P1 补抽 1 后手牌 4，c1 回收至 P1 主牌堆底；P2 不变；超 2 张的搁置请求非法。

### T-0011 洗牌与牌堆私密性
- type: edge
- rules: R-CR-114, R-CR-128.1, R-CR-129.1
- mechanism: MECH-PRIVACY
- setup: reset(seed=42) 完成。
- actions: observe(P1) 与 observe(P2)
- expect: 双方仅知对手牌堆数量，内容不可见；己方手牌仅己方可见；牌库顶对双方不可见。

### T-0012 回合顺序循环
- type: normal
- rules: R-CR-115.1, R-CR-115.1.c, R-CR-306
- mechanism: MECH-TURN
- setup: F-STATE-SETUP。
- actions: 双方各完成 1 回合（快进：从主阶段连续选择"结束"×2 轮）
- expect: 回合玩家序列 P1→P2→P1→P2；回合序号递增。

### T-0013 同 seed 完全复现
- type: edge
- rules: R-CR-115, R-CR-116, R-CR-114
- mechanism: MECH-SETUP-PROCESS
- setup: 两次 reset(seed=42)+固定动作脚本（调度 0 张→主阶段结束）。
- actions: 分别执行并记录状态哈希链
- expect: 两次运行的逐步状态哈希完全一致。

### T-0014 胜利分与终局初始判定
- type: normal
- rules: R-CR-194.1, R-CR-472, R-CR-485
- mechanism: MECH-WINNING
- setup: F-STATE-SETUP，P1 分=7、P2 分=8（注入）。
- actions: 触发清理（任意合法行动完成）
- expect: 清理 323.1 判定 P2 获胜（8≥8 且 8>7）；对局终止；result.winner=P2，termination=score。

## 2. 区域、物体与隐私（T-0015..T-0022）

### T-0015 区域成员排他
- type: edge
- rules: R-CR-105, R-CR-106, R-CR-107, R-CR-108
- mechanism: MECH-SPACES
- setup: F-STATE-MAIN。
- actions: 枚举全部游戏物体
- expect: 每个物体恰属一个区域；区域成员并集=全部物体。

### T-0016 跨区域迁移新物体
- type: normal
- rules: R-CR-124.1
- mechanism: MECH-GAME-OBJECTS
- setup: P1 单位甲在手牌（注入持续效果标记：本回合内[M]+1 于手牌甲——若规则禁止则改以场上单位受回合内效果后被召回场景）。
- actions: 单位甲 打出进场后被召回，再被移回手牌
- expect: 每次跨场↔非场迁移后，原先附着于其上的（非自有的）持续效果不再适用；物体实例 id 更新。

### T-0017 所属权恒定
- type: edge
- rules: R-CR-127.1, R-CR-192.1
- mechanism: MECH-OWNERSHIP
- setup: P1 单位甲控制权被效果转给 P2（注入该效果）。
- actions: 单位甲随后被摧毁
- expect: 甲进入 P1（所属者）废牌堆；所属权全程为 P1。

### T-0018 公开/私密/隐秘三级
- type: normal
- rules: R-CR-128, R-CR-109.1
- mechanism: MECH-PRIVACY
- setup: F-STATE-MAIN，P1 打出单位 U2 至基地。
- actions: observe(P2)
- expect: U2 战力/休眠态公开；P1 手牌内容不可见（数量可见）；双方牌堆内容不可见。

### T-0019 待命区隐私
- type: edge
- rules: R-CR-108, R-CR-811.6.a, R-CR-811.1.b
- mechanism: MECH-NONBOARD-ZONES
- setup: P1 控制战场 B1，将带[待命]的手牌（注入关键词）付[A]待命至 B1。
- actions: observe(P2) / observe(P1)
- expect: P2 仅见 B1 存在一张待命牌（卡背），内容与其[反应]属性不可见；P1 可见内容。

### T-0020 打出时费用判定以印刷为准
- type: edge
- rules: R-CR-206.1, R-CR-131.1
- mechanism: MECH-COSTS
- setup: 手牌 S1 费用被效果临时改为 [0]（注入）。
- actions: 另一效果要求判定 S1 的费用
- expect: 判定结果为印刷费用 1[R]（不受临时改变影响）。

### T-0021 类别与类型行为约束
- type: normal
- rules: R-CR-133, R-CR-141, R-CR-148, R-CR-154
- mechanism: MECH-CATEGORY
- setup: F-STATE-MAIN，P1 手牌含 U2/G1/S1。
- actions: legal_actions(P1) 过滤"打出目标位置"
- expect: U2 可选基地/控制战场；G1 仅基地；S1 不入基地/战场（结算后去废牌堆）。

### T-0022 效果文本与规则文本区分
- type: normal
- rules: R-CR-135, R-CR-136, R-CR-724.1
- mechanism: MECH-EFFECT-TEXT
- setup: P1 场上有带效果文本的装备 G2（注入文本），未贴附任何单位。
- actions: 查询 G2 文本激活状态；随后合法贴附至 U2
- expect: 未贴附时效果文本未激活（不生效）；贴附后激活并入 U2 文本集合。

## 3. 三类卡与符文资源（T-0023..T-0034）

### T-0023 单位打出休眠进场
- type: normal
- rules: R-CR-142, R-CR-143, R-CR-144, R-CR-359.2
- mechanism: MECH-UNITS
- setup: F-STATE-MAIN，符文池 [2]+[R][R]。
- actions: 打出 U2 至基地
- expect: U2 以休眠状态入场于其基地；符文池扣 2 法力与 2[R]；[急速]未支付不生效。

### T-0024 单位主动技能时机限制
- type: illegal
- rules: R-CR-145.2, R-CR-381.1
- mechanism: MECH-UNITS
- setup: P1 场上单位带主动技能（注入），当前为 P2 回合/或 P1 回合闭环。
- actions: 尝试激活该技能
- expect: 拒绝：主动技能仅控制者回合主阶段开环（缺[迅捷]/[反应]）。

### T-0025 装备进基地且活跃
- type: normal
- rules: R-CR-148, R-CR-149, R-CR-359.3
- mechanism: MECH-GEAR
- setup: F-STATE-MAIN，符文池 [1]+[R]。
- actions: 打出 G1
- expect: G1 活跃状态入 P1 基地；不可选择战场作为落点（无[灵便]类权限）。

### T-0026 法术时机与去向
- type: normal
- rules: R-CR-155, R-CR-157, R-CR-158
- mechanism: MECH-SPELLS
- setup: F-STATE-MAIN，手牌 S1（无文本，仅印刷费用 1[R]）。
- actions: 打出 S1→全员让过→结算
- expect: S1 结算后入 P1 废牌堆；S1 未进入任何场上区域；闭环期间无 S1 权限（非法列表无 S1 打出）。

### T-0027 法术默认时机非法
- type: illegal
- rules: R-CR-155.1, R-CR-308, R-CR-309
- mechanism: MECH-SPELLS
- setup: 任一玩家回合闭环（链上存在项目）。
- actions: legal_actions 检查无[迅捷][反应]法术 S2
- expect: S2 不在合法打出列表。

### T-0028 符文召出与休眠获得
- type: normal
- rules: R-CR-164.2, R-CR-163, R-CR-430.1
- mechanism: MECH-RUNES
- setup: P1 其回合召出阶段，符文堆非空。
- actions: 召出 2 符文；随后对其中 1 张执行 [E]：[反应]—[获得][1]
- expect: 符文默认活跃入场；[E] 支付后符文池 +1 法力；该符文转休眠。

### T-0029 符文回收获得 [C]
- type: normal
- rules: R-CR-164.2, R-CR-416.1.b
- mechanism: MECH-RUNES
- setup: P1 场上 [R] 基本符文 1 张。
- actions: 执行"回收此牌：[反应]—[获得][C]"
- expect: 符文回 P1 符文堆底；符文池 +1[R]（=[C] 即自身特性）。

### T-0030 符文技能跨回合闭环可激活
- type: normal
- rules: R-CR-164.2, R-CR-813.1.b, R-CR-813.1.c.2
- mechanism: MECH-KW-REACTION
- setup: P2 回合且链上存在项目（闭环），P1 有活跃 [R] 符文。
- actions: P1 激活符文 [E]：[获得][1]
- expect: 允许（[反应]权限）；获得资源技能确认后立即结算（429.2/337.2：链上不留待反应窗口）。

### T-0031 符文池清空时点（主阶段）
- type: normal
- rules: R-CR-167, R-CR-316.3
- mechanism: MECH-RUNE-POOLS
- setup: P1 回合开始阶段完成时其符文池含 [1]+1[R]（注入），P2 池含 1[R]。
- actions: 进入 P1 主阶段
- expect: 主阶段开始时双方池清空（P1 与 P2 皆空）。

### T-0032 符文池清空时点（回合结束）
- type: normal
- rules: R-CR-167.1, R-CR-317.2.d
- mechanism: MECH-RUNE-POOLS
- setup: P1 回合结束阶段开始，双方池各有残余。
- actions: 推进至回合移交
- expect: 回合结束时所有玩家池清空。

### T-0033 非法扣费拒绝
- type: illegal
- rules: R-CR-357.1, R-CR-168, R-CR-134
- mechanism: MECH-PLAY-STEP4-PAY
- setup: P1 池=[1]+1[R]，尝试打出费用 [1]+[G] 的卡（注入）。
- actions: 打出该卡并进入支付
- expect: 非法：符能特性不匹配（[R] 不可付 [G]）；无部分扣费状态残留。

### T-0034 支付中可获得资源
- type: normal
- rules: R-CR-357.1.a, R-CR-429.2, R-CR-164.2, R-CR-444
- mechanism: MECH-PLAY-STEP4-PAY
- setup: P1 池=0，场上活跃符文 2 张，打出费用 [1]+[R] 的 U2。
- actions: 支付窗口内激活符文回收技能获得 [R]、再 [E] 另一符文获得 [1]
- expect: 支付成功；获得技能不占用新链；总过程无中间非法态。

## A 块完（T-0001..T-0034）

## 4. 回合状态机与阶段（T-0035..T-0044）

### T-0035 四态派生：链非空→闭环
- type: normal
- rules: R-CR-308, R-CR-309, R-CR-310, R-CR-331
- mechanism: MECH-TURN-STATES
- setup: F-STATE-MAIN。
- actions: P1 打出 U2（入链）→ 查询四态 → U2 确认 → 查询四态
- expect: 入链后=普通闭环；确认落位且链空后=普通开环。

### T-0036 对决状态派生
- type: normal
- rules: R-CR-310.1, R-CR-343, R-CR-344
- mechanism: MECH-TURN-STATES
- setup: P1 单位于战场 B1，P2 单位移动进入 B1（触发争夺）。
- actions: 清理完成后查询回合状态
- expect: 状态=法术对决开环（对决开始）；对决关闭且无人争夺时回普通开环。

### T-0037 优先权唯一与行动归属
- type: normal
- rules: R-CR-312, R-CR-312.1, R-CR-409
- mechanism: MECH-PRIORITY
- setup: F-STATE-MAIN（P1 回合普通开环）。
- actions: legal_actions(P2)
- expect: P2 无自决行动（仅可能有反应窗口类动作）；仅 P1 有自决行动。

### T-0038 唤醒步骤
- type: normal
- rules: R-CR-315.1.b, R-CR-415.1
- mechanism: MECH-START-OF-TURN
- setup: P1 回合开始，其场上 2 单位休眠、1 符文休眠。
- actions: 执行唤醒子步骤
- expect: 全部"能活跃的"物体转活跃；无法活跃的维持休眠。

### T-0039 据守得分
- type: normal
- rules: R-CR-315.2, R-CR-469.2, R-CR-470
- mechanism: MECH-START-OF-TURN
- setup: P2 控制战场 B1（上回合确立），P1 回合开始阶段（P2 非回合玩家）。
- actions: 推进至 P2 其回合开始阶段计分步骤
- expect: P2 对 B1 据守得 1 分（若本回合未从 B1 得过分）。

### T-0040 空堆抽牌→燃尽
- type: edge
- rules: R-CR-315.4, R-CR-431, R-CR-431.1
- mechanism: MECH-ACT-BURNOUT
- setup: P1 主牌堆=0、废牌堆={c1..c3}，进入抽牌子步骤。
- actions: 抽牌
- expect: 废牌堆洗入牌堆（seed 序）→P1 选一名对手（P2）获得 1 分→完成抽牌；不终止动作流。

### T-0041 燃尽循环与立即胜利
- type: edge
- rules: R-CR-431.3, R-CR-431.3.c.1
- mechanism: MECH-ACT-BURNOUT
- setup: P1 主牌堆=0、废牌堆=0（第二次燃尽条件）；P2 分=8。
- actions: 触发需抽牌事件
- expect: 按 431.3.c.1 条件直接判定立即胜利（P2）；termination=burnout。

### T-0042 主阶段进入触发与清池
- type: edge
- rules: R-CR-316.1, R-CR-316.2, R-CR-316.3
- mechanism: MECH-MAIN-PHASE
- setup: 存在"主阶段开始时"触发技能（注入于传奇），P2 池含残余 [R]。
- actions: P1 回合推进至主阶段
- expect: 顺序：清双方池→触发入链→FEPR 处理→行动窗口开放。

### T-0043 回合结束清扫
- type: normal
- rules: R-CR-317.2, R-CR-324.1
- mechanism: MECH-ENDING-PHASE
- setup: P1 回合结束阶段开始；P1 单位甲带 2 伤害、被眩晕（注入）、本回合获得[M]+1。
- actions: 执行结束阶段
- expect: 3c 移除甲全部伤害；3d 眩晕与回合内[M]+1 失效；3e 双方池清空。

### T-0044 结束阶段触发延长 FEPR
- type: edge
- rules: R-CR-317.2, R-CR-335, R-CR-336
- mechanism: MECH-ENDING-PHASE
- setup: "回合结束时"触发技能（注入），其结算产生新任务（对敌方造成 1 伤害致单位死亡）。
- actions: 推进结束阶段
- expect: 结束触发→FEPR→死亡→再清理→安静后才移交下一位玩家。

## 5. 清理 与链/FEPR（T-0045..T-0060）

### T-0045 清理抑制 FEPR
- type: illegal
- rules: R-CR-320, R-CR-334
- mechanism: MECH-CLEANUPS
- setup: 清理进行中（如致命伤害批量处理）。
- actions: 玩家尝试打出任何卡牌
- expect: 拒绝（无行动窗口）；清理完成后窗口恢复。

### T-0046 结算抑制清理→未决
- type: edge
- rules: R-CR-321, R-CR-321.1
- mechanism: MECH-CLEANUPS
- setup: 法术结算中造成单位致命伤害。
- actions: 结算完成
- expect: 结算期间不发生清理；结算完成的检查点执行清理并摧毁该单位。

### T-0047 致命伤害清理摧毁
- type: normal
- rules: R-CR-323.5, R-CR-323.4, R-CR-428.1, R-CR-143
- mechanism: MECH-ACT-KILL
- setup: 单位甲 战力 3、累积伤害 3；甲带绝念触发（注入）。
- actions: 触发清理
- expect: 3a 记录绝念待处理；3b 甲入其所属者废牌堆；绝念随后经 FEPR 结算。

### T-0048 清理迭代
- type: edge
- rules: R-CR-322, R-CR-318
- mechanism: MECH-CLEANUPS
- setup: 清理 3b 摧毁甲→另单位乙的被动失效→乙战力降以致其伤害致命。
- actions: 执行清理
- expect: 本次清理完成后立即再清一次；乙随后被摧毁；直至无新满足条件。

### T-0049 胜利检查在清理第 1 项
- type: edge
- rules: R-CR-323.1, R-CR-472
- mechanism: MECH-WINNING
- setup: 清理同时存在：P1 达胜利分（8，领先）与某单位待摧毁。
- actions: 执行清理
- expect: 先做胜利检查并终局（P1 胜）；后续清理项不再执行。

### T-0050 待处理→确认的入序
- type: normal
- rules: R-CR-329, R-CR-337.1.b
- mechanism: MECH-FEPR-FINALIZE
- setup: 链上有待处理项 A（先入）与 B（后入，非立即结算类）。
- actions: FEPR 推进
- expect: 确认顺序 A→B（加入序）。

### T-0051 单位确认即入场（立即结算分支）
- type: normal
- rules: R-CR-337.2, R-CR-359.2, R-CR-400.2
- mechanism: MECH-PLAY-STEP6-PROCEED
- setup: P1 打出 U2 经步骤 5 通过。
- actions: FEPR-确认
- expect: U2 确认后立即入场（休眠于指定位置），不留链上待反应；可激活其进场触发入新链。

### T-0052 执行窗口可加反应
- type: normal
- rules: R-CR-338.1, R-CR-813.1.c.1
- mechanism: MECH-FEPR-EXECUTE
- setup: P1 打出法术 S1 确认；P2 手牌 [反应] 法术 R1（注入）。
- actions: 执行窗口 P2 打出 R1 连锁
- expect: R1 入链为待处理；FEPR 回到确认步；R1 比 S1 先结算。

### T-0053 全员让过→结算最新项
- type: normal
- rules: R-CR-339.1, R-CR-340.1
- mechanism: MECH-FEPR-RESOLVE
- setup: 链上 A（旧）确认、B（新）确认。
- actions: 全员连续让过
- expect: 仅结算 B；结算后链上剩 A，重新进入 FEPR 评估。

### T-0054 连锁后进先出
- type: normal
- rules: R-CR-340, R-CR-336
- mechanism: MECH-FEPR-RESOLVE
- setup: S1→R1 连锁（T-0052 延续）。
- actions: 双双让过
- expect: R1 先结算→清理检查点→S1 再结算。

### T-0055 非回合玩家让过后可再行动
- type: edge
- rules: R-CR-339, R-CR-348.1
- mechanism: MECH-FEPR-PASS
- setup: 对决中焦点轮转：P2 让过焦点后 P1 打出法术。
- actions: 焦点再次轮至 P2
- expect: P2 可重新选择行动（此前让过不构成连续全员让过）。

### T-0056 清理生成对决/战斗标记
- type: normal
- rules: R-CR-323.6, R-CR-323.9, R-CR-323.10, R-CR-344.1
- mechanism: MECH-CLEANUPS
- setup: 移动完成后战场 B1 有双方单位（战斗待定）、B2 仅 P2 进入非控（争夺）。
- actions: 清理完成至行动窗口
- expect: 回合玩家按 323.9/10 选择开启顺序；多选一场→逐个结算。

### T-0057 任务优先于行动
- type: illegal
- rules: R-CR-333, R-CR-334, R-CR-335
- mechanism: MECH-TASKS-FEPR
- setup: 存在未决任务（待清理）。
- actions: legal_actions(P1)
- expect: 仅与任务相关的选项，无常规自决行动。

### T-0058 触发入链顺序（跨玩家）
- type: normal
- rules: R-CR-383.3.d.1
- mechanism: MECH-TRIGGERED
- setup: P1 回合；同一事件同时满足 P2 技能甲与 P1 技能乙两个触发。
- actions: 事件发生后入链
- expect: 顺序：回合玩家 P1 的乙先（其自选内部序），随后 P2 的甲。

### T-0059 对决焦点传递
- type: normal
- rules: R-CR-345.1, R-CR-346.1, R-CR-346.1.a
- mechanism: MECH-FOCUS
- setup: 移动进非控战场→非战斗对决（P1 为争夺发起者）。
- actions: 对决开始；链上项目结算完
- expect: 开始焦点=P1；该项目由触发产生→焦点不传递（346.1）；玩家主动打出产生的项目结算完→焦点按回合序传递。

### T-0060 非战斗对决确立控制
- type: normal
- rules: R-CR-348.2, R-CR-190.1.c, R-CR-467.1
- mechanism: MECH-SHOWDOWNS
- setup: 上述对决中 P1 单位留场、P2 单位离场（被效果移走），全员让过关闭对决。
- actions: 对决关闭结算
- expect: P1 为唯一留场方→确立控制；若本回合未从该战场得过分→征服得 1 分。

## 6. 打出六步与选择/费用（T-0061..T-0076）

### T-0061 六步完整轨迹
- type: normal
- rules: R-CR-349, R-CR-350, R-CR-351, R-CR-352, R-CR-353, R-CR-354, R-CR-355, R-CR-356, R-CR-357, R-CR-358, R-CR-359
- mechanism: MECH-PLAYING-CARDS-OVERVIEW
- setup: F-STATE-MAIN，打出 U2。
- actions: step() 执行并记录事件轨迹
- expect: 事件序列含入链→选择→定费→支付→复核→确认入场；每步产生对应事件记录（trace 锚点）。

### T-0062 目标数量精确
- type: illegal
- rules: R-CR-355.6
- mechanism: MECH-PLAY-STEP2-CHOICES
- setup: 法术 T2 文本"对 2 名单位各造成 1 伤害"（注入）。
- actions: 仅选 1 目标并继续
- expect: 拒绝：目标数量不精确；不进入定费。

### T-0063 目标合法性动态化
- type: edge
- rules: R-CR-358.1, R-CR-359.3.e
- mechanism: MECH-PLAY-STEP5-LEGALITY
- setup: S1 指定敌方单位甲；连锁反应将甲移回手牌。
- actions: 继续至 S1 结算
- expect: 结算时目标跨区域往返→该指示非法跳过（尽可能执行其余指示）；若 S1 全部指示关联失效目标则按其条款处理。

### T-0064 分摊须足额
- type: illegal
- rules: R-CR-355.14
- mechanism: MECH-PLAY-STEP2-CHOICES
- setup: 法术"将 4 点伤害分摊给任意单位"（注入）。
- actions: 仅分配 3 点提交
- expect: 拒绝：分摊必须足额且不超单目标致少限制（若有）。

### T-0065 额外费用选择（可选）
- type: normal
- rules: R-CR-356.2.b, R-CR-820.1.c.1
- mechanism: MECH-PLAY-STEP3-COST
- setup: 法术带可选额外费用（注入[回响][1]）。
- actions: 定费时选择支付/不支付回响
- expect: 两种选择均可行且仅一次（820.1.c.3）；总费相应变更；不付则无额外执行。

### T-0066 减费下限独立与总费下限 0
- type: edge
- rules: R-CR-356.4, R-CR-356.6
- mechanism: MECH-PLAY-STEP3-COST
- setup: 卡费 [5]，减费效果 A（本卡-3，下限[2]）、效果 B（-4，下限[1]）（注入）。
- actions: 定费
- expect: 各项按其下限独立计算后合成；若超出则总费=max(0,合计)（≥0）。

### T-0067 替代费用（流转）
- type: edge
- rules: R-CR-356.1, R-CR-829.1.c.1
- mechanism: MECH-KW-FLOW
- setup: 废牌堆中法术带[流转][2][R]（注入）。
- actions: 从废牌堆支付流转费打出
- expect: 替代费用取代基础费用；打出时机与其他权限不变（829.1.b.2）；确认后若离链非自身指示则放逐。

### T-0068 法盾增费
- type: normal
- rules: R-CR-809.1.c, R-CR-809.1.c.1
- mechanism: MECH-KW-DEFLECT
- setup: P1 单位带[法盾1]；P2 打出一指定该单位的法术。
- actions: 定费/支付
- expect: 该法术强制额外费用+1（任意特性符能可付）；多选目标多次指定则多次加收。

### T-0069 支付撤销与返还
- type: edge
- rules: R-CR-358.5, R-CR-357.2.a
- mechanism: MECH-PLAY-STEP5-LEGALITY
- setup: 打出过程中已支付费用，步骤 5 因条件性权限不满足失败。
- actions: 执行撤销
- expect: 打出动作全撤销、卡牌回起始区域；被替换代付的部分仍视为已支付（357.2.a）；不残留非法状态。

### T-0070 主动技能五步（激活）
- type: normal
- rules: R-CR-360, R-CR-361, R-CR-362, R-CR-377.1, R-CR-401, R-CR-402, R-CR-403, R-CR-404, R-CR-405, R-CR-406
- mechanism: MECH-ACTIVATED
- setup: P1 主阶段开环，场上单位带付费主动技能（无目标）。
- actions: 激活并推进 FEPR
- expect: 五步与卡牌同构（入链→选择→定费→支付→复核→确认）；确认后留链待结算。

### T-0071 获得资源技能确认即结算
- type: edge
- rules: R-CR-429.2, R-CR-337.2
- mechanism: MECH-ACT-ADD
- setup: 激活获得资源技能（符文 [E]）。
- actions: FEPR-确认
- expect: 该技能确认后立即结算得资源；不给反应窗口。

### T-0072 装备默认目的地与例外
- type: edge
- rules: R-CR-355.6, R-CR-811.1.d.1.a
- mechanism: MECH-GEAR
- setup: 装备 G-待命 从待命状态打出。
- actions: 打出至其待命战场
- expect: 允许（待命覆盖装备的基地限制）；正常打出同一装备仍只能进基地。

### T-0073 被动授予迅捷的条件复核
- type: illegal
- rules: R-CR-806.4, R-CR-806.4.b
- mechanism: MECH-KW-ACTION
- setup: 卡带条件性迅捷"若对手控制 2 以上单位则迅捷"（注入），打出时条件满足、确认前对手单位被减至 1。
- actions: 打出并推进至步骤 5
- expect: 复核失败→撤销回起始区域。

### T-0074 替换效果每事件一次
- type: normal
- rules: R-CR-370.2, R-CR-372.1
- mechanism: MECH-REPLACEMENT
- setup: 单位甲受两个可替换"受到伤害"事件的替换效果 R1/R2（注入）。
- actions: 造成 2 伤害
- expect: 受影响方控制者选 R1/R2 顺序；每个替换对该事件各生效一次。

### T-0075 摧毁替换与绝念移除
- type: edge
- rules: R-CR-370.1, R-CR-808.1.d.1
- mechanism: MECH-REPLACEMENT
- setup: 单位带绝念触发；其摧毁被替换为"治疗并召回休眠"（注入）。
- actions: 致命伤害清理
- expect: 替换生效：不进废牌堆；已入链的绝念从链移除。

### T-0076 延迟替换窗口外失效
- type: edge
- rules: R-CR-390.1, R-CR-391.1
- mechanism: MECH-DELAYED
- setup: "本回合内下一次受到伤害-2"延迟替换登记（注入），本回合未受伤。
- actions: 进入下回合后造成伤害
- expect: 替换不再适用（窗口关闭）。

## B 块完（T-0035..T-0076）

## 7. 移动、召回与战斗（T-0077..T-0100）

### T-0077 标准移动（基地→控制战场）
- type: normal
- rules: R-CR-144.1, R-CR-420, R-CR-446.1, R-CR-447.1
- mechanism: MECH-MOVEMENT
- setup: P1 控制战场 B1，其基地有活跃单位甲。
- actions: 甲标准移动→B1
- expect: 立即完成、无链无反应窗口；甲状态保留（伤害/增益/贴附）；完成后清理（453）。

### T-0078 移动进非控战场→争夺与对决
- type: normal
- rules: R-CR-450.1, R-CR-344.1, R-CR-345.1
- mechanism: MECH-MOVEMENT
- setup: 战场 B2 由 P2 控制且无其单位；P1 单位甲移动进入 B2。
- actions: 移动并清理
- expect: B2 进入争夺；非战斗对决开始；焦点=P1（争夺发起者）。

### T-0079 拥挤限制
- type: illegal
- rules: R-CR-447.1, R-CR-452.1
- mechanism: MECH-MOVEMENT
- setup: 战场 B1 已有 P2 的 2 名单位。
- actions: P1 单位尝试移入 B1
- expect: 拒绝：不得移入已有 2 名其他玩家单位的战场。

### T-0080 游走扩展终点
- type: normal
- rules: R-CR-810.1.b, R-CR-810.1.c
- mechanism: MECH-KW-GANKING
- setup: P1 单位乙带[游走]位于战场 B1；B2 非拥挤。
- actions: 乙标准移动 B1→B2
- expect: 允许（[游走] 提供跨战场选项）；无[游走]单位无此选项。

### T-0081 召回非移动
- type: edge
- rules: R-CR-456.1, R-CR-458.1
- mechanism: MECH-RECALL
- setup: P1 单位甲在 B1（带伤害 1、增益），效果召回甲。
- actions: 召回
- expect: 甲至其所属者基地；不触发争夺/对决；伤害与增益保留（458）。

### T-0082 装备可召回
- type: normal
- rules: R-CR-457.1
- mechanism: MECH-RECALL
- setup: 装备 G2（未贴附）位于战场 B1（经待命等入场），被召回。
- actions: 召回
- expect: G2 回基地。

### T-0083 战斗启动条件
- type: edge
- rules: R-CR-460, R-CR-461, R-CR-462
- mechanism: MECH-COMBAT
- setup: 战场 B1 双方单位共存而战斗未启动；链上有未决项目。
- actions: 清理评估
- expect: 链非空→战斗不启动（460）；链空后→战斗标记待发生并按 323.10 处理。

### T-0084 战斗步骤1：攻防与焦点
- type: normal
- rules: R-CR-464.1, R-CR-464.2, R-CR-345.1
- mechanism: MECH-COMBAT-STEP1-SHOWDOWN
- setup: P2 单位移入 P1 控制的 B1（P1 有单位）→战斗标记→开启战斗。
- actions: 进入步骤1
- expect: P2=进攻方且得焦点；攻/守触发按 进攻方→（非防守方）→防守方 序入链。

### T-0085 攻守触发每场一次
- type: edge
- rules: R-CR-383.4, R-CR-464.3
- mechanism: MECH-TRIGGERED
- setup: 单位带进攻触发；同回合第二次战斗。
- actions: 两次战斗各检查触发
- expect: 每场战斗各仅检一次：第一场触发，第二场重新可用（每场计数）。

### T-0086 伤害池与先攻分配
- type: normal
- rules: R-CR-465.2, R-CR-465.2.b, R-CR-465.2.c
- mechanism: MECH-COMBAT-STEP2-DAMAGE
- setup: 进攻方单位 {3[M],2[M]}，防守方 {4[M]}。
- actions: 步骤2
- expect: 进攻方伤害池=5、防守方=4；进攻方先分配；随后防守方分配；分配后同时造成。

### T-0087 致命先行
- type: illegal
- rules: R-CR-465.2.c.4.a
- mechanism: MECH-COMBAT-STEP2-DAMAGE
- setup: 防守方单位甲（完整 4[M]）与乙（带 2 伤，4[M]——致少=2）。
- actions: 进攻方对乙先分配 1 点（未达致少）再转向甲
- expect: 拒绝：必须先为单位分配致命伤害才能轮到下一个；且不得超过致少最小值。

### T-0088 壁垒优先分配
- type: illegal
- rules: R-CR-815.1.b, R-CR-465.2.c.6
- mechanism: MECH-KW-TANK
- setup: 防守方含[壁垒]单位与无壁垒单位。
- actions: 绕过壁垒直接给无壁垒者分配
- expect: 拒绝：全体壁垒被分致命前，无壁垒者不是合法分配对象。

### T-0089 后排居末
- type: illegal
- rules: R-CR-826.3, R-CR-465.2.c.7
- mechanism: MECH-KW-BACKLINE
- setup: 防守方含[后排]单位与普通单位。
- actions: 先给[后排]分配
- expect: 拒绝：非后排单位未分致命前，后排不是合法分配对象；顺序=壁垒→普通→后排。

### T-0090 抵挡在分配时生效
- type: edge
- rules: R-CR-437.5, R-CR-465.2.c.5, R-CR-715.1
- mechanism: MECH-ACT-PREVENT
- setup: 防守单位被抵挡 2（延迟替换），进攻方另带额外伤害 1。
- actions: 步骤2 对其实际造成 3
- expect: 额外伤害并入（4）后抵挡抵扣 2→实际承受 2；抵挡耗尽。

### T-0091 战斗结算：防守存活召回进攻
- type: normal
- rules: R-CR-466.3, R-CR-324.1.d
- mechanism: MECH-COMBAT-STEP3-RESOLUTION
- setup: 步骤2 后双方均有存活单位（无结果）。
- actions: 步骤3
- expect: 新对决+战斗标记；战斗清理插 3d：防守方仍在→召回进攻方单位；攻/防身份移除、整场战斗效果失效。

### T-0092 战斗结算：确立控制与征服
- type: normal
- rules: R-CR-466.2, R-CR-466.4, R-CR-467.1
- mechanism: MECH-COMBAT-STEP3-RESOLUTION
- setup: 步骤2 后防守方全部离场，进攻方留场。
- actions: 步骤3
- expect: 进攻方确立控制；争夺清除；未得过分则征服得 1 分（受 470/471 限制判定）。

### T-0093 强攻/坚守生效窗
- type: edge
- rules: R-CR-807.1.c, R-CR-814.1.c, R-CR-466.5
- mechanism: MECH-KW-ASSAULT
- setup: 进攻单位带[强攻2]、防守单位带[坚守1]。
- actions: 步骤1→步骤3
- expect: 步骤2 计算时加成生效；步骤3 结束身份移除后加成消失。

### T-0094 对决关闭双留→无控制
- type: edge
- rules: R-CR-348.2, R-CR-190.2
- mechanism: MECH-SHOWDOWNS
- setup: 非战斗对决关闭时双方单位仍同场。
- actions: 关闭对决
- expect: 无人确立控制；战场维持争夺；后续清理标记战斗待发生。

### T-0095 征服唯一性
- type: edge
- rules: R-CR-470.1
- mechanism: MECH-SCORING
- setup: P1 本回合已从 B1 征服得 1 分；随后再夺 B1（失控后重夺）。
- actions: 第二次确立控制 B1
- expect: 不再得分（每战场每回合每玩家限 1 分）。

### T-0096 据守冲突不重复
- type: edge
- rules: R-CR-470, R-CR-469.2
- mechanism: MECH-SCORING
- setup: P1 回合开始阶段从 B1 据守得 1 分；本回合内尝试再次从 B1 征服得分。
- actions: 再次确立控制 B1
- expect: 不再得分。

### T-0097 终分限制改判抽牌
- type: edge
- rules: R-CR-471.1.b
- mechanism: MECH-SCORING
- setup: P1 分=7（胜利分 8），本回合尚未从 B2 得分；此时征服 B1。
- actions: 征服结算
- expect: 改为 P1 抽 1 张牌而非得分（未满足"本回合已在每个战场得分"）。

### T-0098 燃尽送分不受 470 限制
- type: edge
- rules: R-CR-431.2, R-CR-470
- mechanism: MECH-SCORING
- setup: P2 燃尽送分 P1，P1 本回合已从某战场得分。
- actions: 燃尽结算
- expect: P1 正常获得燃尽分（471/470 的限制不适用——按其条款）。

### T-0099 同分不获胜
- type: edge
- rules: R-CR-194.1, R-CR-472
- mechanism: MECH-WINNING
- setup: 清理时 P1=8、P2=8。
- actions: 胜利检查
- expect: 无人获胜（须高于所有对手）；对局继续。

### T-0100 移动完成清理链
- type: edge
- rules: R-CR-453, R-CR-319.8
- mechanism: MECH-MOVEMENT
- setup: P1 单位移动完成，移动引发对敌方单位的被动伤害致命（注入被动）。
- actions: 移动完成
- expect: 清理立即执行：致命单位摧毁、争夺/战斗标记按需产生。

## C 块完（T-0077..T-0100）

## 8. 附加规则（认输/增益/强力/额外伤害/贴附/未激活，T-0101..T-0110）

### T-0101 认输终局
- type: normal
- rules: R-CR-650, R-CR-651, R-CR-195.1
- mechanism: MECH-CONCEDE
- setup: F-STATE-MAIN 任意时点（含非己回合）。
- actions: P2 认输
- expect: P2 移出对局；P1 获胜；termination=concede；链上 P2 项目与其物体按 652 移除。

### T-0102 增益唯一与+1[M]
- type: normal
- rules: R-CR-702.1, R-CR-703.1, R-CR-426.1
- mechanism: MECH-BUFFS
- setup: 单位甲 3[M] 无增益。
- actions: 给予增益；再次给予增益
- expect: 首个生效后甲=4[M]；每单位至多 1 个增益，第二次按 426/703 上限裁决（不叠加第二个）。

### T-0103 单位离场增益移除
- type: edge
- rules: R-CR-705.1
- mechanism: MECH-BUFFS
- setup: 甲带 1 增益被摧毁。
- actions: 清理
- expect: 增益随甲离开游戏被移除；不产生独立回收/留存。

### T-0104 变为强力事件
- type: normal
- rules: R-CR-708, R-CR-709.1
- mechanism: MECH-MIGHTY
- setup: 单位甲 4[M]，其被动"当我变为强力单位时…"（注入）。
- actions: 给甲增益（4→5）
- expect: 甲成为强力单位；转变事件触发；其后移除增益（5→4）不构成"变为强力"。

### T-0105 非场地区域按印刷战力
- type: edge
- rules: R-CR-711.1
- mechanism: MECH-MIGHTY
- setup: 手牌中 5[M] 印刷的单位（场上无同卡），检查效果引用"是否强力"。
- actions: 评估
- expect: 手牌/牌堆中的单位按印刷战力判定（=5 视为强力）。

### T-0106 额外伤害对多目标分别并入
- type: normal
- rules: R-CR-713, R-CR-714, R-CR-715.1
- mechanism: MECH-BONUS-DAMAGE
- setup: 行动"对两名单位各造成 3"并带额外伤害 +1（注入）。
- actions: 结算
- expect: 每个目标分别承受 4（额外伤害并入同一事件总额后按目标结算，不计两次于同一目标）。

### T-0107 贴附生效并入
- type: normal
- rules: R-CR-717, R-CR-718, R-CR-719.2, R-CR-724.1
- mechanism: MECH-ATTACHMENT
- setup: 装备 G2（+2[M]、效果文本"此单位获得[游走]"）贴附至单位甲 3[M]。
- actions: 贴附完成
- expect: 甲=5[M] 且获得[游走]；G2 规则文本未激活、效果文本激活并入甲。

### T-0108 顶部卡离场贴附留存
- type: edge
- rules: R-CR-719.5
- mechanism: MECH-ATTACHMENT
- setup: T-0107 状态下甲被摧毁。
- actions: 清理
- expect: 甲入废牌堆；G2 卸除并留在当前区域（同一战场/基地）；其效果文本回到未激活。

### T-0109 未激活切换与时间戳
- type: edge
- rules: R-CR-721, R-CR-722, R-CR-723, R-CR-480.2
- mechanism: MECH-INACTIVE
- setup: 持续效果 E 提供 +1[M]（时间戳 t1）←其来源文本被效果指定未激活，再恢复。
- actions: 未激活→再激活→评估甲战力
- expect: 未激活期 E 不生效；再激活后 E 按新时间戳重新参与层序（原 t1 失效）。

### T-0110 部分解除未激活
- type: edge
- rules: R-CR-725.1, R-CR-821.1.c
- mechanism: MECH-INACTIVE
- setup: [武装]卡规则文本未激活；[百炼]单位打出选择该武装。
- actions: 百炼结算
- expect: 必要部分暂时视为激活以完成贴附；其余文本仍按其状态。

## 9. 关键词专项（MVP/P1，T-0111..T-0124）

### T-0111 关键词赋予默认时长
- type: normal
- rules: R-CR-801.3.a.3, R-CR-801.3.a.2
- mechanism: MECH-KEYWORDS-GENERAL
- setup: 效果"单位甲获得[游走]"（无时长表述）。
- actions: 甲随后被召回/移动
- expect: 只要甲留在场上效果持续；离场即失效。

### T-0112 迅捷对决打出
- type: normal
- rules: R-CR-806.1.c.1
- mechanism: MECH-KW-ACTION
- setup: 对手回合法术对决期间，P1 手牌[迅捷]法术。
- actions: legal_actions(P1) 并打出
- expect: 允许打出；无[迅捷]的普通法术仍不可。

### T-0113 迅捷不改自有限制
- type: illegal
- rules: R-CR-806.3, R-CR-806.3.1, R-CR-813.3.a
- mechanism: MECH-KW-ACTION
- setup: P1 带[迅捷]的单位（注入）在对决中，P1 不控制任何战场。
- actions: 尝试打出至非控战场
- expect: 拒绝：打出目的地自有限制不变（基地/控制战场）。

### T-0114 急速活跃进场
- type: normal
- rules: R-CR-805.1.a, R-CR-805.2.b, R-CR-805.6
- mechanism: MECH-KW-ACCELERATE
- setup: 手牌[急速]单位，符文池足以支付费用+[1]+[C]。
- actions: 定费时选择支付急速并完成打出
- expect: 单位以活跃状态直接进场（非先休眠后激活）；确认中即使失去急速仍活跃（805.2.b）。

### T-0115 绝念记录最后状态
- type: normal
- rules: R-CR-808.1.d.2, R-CR-808.1.d.3
- mechanism: MECH-KW-DEATHKNELL
- setup: 单位带绝念"对甲的敌玩家造成等同于我战力的伤害"，战力被临时+2 后遭摧毁。
- actions: 清理 3a/3b→绝念结算
- expect: 入链前记录位置/属性最后状态；结算按记录值（含临时+2）执行。

### T-0116 待命完整流程
- type: normal
- rules: R-CR-811.1.b, R-CR-811.1.c.1, R-CR-811.1.c.2, R-CR-811.1.c.3, R-CR-811.6
- mechanism: MECH-KW-HIDDEN
- setup: P1 控制 B1 无待命牌；手牌[待命]卡，其回合开环。
- actions: 待命→次回合从待命状态打出
- expect: 付[A]牌面朝下入 B1 待命区（非打出、不开链）；下回合起获[反应]打出无视基础费用；打出时开链。

### T-0117 待命打出目标受限
- type: illegal
- rules: R-CR-811.1.d.2, R-CR-811.1.d.3
- mechanism: MECH-KW-HIDDEN
- setup: 从 B1 待命打出带目标的打出效果卡。
- actions: 尝试选择 B2 的合法目标
- expect: 目标须从其待命战场选择（除文本明确使该选择无法达成——811.1.d.2 例外逐目标判定）。

### T-0118 瞬息计分前摧毁
- type: normal
- rules: R-CR-816.1.b, R-CR-816.1.c
- mechanism: MECH-KW-TEMPORARY
- setup: P1 场上[瞬息]常驻牌；P1 控制战场 B1。
- actions: P1 回合开始阶段
- expect: 计分之前触发摧毁该牌（先摧毁后据守计分；若其据守关键则分不得）。

### T-0119 多瞬息仅触发一次
- type: edge
- rules: R-CR-816.2, R-CR-816.2.a
- mechanism: MECH-KW-TEMPORARY
- setup: 常驻牌获得两个[瞬息]实例（印刷+效果赋予）。
- actions: 开始阶段触发枚举
- expect: 仅触发一次摧毁。

### T-0120 预知进场洞察
- type: normal
- rules: R-CR-817.1.b, R-CR-817.2.a
- mechanism: MECH-KW-VISION
- setup: P1 牌堆顶={c1,c2,c3}（seed 固定），打出带[预知]常驻牌。
- actions: 进场触发结算
- expect: 洞察其牌堆顶：每张可选回收；P1 未回收的保持原位（内容仅 P1 可见）。

### T-0121 双预知识别同叠
- type: edge
- rules: R-CR-817.2, R-CR-817.2.b
- mechanism: MECH-KW-VISION
- setup: 同一卡带两个[预知]实例；其间无任何过程。
- actions: 两次洞察分别结算
- expect: 第二次看到的牌堆顶与第一次相同（若未回收）。

### T-0122 伏击打点与[反应]获得
- type: normal
- rules: R-CR-822.1.b, R-CR-822.1.c
- mechanism: MECH-KW-AMBUSH
- setup: P1 在 B1 有单位；手牌[伏击]单位，闭环状态。
- actions: 打出该单位至 B1
- expect: B1 为合法位置（[伏击]权限）；因打至有己方单位战场而获得[反应]（可在闭环打出）。

### T-0123 伏击打点失效
- type: edge
- rules: R-CR-822.3, R-CR-822.3.a
- mechanism: MECH-KW-AMBUSH
- setup: T-0122 中确认前己方单位被效果移出 B1。
- actions: 步骤 5 复核
- expect: 该位置不再有效；若无其他权限覆盖则打出撤销（822.3.a）。

### T-0124 强攻值相加
- type: normal
- rules: R-CR-807.2
- mechanism: MECH-KW-ASSAULT
- setup: 单位自带[强攻1]，效果再赋予[强攻3]。
- actions: 作为进攻方计算战力
- expect: 合计[强攻4]（多来源相加）。

## 10. 横切法则与端到端一致性（T-0125..T-0134）

### T-0125 “无法”高于“可以”
- type: illegal
- rules: R-CR-054.1
- mechanism: MECH-CANT-BEATS-CAN
- setup: 效果 A"你可以打出此牌"，效果 B"你无法打出卡牌"（注入并存）。
- actions: 尝试打出
- expect: 拒绝（B 优先）。

### T-0126 尽可能执行
- type: edge
- rules: R-CR-055.1
- mechanism: MECH-CANT-BEATS-CAN
- setup: 法术三指示："抽 1；对甲造成 2（甲不在场）；获得[1]"。
- actions: 结算
- expect: 第一、三指示执行，第二指示忽略；整体不回滚。

### T-0127 区域归属修正
- type: edge
- rules: R-CR-056.1
- mechanism: MECH-CANT-BEATS-CAN
- setup: 对手效果指示"将 P1 手牌甲放入 P2 牌堆底"。
- actions: 结算
- expect: 甲改为进入 P1 自己的对应区域（P1 牌堆底）。

### T-0128 卡面优先
- type: edge
- rules: R-CR-002.1
- mechanism: MECH-GOLDEN-RULES
- setup: 卡面文本与核心规则表面冲突的注入卡（"此牌可以移入拥挤战场"）。
- actions: 执行该移动
- expect: 卡面允许；但该卡面若表述"无法移动"则规则侧"可以移动"被压（双向校验卡面优先与无法优先的复合）。

### T-0129 第一人称绑定
- type: normal
- rules: R-CR-053.1
- mechanism: MECH-SILVER-RULES
- setup: 两张同名带"我[M]+1"被动的甲、乙同时在场。
- actions: 评估属性
- expect: 各自只增益自身；互不影响对方（自称绑定来源物体）。

### T-0130 观察不泄漏（端到端）
- type: illegal
- rules: R-CR-128, R-CR-128.1, R-CR-811.6.a
- mechanism: MECH-PRIVACY
- setup: 完整对局任意状态（注入：对手手牌 4、牌堆 20、B2 有待命牌）。
- actions: observe(P1)、legal_actions(P1)、export_trace(visibility=public)
- expect: 三处均不含对手手牌内容、牌堆顺序、待命牌内容与身份；对手手牌仅存数量。

### T-0131 已选动作皆合法（回放校验）
- type: edge
- rules: R-CR-334, R-CR-312.1, R-CR-358
- mechanism: MECH-TASKS-FEPR
- setup: 用随机策略跑 N=20 局（仅骨架卡池）。
- actions: 回放每局 trace，逐步校验 chosen_action ∈ legal_actions(state)
- expect: 100% 成立；非法提交计数=0；每步 before/after 状态哈希链连续。

### T-0132 同 seed 终局一致
- type: edge
- rules: R-CR-115, R-CR-306, R-CR-472
- mechanism: MECH-SETUP-PROCESS
- setup: 固定 seed+固定动作脚本的完整对局 × 2 次。
- actions: run_episode(policy_script, seed=42) 两遍
- expect: 终局 winner/length/最终状态哈希一致；逐步事件流一致。

### T-0133 快照恢复等价
- type: edge
- rules: R-CR-310, R-CR-331
- mechanism: MECH-TURN-STATES
- setup: 对局推进至任意闭环状态（链上有待处理项）。
- actions: snapshot→继续若干步记录 S_a；restore→重放相同动作序列记录 S_b
- expect: S_a 与 S_b 状态及后续演化完全一致。

### T-0134 随机对局可完结
- type: normal
- rules: R-CR-302, R-CR-196, R-CR-431.3.c.1
- mechanism: MECH-TURN
- setup: 双方随机策略，骨架卡池（无文本），步数上限 5000 防死循环。
- actions: run_episode × 50（不同 seed）
- expect: 全部对局在步数上限内以 score/burnout/concede 之一终止；无非法状态；termination_reason 分类统计可导出。

## D 块完（T-0101..T-0134）。矩阵合计 134 案例。

## 11. 覆盖声明与维护

- MVP 行为机制全部具备 ≥1 正常 + ≥1 非法/边界案例，或经 §0 豁免清单显式标注；
  结构性机制与 meta 类规则无独立案例（由所属章节案例间接覆盖）。
- P2 机制（回响/装配/百炼/XP/额外回合/另做选择/不可被选取/宣告/无视/灵便/等级/狩猎/唯我/已强化等）
  不在本矩阵范围，随阶段 4 首批对应卡牌启用时新增案例并回填。
- 新增案例编号顺延（下一可用：T-0135）；修改既有案例须同步检查 spec/rules_spec.yaml 的 test_ids 回填
  （重跑 `python scripts/spec/build_rules_spec.py` 即可）。
