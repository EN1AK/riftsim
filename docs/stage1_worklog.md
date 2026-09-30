# 阶段工作日志（防上下文丢失）

> 最后更新：2026-10-01。**阶段 0–3 验收；阶段 4 四轮交付推进中：cardfx per-card 脚本架构 + 383 触发注册表首批落地**（hold/conquer + score/channel 载荷），测试 132 绿。效果事实源=`src/riftsim/cardfx/*.py`；中阶段目标=把 480 张迁移草稿逐 set review 为「已实现-完备」并继续手写未适配卡。**阶段 5 暂缓**（真卡组由用户提供后一并启用 record_decklists/replay 卡组感知——该两项基建已就绪）。

## 阶段 4 交付物（首轮：回放器 + 效果地基）

### 回放器（VM-1 通过）
- `viewer/`（index.html/app.js/tracecore.js/styles.css）：单文件离线、纯 JS 消费 trace、零引擎代码；文件选择/拖拽加载多局。场面（双基地/双战场/控制·争夺/单位战力-伤害-休眠-眩晕-增益-贴附-关键词/卡背打码/回合·阶段·四态/符文池·分数）、时间轴（帧内事件 event_seq 展开、播放/暂停/0.5–4×、←/→、回合·战斗·得分·终局锚点、前后帧字段级 diff 三型着色）、决策面板（请求中文简述、合法动作解码+已选高亮、policy 字段仅实证存在才显示、本帧 rule_ids）、视角 P0/P1/Observer/Privileged 门控（Privileged 需授权且仅当有 privileged_state_ref；现 trace 无→禁用流程按规格）、索引页（match/seed/policies/胜负/步长/非法/异常红标/引擎版本/点击切换）、终局面板（winner/termination/final hash/completeness）。
- 加载即复验（§3.6，失败顶部列示并禁播）：schema 主版本拒绝、hash 链（引擎按步整块记录 before/after，折叠后链式比对）、completeness.ok 与计数 vs 实际、chosen∈legal（字节相等）、match_id 一致、event_seq 严格递增。
- 校验证据：`python scripts/viewer_check.py` 4/4 fixture PASS；`node .tmp/viewer_unit.js` ALL PASS（4 fixture 双视角隔离：Observer 座位对象重建后 hand/hidden 恒 null，P0 己方手牌+己方待命可见且对方恒打码；chosen∉legal / hash 链断 / 未知 schema 主版本三型损坏检出）。
- 已知口径差异（记录在案）：**summary 级 sink 不落快照**（trace/sink.py 策略：snapshot 仅 debug/step 全量或 sampled/每 N 步），VM-1 入参条款「summary 等级 ≥3 局」与此有张力；当前 VM-1 以 debug 级 fixture（m-1fd805f27d84/m-90b60feff4ae，74 步快照、含打出/移动/战斗/得分全程）按「或 1 局含完整…」分支验收。summary 局场面按规格显示「未知」。是否在 summary 通知期快照（性能代价）留待阶段 5 决议。

### 卡牌数据库与效果系统（地基）
- `src/riftsim/carddb.py`：cards_bilingual.db 全量 1267 张 → CardDefinition 注册表 + CardDbAudit；card_db_version=语义列规范化哈希+来源标注（cdb1:<12hex>@cards_bilingual.db）；混色符能费卡（41）与类型缺失卡（2）按「不猜」进 unsupported；特性缺省按 color_cn 回填（69 张入审计）。
- `src/riftsim/effects.py`：CN 权威白名单解析（EN 交叉校验）：a)　「此牌以休眠状态进场。」/ "This enters exhausted." → enters_exhausted（R-CR-369.3/143.4/359.2.c）；b)　「{{横置}}：对…造成N点伤害」/ ":rb_exhaust:: Deal N to …" → activated_deal_damage（377.1/135.2.e.2/414.1/417.1，目标白名单两类）；c)　行首关键词行+链接([X>]/[X][>])+破折([X]—…)特例（绝念 808.1.a/鼓舞 812/强化 827.1）→ 印刷关键词。其余句式一律 unparsed，不模糊猜。
- 接线：playing.py（deal_damage 宣告时随动选定目标、结算时复查 scope 失效→fizzle 事件 R-CR-359.3.e.9；enters_exhausted 覆盖装备默认进场；静态 kind 不可激活 377.1；非法/越权提交 IllegalActionError 且状态不变）；enums.py Keyword 800..829 全 25 枚举；cards.py/state.py AbilityDef 增 damage/target_scope 并序列化往返。
- 测试：54 → **121 绿**（解析单测 51 + 全库加载 9 + 打出/技能集成组合 7：OGN-017 真卡组组 休眠进场/目标展开/伤害生效/目标失效 fizzle/静态不可激/非法拒改状态/快照往返）。

