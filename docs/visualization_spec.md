# 对局可视化规格（docs/visualization_spec.md）

> 阶段 2 交付物。只读回放器 + trace 数据契约。**可视化消费记录，绝不驱动引擎**
> （`replay`=再执行产生状态，`playback`=消费记录展示，两者严格区分）。
> 数据缺失一律显示「未知」，禁止编造牌面/奖励/网络输出。

## 1. 存储布局与命名

```
runs/<run_label>/                    # 一次训练/评估会话
  metrics.jsonl[.gz]                 # 汇总指标（与对局回放解耦）
  traces/
    <match_id>.jsonl[.gz]            # 单局 trace（可见性由 Header.visibility 标记）
  traces_priv/                       # 特权 trace（显式授权、默认不产生）
  index.sqlite 或 index.jsonl        # 对局索引（match_id/seed/policy/结果/长度/异常）
```
- 大小纪律：单局 debug 预估 ≤ 数 MB；滚动写入 + 完整性计数；
  retention/压缩由运行配置决定，不影响 schema。
- `match_id`：`yyyymmdd-<时间戳>-<rand8>`；`step_id` 决策步 0 起递增；
  `event_seq` 局内严格递增全局序。

## 2. Trace 数据契约（rifttrace/1）

### 2.1 EpisodeHeader（每局首行，type=header）
```json
{
  "type": "header",
  "schema_version": "rifttrace/1",
  "engine_version": "0.1.0",
  "ruleset_version": "core-2026-07-zh+patch-2026-07+errata-2026-07",
  "card_db_version": "skeleton-v1",
  "spec_hash": "<sha256[:12]>",
  "action_layout_version": "actlayout/1",
  "match_id": "...",
  "seed": 42,
  "config": {"mode": "duel_1v1", "win_score": 8, "decks": ["F-DECK-A", "F-DECK-B"], "max_steps": 5000},
  "policy_ids": ["random/v1", "random/v1"],
  "started_at": "ISO8601",
  "visibility": "public",
  "trace_level": "summary|sampled|debug"
}
```

### 2.2 DecisionRecord（type=decision）
```json
{
  "type": "decision", "match_id": "...", "step_id": 12,
  "player_id": 0,
  "request_kind": "MAIN_ACTION",
  "observation_ref": "sha256(obs 规范序列化) 或 snapshot 步索引",
  "legal_action_ids": […],
  "action_mask_ref": "actlayout/1#12",
  "chosen_action_id": 37,
  "policy": {"policy_version": "…", "checkpoint_id": "…",
             "action_prob": 0.42, "topk": [[37, 0.42], [3, 0.31]],
             "value_estimate": 0.05},
  "rng_state_ref": {"recycle_random_order": 3, "effect_random": 0}
}
```
规则：**policy 字段仅在训练器实际写入时存在**（随机/脚本策略省略）；
`chosen_action_id ∈ legal_action_ids` 由回放器复验（T-0131）。

### 2.3 EventRecord（type=event）
```json
{
  "type": "event", "match_id": "...", "event_seq": 101, "step_id": 12,
  "rule_ids": ["R-CR-315.4", "R-CR-431.2"],
  "card_ids": ["uid:117"],
  "event_type": "DRAW",
  "public_payload": {"player": 0, "drawn_count": 1, "deck_remaining": 35},
  "privileged_payload": null,
  "before_state_hash": "…", "after_state_hash": "…"
}
```
- 事件一律由引擎产生；`privileged_payload` 仅 privileged trace 填充
  （含来源决定版，如燃尽洗牌后顺序摘要），public 版置 null 而非删除字段。

### 2.4 SnapshotRecord（type=snapshot）
```json
{
  "type": "snapshot", "match_id": "...", "step_id": 20,
  "public_view_by_player": {"0": {…}, "1": {…}},
  "privileged_state_ref": null,
  "rng_state_ref": {"recycle_random_order": 3},
  "state_hash": "…"
}
```
- `public_view_by_player` = 该步引擎公开观察的最小可回放序列化（与 `observe()` 同源）。
- 完整（特权）快照分存于 traces_priv，只有在 trace_level=debug+授权时写入。

### 2.5 EpisodeFooter（每局末行，type=footer）
```json
{
  "type": "footer", "match_id": "...",
  "result": {"winner": 0, "termination_reason": "SCORE", "modal_winner": false},
  "reward_by_player": {"0": 1.0, "1": -1.0},
  "length": {"decision_steps": 87, "turns": 6, "events": 402},
  "invalid_action_count": 0,
  "final_state_hash": "…",
  "trace_completeness": {"expected_events": 402, "written_events": 402, "ok": true}
}
```