### 覆盖报告（reports/card_coverage.md；scripts/cards/card_coverage_report.py 幂等重生成）
- 可加载 1224（可执行=非空文本全解析 **147** / 无文本 83 / 部分支持=有未解析句式 **994**）；未支持 43（混色符能费 41 + UNL-T04/T08 类型缺失 2）；规则歧义阻塞 0（514 R-CARD 保持 deferred，OPEN-1..6 为精度暂缓）。
- CN/EN ParseConflict 实际 7 条，全部裁决（解析器口径差异 5：EN 单行串联/裸词标记未入白名单，CN 权威面不受影响；源文本缺失 2：UNL-T02/T07 token 中文无文本）。
- 下批白名单候选（unparsed 聚类 top5）：①装备资源技能「[E]：[反应]—[获得][色]，用以支付符能费用」×12；②可选附加费「你可以选择支付…作为打出我的额外费用」×7；③静态「我以活跃状态进场」×6；④打出位置选项「你可以选择将我打出到一处开放的战场」×6；⑤法术直伤「对战场上的一名单位造成N点伤害」×4（另有「当你打出我时，抽牌」×5）。

### 阶段 4 遗留（接阶段 5/效果量产）
- 967 句式的白名单量产（按覆盖报告 §4 新聚类序）；关键词语义接线：P1 已接 805/807/809/814/816/817/822，**808 绝念暂缓**（依附触发注册表入链，last_known 已备）；818/819/820/823/824/827/828/829 P2。
- 混色符能费 schema（41 张需要 dual-color cost_power 表达）。
- Layers/替换·延迟效果/触发注册表入链/Token·计数标（阶段 3 遗留，随效果量产）。
- viewer：卡片图未下载（image_url 占位，展示走文本卡）；summary 快照策略决议（见上）；Privileged trace 产线未建（traces_priv）。

### 本轮文件（首轮）
viewer/{index.html,app.js,tracecore.js,styles.css}；scripts/viewer_check.py；scripts/cards/card_coverage_report.py；reports/card_coverage.md；src/riftsim/{carddb.py,effects.py}(新) + cards/enums/playing/state(修)；tests/test_effects_parse.py、test_carddb.py、test_playing_effects.py；.tmp/probe_* 与 .tmp/viewer_unit.js（审计留档）。

## 阶段 4 三轮交付（架构转向：cardfx per-card 脚本）

### 转向决策（2026-09-30 用户拍板）
解析式白名单天花板（967 张部分支持、885 长尾模板）+ 成熟先例（ygopro core+per-card Lua）→ **全量转向 per-card 脚本**。保留的正确性资产：引擎仍是合法动作唯一聚合者；横切规则注入位（目标失效 359.3.e.9/费用/快照/回放/隐藏信息）全部不变；通用 kind 结算保留为原语库（spell_damage/spell_draw/spell_pump/on_play_draw/on_play_pump/gain_resource/extra_cost/...）供脚本声明复用；孤例用 `AbilityDef.resolve_fn` 命名回调（快照只存字符串 key，函数不进序列化）。

### 落地清单
- `src/riftsim/cardfx/__init__.py`（新）：`card()` 注册（重复登记即错）、`resolver()` 命名回调、`apply_fx()` 覆盖到 carddb 静态定义、`reviewed` 完备标记、`registry()` 统计视图；set 分文件 ogn/sfd/unl/ven/fnd/arc/ogs/sgn。
- 迁移：`scripts/cards/gen_cardfx_from_defs.py` 一次性生成 535 张草稿（已删，git 历史可考）；**保真验证**：切换前后 1224 defs 效果面 diff=0（`.tmp/defs_fx_baseline.json` vs `after_switch`，工具 `scripts/cards/dump_defs_fx.py` 保留）。
- 退役：`src/riftsim/effects.py`、`tests/test_effects_parse.py`（96 个解析单测）删除；carddb 不再解析文本、无 ParseConflict（交叉校验能力随架构放弃，已告知用户）。
- carddb：RUNE 技能引擎统一供给（164.2）不变；audit.hook_cards/keyword_cards 改从 cardfx 统计。
- play 注入位：apply_card_text/apply_ability_resolution/handle_activate/_push_enter_triggers 四处 resolve_fn 优先分发；`_push_enter_triggers` 支持 `kind="trigger"+resolve_fn` 孤例进场触发。
- 覆盖报告重写（`scripts/cards/card_coverage_report.py`）：分层=完备(reviewed)/草稿/vanilla/未适配；无文本 85=66 基本符文+2 unsupported+17 vanilla 口径注明；零文本解析依赖。
- 手写批次 3（新原语 spell_pump/on_play_pump + 中文数字语境）：
  - 原语：本回合临时战力修正（`might_temp` 字段/3.d 清除/序列化/obs 输出基建本就备好）；`AbilityDef.pump_value`；目标枚举与预检同 spell_damage 路径（355.6；359.3.e.9 fizzle）。
  - 手写 6 卡（reviewed=True）：OGN-154(+7任一单位)、SFD-097(+5)、OGN-197/197a/197b(打出+3)、OGN-083(抽两张，中文数字)。
  - 测试 `tests/test_cardfx_batch3.py` 8 个：枚举/数值参数化/fizzle/317.2.c 回合结束失效/触发链/源离场 ignore/抽两/快照往返。
- 测试画像：96（转向后基线）→ **104 全绿**（+8 批次 3；test_carddb 白名单 +spell_pump/on_play_pump）。
- 阶段 5 前置基建顺带就绪：`GameConfig.record_decklists`（setup meta.config 记完整 def_id 卡表）、`replay._config_from_header`（trace 真卡组回放重建，旧骨架 fixture 兼容 fallback）——真卡组由用户提供后启用。

### 当前覆盖（cardfx 口径，2026-10-01）
已实现-完备 **55** / 已登记-草稿 **480** / vanilla 17 / 未适配 **606** / unsupported 43。

### 重大事件（2026-09-30）：卡牌数据缺陷修复 + reviewed 清理
**起因**：用户指出「枯萎战斧的四点伤害效果没录全」。
**溯源（两级缺陷）**：
1. **合并管线缺陷**：`scripts/cards/build_bilingual_db.py` 只取 EN 源 `text_plain`，**丢弃 `effect_plain` 拓展栏**（32 张卡受影响，例 UNL-019 的"回合结束未征服→卸载+自伤4"）。已修复（合并两栏）+重建卡库。
2. **CN 抓取源缺陷**：cards_cn `effect` 字段对部分卡的卡体效果段缺失（例如 UNL-039/096/SFD-172/073 装备的「宿主获得[狩猎]/[绝念]/[等级3]/Mech」提示段在 CN 源文本里就没有）；CN 侧缺段需重抓或对照 EN 补齐（待后续；发动机实现以 **EN effect 段权威 + CN 名称显示**）。
**影响与清理**：
- 暴露 reviewed 误标：原 70 张中 **17 张装备系**只接了装配费、未接卡体效果段（`SFD-016/030/042/051/086/108/115/118/124/134/153/172/UNL-019/039/096/VEN-011/VEN-027`）→ 全部降级回评（注释写明未接段落+原因+参考 EN）。另有 3 张 SFD-059/090/139 早前已降——合计 reviewed 70→53。
- OK 的 6 张提示行卡（SFD-009/033/064/102/133/073）保留。
**防呆升级**：`test_reviewed_has_no_unwired_effect_lines` 双侧审计（CN/EN）；EN 侧放行关键词提示行（[Assault]/Ganking/…）与类别声明行白名单（「I am a Mech.」）。其他行仍要求 abilities 登记——审计基准对齐 rift bilingual 修复后的完整卡面。
**数据结论透给直接用户**：「四点伤害」实效存在，只是 bilingual 库此前丢失了 effect_plain 栏——已恢复并按标准回评流程处理。