### 2.6 兼容与迁移
- reader 首检 `schema_version`；`rifttrace/1 → 1.x` 仅允许新增字段；
  破坏性变更升主版本，viewer 对未知主版本拒绝读取并提示。
- `EventType` 新增值向后兼容（viewer 未知类型显示原始名+"未知事件"标记）。

## 3. 回放器功能规格（viewer/，离线单 HTML + JSONL）

### 3.1 场面
- 双基地（各玩家行内）、两个战场区（每区：控制者标记/争夺标记/单位列表含
  战力-伤害/休眠/眩晕/增益/贴附数/关键词徽标/待命位"背面"卡）、回合/阶段/四态、
  符文池（双）、分数、手牌数（对对方）、废牌堆/放逐计数与列表（公开）。
- 当前行动玩家与请求类型横幅（「MAIN_ACTION/REACTION 执行窗/战斗分配」…）。
- 隐藏区：待命卡=卡背图样；内容仅在 privileged 视角显式授权后可见。

### 3.2 时间轴
- 按 step_id 滑动（决策帧），帧内展开 event_seq 列表；
  播放/暂停/倍速（0.5/1/2/4×）；键盘 ←/→ 步进；跳转：回合/战斗/得分/终局锚点。
- 每帧显示「动作前 → 动作后」公开差异（字段级 diff：新增/移除/数值变化三型）。

### 3.3 决策面板
- 当前 step：请求说明、合法动作列表（解码为中文简述+规则锚点）、已选动作高亮。
- 若 DecisionRecord.policy 存在：展示 top-k 概率、value 估计、checkpoint_id。
- 关联显示本帧相关 rule_ids（点击→rules_spec 摘要？M1 期直接显示规则号与 canonical 摘要）。

### 3.4 视角切换
- `P0 / P1 / Observer(both-hidden) / Privileged` 四档；默认 Observer 仍按 public 过滤；
  Privileged 需页面显式确认 "I am authorized" 且仅当有 traces_priv 数据；
  隐藏信息在 P0/P1 视角严格打码（T-0130 的 UI 对应项）。

### 3.5 对局索引页
- 读取 index：表格列 match_id/seed/policies/胜负/长度/非法/异常/引擎版本；
  筛选与排序；点击进入回放。异常局（invalid>0、truncated、burnout）红色标签。
- 训练指标页（独立、不进本回放器）：metrics.jsonl 画图（SPS/长度曲线/胜率趋势）。

### 3.6 校验显示
- 加载即复验：hash 链连续（相邻 event 的 after_hash == 下一个 before_hash）、
  completeness.ok、chosen∈legal。失败项在页面顶部列出并禁止播放（防误导）。

## 4. 性能与隔离验收

| 项 | 要求 |
|---|---|
| 依赖方向 | viewer 无引擎代码（纯 JS 解析 JSONL）；引擎无 viewer import |
| headless 默认 | 训练路径永远不需 viewer；trace off 时引擎无 JSON 格式化 |
| 等级对比 | bench 记录 off/summary/sampled/debug 的 SPS 与内存/磁盘差异（TM-1 附件） |
| 确定性 | 给定 trace，`playback` 每帧公开场面 == 同 seed `replay` 同步 `observe()`（抽样比对） |
| 泄漏 | viewer public 渲染不含任何对手私有 uid/def（代码审查+样例断言） |

## 5. VM-1 验收（首个可视化里程碑）

输入：阶段 3 随机策略 fixture trace（summary 等级）≥3 局或 1 局含完整 打出/移动/战斗/得分。
1. 3.1 场面与 3.2 时间轴逐帧正确（抽查每帧 vs replay 公开观察一致）。
2. 3.3 决策面板显示合法动作与已选动作；随机策略无 policy 字段时正常省略。
3. 隐藏区全程打码；无任一对手手牌内容渲染。
4. 终局帧显示 winner/termination/final hash；完整性校验通过。

## 6. 后续阶段钩子

- 阶段 4：卡片图渲染（cards_bilingual 图片 assets）、效果文本展示、贴附堆展开。
- 阶段 5：重放校验批跑器输出（reports/replay_validation.md）链接到异常帧。
- 阶段 6：决策面板显示 policy 字段；信念采样搜索视图（仅 privileged、明确标注）。