### 全库文本完整性最终审计（2026-09-30，重建后）
- builder 过滤 effect_plain 抓取噪音行（纯数字/长度<4 注释 DIV，例 VEN-103 的 `'1'`）后重建。
- `text_en` **无截断残留**：先前审计报的「未闭合行」全部验证为卡面合法格式（以 `"` 结尾的引用文本 / `Choose one —` 分行布局 / Empower 费用行）；VEN-110a/113/114/188 等多行卡重建后完整。
- `text_cn` **39 张缺段**（CN 抓取源问题，清单见 [.tmp/full_data_audit.out](.tmp/full_data_audit.out)）——以 EN effect 段为权威实现依据；CN 重抓待后续。
- **用户确认（2026-09-30）**：所有**装备卡**均受此乱（CN `effect` 字段只抓回主段、缺卡面第二段——CN 官网装备卡面的第二区块布局导致）；少例外也见于非装备（OGN-035/207/248/223 等极少数）。**中文卡片爬取（cards_cn effect 字段）确认存在数据缺失，未修复，重抓/人工对照 EN 补齐后修复**。
- **补齐脚本** `scripts/cards/fill_cn_gaps.py`（2026-09-30）：扫描 bilingual 中 EN>CN 行数差 49 张生成对照清单 `.tmp/cn_gaps_candidates.md`（EN 缺段原文 + 模板机翻 CN 占位，未匹配模板者标 `[需校对]`）+ 待执行 SQL `.tmp/cn_gaps_apply.sql`（默认不执行；人工逐卡审定后取消 `BEGIN;` 注释事务应用）。注意有的 EN 多行其实是 CN 侧聚合表述（如 OGN-248「进行六次」合并六条同效果），不都要补——**人工对帐必做**。
- **用户审批执行（2026-09-30）**：`text_cn_filled` / `cn_fill_note` 新列已建；`text_cn` 原样保留。审定后 49 候选 → 6 张「不用改」（OGN-035/207/248、SFD-223/223*、UNL-009——CN 侧聚合表述或无需改）+ 6 张 `[NO TEXT]` 占位（VEN-R01~06 不补）+ **37 张已按候选行补齐**，每行前置统一权威标记 `[EN补·非权威CN — 对照 EN 补齐；CN 抓取缺段；释义以官方原版为准]`。验证 UNL-019/SFD-223/UNL-T08 三类典型到位；测试 128 全绿。
- `text_cn` 空的 12+ 张基本全符文卡（R01~R06 各 set/+变体）与 token/指示物（SFD-T01/OGN-271~273/UNL-T2~T8），合法无文本；部分在 vanilla 档。
- 测试 128 全绿；reviewed=53（最终 clean 基线）。

### review 进展（rq-4 修订：819 灵便 + 装配语义修正，2026-09-30）
- **用户纠正的语义**：818 装配是**场上（基地）装备的主动技能**（首版误实现为手牌技能）；819 灵便是「自带[反应] + 打出时触发一次贴附」（819.1.d），非手牌机制。
- 修订落地：装配枚举/校验/结算源全部改为场上（`_activate_options` equip 分支 + handle_activate zone==BASE 校验 + `_resolve_equip` 源在场复查）；`_resolve_equip` 通用于 818 技能与 819 触发（同为「源装备在场→贴附」）；失效指示无视→装备滞留**基地**（359.3.e.6；821.1.c.5 同原则）而非早期误实现的手牌。
- 819 接线：legal_reactions gate（819.1.b 自带[反应]）；`_play_options` GEAR的「打出+触发目标」变体（每友方单位一变体；基础打出同时可用）；`_push_enter_triggers` 挂点（装备入场后 trigger kind="on_play_equip" 随打出 choices 带目标）；修复 `_untrack_source`（playing 版仅源区）贴附移除区域残留 → 用 resources`_untrack` 全分支版。
- 已知间隙（TODO-383 目标时点）：819 触发目标在打出宣言时选定；383 触发式技能的规则选择时点为入链时——当前近似，待触发注册表（383 通用）时修正。
- SFD-022/056/064 恢复 reviewed（819 接线后），审计 WIRED +EQUIP/QUICKDRAW；测试 120→126（+6：819 触发/变体/fizzle/反应时机 + 场上装配修正相关改断言）。
- **事件流演示抓到一个 719.5 条件 bug**：`resources._untrack` 的 detach 循环无条件在每次区域移除时卸除贴附卡——宿主「战场→基地」（场上→场上）移动亦误触发 DETACH（演示幕 1 可见 DETACH+RECALL 序列）。修：`_untrack(board_move=True)` 由 movement 两分支传入跳过 detach；加回归测试 test_board_move_does_not_detach。测试 126→127。
- 终端事件流演示工具 `.tmp/demo_effects.py`（五幕：装配+加成+跟随/装配失误/法术直伤致死/灵便打附/预知洞察），输出 `.tmp/demo_effects.txt`。
草稿 review 队列按 set：ogn 142、sfd 139、unl 128、ven 111、ogs 11、arc 3、fnd 1；606 未适配聚类底稿在 `.tmp/review_queue.txt`（A 仅关键词 61 / B 单句式 12 / C 复杂 456）。

### review 进展（383 触发注册表首批，2026-10-01）
- **基建** `src/riftsim/triggers.py`（新）：`fire(state, event, player=, battlefield_index=)` 按「宿主在触发战场 + 装备控制者==触发者（卡面『我』）+ ability.trigger==event」收集注册，链项 kind="trigger" uid 确定序入链（383.3；383.3.d 玩家定序仍记近似）。AbilityDef +trigger/payload/value 三字段（cards.py），state.py 序列化往返。
- **挂点**：scoring.score_conquer 征服时刻（确立控制，470/471.1.b 拦分不拦触发）后 fire conquer；phaser.score_hold 每次据守得分后 fire hold；phaser.begin_after_triggers 拆段——据守触发链 live 则 sub_step="begin_after_hold_triggers" 停链，结算干净后由 engine.advance 续 315.3 召出/315.4 抽牌/316 主阶段。
- **载荷 dispatch**（playing._resolve_trigger_payload）：score=触发控制者 +value 分（卡牌效果分，470 战场分限不适用）；channel=召 value 枚符文后置休眠（430.2/430.5 休眠进场，430.1 默认活跃被卡面覆盖）；未知载荷 emit unwired_payload 不静默。
- **首批两卡**（均由 bilingual 修复后暴露的降级档恢复 reviewed）：SFD-115 三相之力（据守+1 分，trigger=hold/payload=score/value=1；锚 383.3+469.2）、SFD-118 碎骨棒（征服召 1 休眠符文，conquer/channel/1；锚 383.3+430.2/430.5）。
- **测试** tests/test_triggers.py（新）5 项：据守触发 +1 分（总 +2 断言 SCORE trigger_score/383.3 规则锚）、征服触发召休眠符文（基地 +1 且 exhausted）、宿主不在触发战场不触发、无人据守不触发、SFD-124 弃1抽1 skip（RESOLVE_CHOICE 续段留二批）。测试脚手眼：真实流程 score 函数只在 advance 内跑（current_request=None），测试直调需清停靠请求再 advance 踢 FEPR——已固化到 helper 注释。tests/test_carddb.py hook 白名单 +trigger。
- 测试 127→**132 绿**；reviewed 53→**55**，drafts 482→480。
- **二批队列**：SFD-124 弃抽（choose_discard 续段）、SFD-016/190 atk_defend 身份触发、VEN-011 move 触发、UNL-019 end_of_turn 触发（「deal 4 to me」对象语义=宿主 vs 装备自身 rules.db 无裁决 → 记 docs/unresolved_rules.md）；增益（SFD-108）/Token（SFD-086/134/153）/条件持续（SFD-042/VEN-027）/替换（SFD-051）/效果改写（SFD-030）/文本拷贝（SFD-059）/放逐联动（SFD-090）随后。

### review 进展（rq-4 装配，2026-09-30）
- 818 装配全链路接线：equip 原语（手牌主动技能 818.1/377；费用 818.1.c.3 含法力+特性符能）→ 主阶段枚举（手牌装备×己方在场单位）、目标范围 818.1.c.2 你控制的单位、法盾 [A] 附加费复用 809（己方目标豁免）、支付→链结算（377.3；非 429.2 即时——`immediate` 按 kind 强制 False，堵住 gain_resource 语义泄漏）、818.2 贴附建立（719.3 同位置/719.4 状态独立）、718.4/137.3.a 战力加成入 effective_might、719.5 离场卸除（既有）+ 719.3.a 跟随宿主移动（movement 同步）。fizzle 语义（359.3.e.6/9 指示无视→源卡滞留手牌；对照 821.1.c.5 同原则）。
- 32 装备卡 abilities 批量登记（`scripts/cards/add_equip_abilities.py` 从装配行抽费用符号，人工核对输出）；标 reviewed 28（SFD-022/056/064 含未接线 {{灵便}}819 撤销留草稿；VEN-137 第二行复制体效果未实现留草稿）。
- 测试 +9（tests/test_equip.py：枚举/费用/范围/贴附/战力加成/跟随移动/719.5/fizzle 滞留手牌/招募敌方目标防御），测试总数 111→120。审计 WIRED_KEYWORDS +EQUIP。
- 修复链路缺陷（TDD 过程发现）：AbilityDef.immediate 默认 True 的 gain_resource 语义误染 equip → handle_activate 强制 kind=="equip" 时链项 immediate=False。

### review 进展（rq-1a/rq-2a，2026-09-30）
- rq-1a：A 类（纯关键词提醒行、效果面=keywords 完备）×61；仅标**关键词全接线**子集 28 张（equip 26/weaponmaster 6/quickdraw 1/hunt 1 共 33 张待关键词接线后补标）。批量标记工具 `scripts/cards/mark_reviewed.py`（幂等插入 reviewed=True）。
- rq-2a：B 类 12 张单原语句式：补 5 张 abilities（FND-196/SFD-034/SFD-087/UNL-066/SFD-066），标 8 张（REPEAT/FLOW 未接线的 SFD-034/SFD-066/UNL-061/VEN-049 留草稿档）。
- **揪出存量 bug**：`_affordable_with_runes` 的 [A] 伪域缺口式在余额不足扣减 specific_total 时取负差反向虚增 recycles_needed——资源紧时合法动作静默丢失（SFD-087 E2[B]×3 暴露；batch3 测试固化回归锁）。
- `tests/test_cardfx_audit.py` 登记审计 4 项：孤儿登记/reviewed 关键词 ⊆ 已接线/reviewed 注释行全覆盖/reviewed 唯一非空。
- 测试 111 全绿（96→104 batch3→108 audit→111 rq-2a）。

### 三轮文件
src/riftsim/cardfx/{__init__.py,ogn.py,sfd.py,unl.py,ven.py,fnd.py,arc.py,ogs.py,sgn.py}(新)；cards.py(+resolve_fn/pump_value)；state.py(序列化两字段)；carddb.py(cardfx 路径)；playing.py(resolve_fn 分发×4 + spell_pump/on_play_pump 注入位 + 目标枚举合并)；config.py/setup.py(record_decklists)；replay.py(_config_from_header)；scripts/cards/{card_coverage_report.py(重写),dump_defs_fx.py(新)}；tests/{test_cardfx_batch3.py(新),test_carddb.py(改写 2 测试)}；删除 effects.py/test_effects_parse.py/gen_cardfx_from_defs.py。

## 阶段 4 二轮交付（效果续批 + P1 关键词接线）

### 新增白名单句式（effects.py，CN 权威 + EN 交叉校验对称）
d) 装备资源技能「{{横置}}：{{反应}}—{{获得}}{{色}}，用以支付符能费用」→ gear_gain_resource（grant_power_domain；377/356.2.a）；e) 可选附加费「你可以选择支付…作为打出我的额外费用」→ optional_extra_cost（cost_symbols，356.2）；f) 「我以活跃状态进场。」→ enters_ready（369.3.a）；g) 「你可以选择将我打出到一处开放的战场。」→ location_open_battlefield（170.11.c）；h) 法术直伤「对战场上的一名单位造成N点伤害[。，]」→ spell_damage（417.1，限法术；VEN-059 源站逗号尾经 EN 互证并入）；i) 法术抽牌「抽N张牌。」→ spell_draw（413.1）；j) 「当你打出我时，抽N张牌」→ on_play_draw 触发（337.2）；k) 「我无法造成战斗伤害。」/「我在战斗中最后承担伤害。」→ no_combat_damage / last_damage（465.2.c.2/c.6）。

### P1 关键词接线（7/8；808 绝念暂缓——依附触发注册表入链，记 OPEN）
- 805 急速：可选附加费 [1]+[C]（805.1.a.1 单特性；[A] 任意符能 805.1.a.2；多特性变体暂缓）→ 活跃进场；variants 机制（variants={"accelerate":true}）。
- 807 强攻 / 814 坚守：keyword_values 内嵌 X（807.1.b/814.1.b）；**身份期战力** effective_might(role)（仅攻/防身份计入 807.1.d.1/814.1.d.1），贯通伤害池 465.2.c、致少 465.2.c.4、致死 142.4（combat/cleanup_sys/legal_assign 三处）。
- 809 法盾：强制附加费 [A]×N（809.1.c/356.2.a.2；[A] 任意特性 809.1.c.1；多目标累加 809.2；己方目标豁免 809.1.c），法术打出与技能激活（377）两路接线；pay 系支持 "A" 伪域。
- 816 瞬息：控制者开始阶段计分前摧毁（816.1.b/c；board_only 且未贴附 722.2）；phaser.start_turn 拆段 sub_step="begin_after_triggers"。
- 817 预知→洞察：进场触发看牌堆顶+可选回收（817.1.b/436.1/817.2.a）；SCOUT_KEEP DecisionKind；observation 按 viewer 过滤 options.uids（隐藏信息）；堆空不燃尽（436.4/436.4.a）。
- 822 伏击：位置选项=有己方单位的战场（822.1.b，无视控制归属）+条件授予[反应]（813.4/813.4.a 可能性即可打）；822.3 步骤 5 复核位置；确认期撤销窗口在当前同步结构不可达→已知间隙。
- 附带规则接线：190.3.a.1 打出到非控战场同样令战场进入争夺（enter_permanent 与 movement 同走 CONTEST）。

### X 值语义裁决（消除 ~80 条虚假 ParseConflict）
规则上仅 807/809/814 有「格式为…[X]」的 X 值语义 → `_X_VALUED_KEYWORDS={ASSAULT,DEFLECT,SHIELD}`；回响/装配/强化/流转的数字是**费用**、狩猎/等级的数字是**段位**，不入 keyword_values（各关键词接线时按各自锚点解析）。CN/EN 两面对称收窄后冲突表仅剩 VEN-059（源站 CN 行尾逗号版式瑕疵，EN 互证同一直伤句）→ 句式和并入后 **0 未登记裁决**（已登记 7 条裁决不变）。

### 覆盖与测试
- `reports/card_coverage.md` 幂等再生成：**可执行 147 → 174**（+27，与 §4 聚类 top 候选全覆盖一致）；可加载 1224 / 无文本 83 / 部分支持 967 / 未支持 43 / 歧义阻塞 0。
- 测试 121 → **192 绿**（+71：test_batch2_effects.py 26 集成测试覆盖 15 张真卡全部新机制 + test_effects_parse 解析面扩展 + test_carddb hook 白名单 2→11）。
- 已知间隙（登记待清，均不阻塞阶段 5）：805 多特性急速变体；822.3 确认期撤销窗口；465.2.c.8 壁垒+「最后承担伤害」同体时排斥任选（现按 465.2.c.2/c.6 组序）；383.3.d 同玩家多触发自选序（现 uid 确定序）；817 多实例预知去重为 1 次；授予性关键词的数值载体（keywords_extra 无数值位）。

### 本轮文件（二轮）
src/riftsim/effects.py（d..k 句式 CN/EN 双面 + X 值收窄 + VEN-059 逗号尾变体）；cards.py/state.py（AbilityDef +grant_power_domain/cost_symbols/draw_count，CardDefinition +keyword_values，序列化往返）；carddb.py（compile_hooks 传 is_spell/is_permanent、keyword_values 交叉校验）；resources.py（effective_might(role)、can_pay/pay_cost "A" 伪域）；playing.py（variants 机制、ambush/open locs、目标预检前移、_deflect_charges、enters_ready/accelerated 进场、_push_enter_triggers、apply_card_text 直伤/抽牌、apply_ability_resolution 四新 kind、SCOUT 决策）；combat.py（_side_pool(role)、no_combat_damage 排除、last_damage 组）；cleanup_sys.py（lethal_marked 按身份期战力）；phaser.py（start_turn 拆段 begin_after_triggers）；engine.py（SCOUT_KEEP dispatch、begin_after_triggers 续段）；legality.py（SCOUT_KEEP 合法集）；observation.py（SCOUT_KEEP options.uids 按 viewer 过滤）；tests/test_batch2_effects.py（新 26 测试，15 张真卡）；test_carddb.py（hook 白名单 2→11）；.tmp/probe_ven059*.py（裁决证据留档）。

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
