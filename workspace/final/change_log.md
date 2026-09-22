# Change Log — 规则变更日志

> Stage 6D 产物。由 `stage6d_build_change_log.py` 从 `workspace/rules_work.db` 的 `changes` 表全量幂等重建；事实来源为数据库，任何手工改动会被下次重建覆盖。

- 构建时间: 2026-09-22T18:45:23
- 变更总数: 267（160 个不同规则受影响）
- 说明: original_content 为 NULL 的条目属于新增规则（new_rule_addition），以显式标记呈现，未伪造原始文本；version 为 NULL 的记录以 `-（无版本）` 呈现。

---

## 汇总统计

### 按批次（change tier）

| 批次 | 数量 | 说明 |
| --- | ---: | --- |
| CHG-4B-T2ER | 222 | 勘误（Errata）应用 — 4B-B004 |
| CHG-4B-T1F | 6 | FAQ 内嵌规则变更 — 4B-B005 |
| CHG-4B-T3 | 38 | 核心规则后官方改动 — 4B-B006 |
| CHG-5- | 1 | Stage 5 独立验证修复 |
| **合计** | **267** |  |

### 按 modification_type

| modification_type | 数量 |
| --- | ---: |
| `partial_replacement` | 100 |
| `condition_change` | 59 |
| `terminology_fix` | 40 |
| `new_rule_addition` | 37 |
| `effect_change` | 23 |
| `replacement` | 5 |
| `other` | 2 |
| `numeric_change` | 1 |

### 按来源文档

| 文档 | 数量 |
| --- | ---: |
| `02_2025-12-03_符文战场_勘误汇总_1028.pdf [errata|zh]` | 51 |
| `03_2026-04-15_破限系列_勘误汇总_260403.pdf [errata|zh]` | 47 |
| `02_2025-10-28_Origins_Errata.pdf [errata|en]` | 41 |
| `08_2026-07-17_Vendetta_Patch_Notes.pdf [official_explanation|en]` | 37 |
| `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf [errata|zh]` | 23 |
| `04_2026-01-14_Spiritforged_Errata.pdf [errata|en]` | 21 |
| `10_2026-07-24_9fe1f19110dd4678a6ad7bd96e791bba.pdf [errata|zh]` | 16 |
| `06_2026-04-03_Unleashed_Errata.pdf [errata|en]` | 12 |
| `09_2026-07-23_Vendetta_Errata.pdf [errata|en]` | 11 |
| `07_2026-04-30_破限系列_官方FAQ.pdf [faq|zh]` | 6 |
| `05_2026-04-15_铸魂淬炼系列_官方FAQ_260114.pdf [faq|zh]` | 1 |
| `07_2026-07-16_Core_Rules.pdf [rule|en]` | 1 |

---

## 1. 勘误（Errata）应用 — 4B-B004（222 条）

> 官方勘误的 `corrected_fragment` 按日期升序应用到 R-CARD 规则的 canonical （同一规则多条勘误链式叠加，canonical 取最后一条；EN 对应勘误仅记录不改 canonical）。

### `R-CARD-ARC-001`  —  card:ARC-001 (蔚) — 本规则共 1 条变更

#### CHG-4B-T2ER-ARC-001-EV-CN-ER-0056  —  `R-CARD-ARC-001`  —  card:ARC-001 (蔚)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-ARC-001` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0056 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[游走]（我可以向其他战场进行移动。）
你可以从废牌堆回收一张卡牌，然后让我本回合内战力+1（可重复执行）。
```

**new_content**:

```
[游走]（我可以向其他战场进行移动。）
从你的废牌堆回收一张卡牌：给予我在本回合内[S]+1。
```

### `R-CARD-FND-196`  —  card:FND-196 (提莫) — 本规则共 1 条变更

#### CHG-4B-T2ER-FND-196-EV-CN-ER-0023  —  `R-CARD-FND-196`  —  card:FND-196 (提莫)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-FND-196` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0023 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守一处战场、或从正面朝下的[待命]状态中打出时，展示你主牌堆顶部的五张牌，当中每
有一张带有[待命]技能的卡牌，就对此处的一名敌方单位造成1 点伤害，然后将展示的牌回收。
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守时，选择一名此处的敌方单位，展示你主牌堆顶部的五张牌。当中每有一张带有[待命]
技能的卡牌，便对该单位造成1 点伤害，然后将展示的牌回收。
```

### `R-CARD-FND-259`  —  card:FND-259 (疾风剑豪) — 本规则共 1 条变更

#### CHG-4B-T2ER-FND-259-EV-CN-ER-0028  —  `R-CARD-FND-259`  —  card:FND-259 (疾风剑豪)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-FND-259` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0028 (source_002) applied per Stage 4B; effective_scope=english_card_text_only |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
支付[2]，[E]：在战场和你的基地之间移动一名友方单位。
```

**new_content**:

```
支付[2]，[E]：在战场和其所属基地之间移动一名友方单位。
```

### `R-CARD-OGN-002`  —  card:OGN-002 (Brazen Buccaneer / 粗鲁的海盗) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-002-EV-CN-ER-0059  —  `R-CARD-OGN-002`  —  card:OGN-002 (Brazen Buccaneer / 粗鲁的海盗)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-002` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0059 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
打出我时，你可以选择额外弃置一张手牌以此让我的费用减少[2]。
```

**new_content**:

```
打出我时，你可以选择弃置一张手牌作为额外费用。若如此做，则我的费用减少[2]。
```

### `R-CARD-OGN-005`  —  card:OGN-005 (Disintegrate / 碎裂之火) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-005-EV-CN-ER-0008  —  `R-CARD-OGN-005`  —  card:OGN-005 (Disintegrate / 碎裂之火)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-005` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `effect_change` |
| reason | official errata EV-CN-ER-0008 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[迅捷]（可在你的回合或法术对决中打出。）
对战场上的一名单位造成3 点伤害。如果该单位被此法术摧毁，则抽一张牌。
```

**new_content**:

```
[迅捷]（可在你的回合或法术对决中打出。）
对战场上的一名单位造成3 点伤害。如果该单位被此法术摧毁，则进行一次：抽一张牌。
```

#### CHG-4B-T2ER-OGN-005-EV-EN-ER-0009  —  `R-CARD-OGN-005`  —  card:OGN-005 (Disintegrate / 碎裂之火)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-005` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `effect_change` |
| reason | official errata EV-EN-ER-0009 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Action] (Play on your turn or in showdowns.)
Deal 3 to a unit at a battlefield. If this kills it, draw 1.
```

**new_content**:

```
Action (Play on your turn or in showdowns.)
Deal 3 to a unit at a battlefield. If this kills it, do this: draw 1.
```

### `R-CARD-OGN-023`  —  card:OGN-023 (Unlicensed Armory / 来路不明的武器) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-023-EV-CN-ER-0029  —  `R-CARD-OGN-023`  —  card:OGN-023 (Unlicensed Armory / 来路不明的武器)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-023` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0029 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
弃置一张手牌，[E]：选择一名友方单位。在本回合内，当它下次被摧毁时，你可以选择支付
[C]，改为以休眠状态将其召回。（把该单位送回基地，此行动不算作移动。）
```

**new_content**:

```
弃置一张手牌，[E]：选择一名友方单位。本回合内，当它下次被摧毁时，你可以选择支付[C]，
以此改为移除其所受伤害、让其进入休眠状态、并将其召回。（把该单位送回基地，此行动不算
作移动。）
```

#### CHG-4B-T2ER-OGN-023-EV-EN-ER-0030  —  `R-CARD-OGN-023`  —  card:OGN-023 (Unlicensed Armory / 来路不明的武器)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-023` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0030 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
Discard 1, [E]: Choose a friendly unit. The next time it dies this turn, you may pay [C]
to recall it exhausted instead. (Send it to base. This isn't a move.)
```

**new_content**:

```
Discard 1, [E]: Choose a friendly unit. The next time it would die this turn, you may
pay [C] to heal it, exhaust it, and recall it instead. (Send it to base. This isn't a move.)
```

### `R-CARD-OGN-025`  —  card:OGN-025 (Blind Fury / 暴怒冲动) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-025-EV-CN-ER-0003  —  `R-CARD-OGN-025`  —  card:OGN-025 (Blind Fury / 暴怒冲动)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-025` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0003 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[迅捷]（可在你的回合或法术对决中打出。）
每名对手展示其主牌堆顶部的一张牌。你从中选择一张，并当作自己的牌打出，无视费用，然后
回收其余的卡牌。
```

**new_content**:

```
[迅捷]（可在你的回合或法术对决中打出。）
每名对手展示其主牌堆顶部的一张牌。你从中选择一张，将其放逐，然后当作自己的牌打出，无
视费用。然后回收其余的卡牌。
```

#### CHG-4B-T2ER-OGN-025-EV-EN-ER-0004  —  `R-CARD-OGN-025`  —  card:OGN-025 (Blind Fury / 暴怒冲动)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-025` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0004 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Action] (Play on your turn or in showdowns.)
Each opponent reveals the top card of their Main Deck. Choose one and play it,
ignoring its cost. Then recycle the rest.
```

**new_content**:

```
[Action] (Play on your turn or in showdowns.)
Each opponent reveals the top card of their Main Deck. Choose one and banish it,
then play it, ignoring its cost. Then recycle the rest.
```

### `R-CARD-OGN-029`  —  card:OGN-029 (Falling Star / 星落) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-029-EV-CN-ER-0063  —  `R-CARD-OGN-029`  —  card:OGN-029 (Falling Star / 星落)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-029` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `replacement` |
| reason | official errata EV-CN-ER-0063 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
进行两次：
对一名单位造成3 点伤害。（可以选择不同的单位。）
```

**new_content**:

```
对一名单位造成3 点伤害。
对一名单位造成3 点伤害。
```

#### CHG-4B-T2ER-OGN-029-EV-EN-ER-0033  —  `R-CARD-OGN-029`  —  card:OGN-029 (Falling Star / 星落)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-029` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `replacement` |
| reason | official errata EV-EN-ER-0033 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
Do this twice:
Deal 3 to a unit. (You can choose different units.)
```

**new_content**:

```
Deal 3 to a unit.
Deal 3 to a unit.
```

### `R-CARD-OGN-032`  —  card:OGN-032 (Ravenborn Tome / 邪鸦魔典) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-032-EV-CN-ER-0018  —  `R-CARD-OGN-032`  —  card:OGN-032 (Ravenborn Tome / 邪鸦魔典)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-032` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0018 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[E]:你打出的下一个法术造成的伤害+1（每段伤害都+1）。
```

**new_content**:

```
[E]:本回合内你打出的下一个法术造成的伤害+1（每段伤害都+1）。
```

#### CHG-4B-T2ER-OGN-032-EV-EN-ER-0019  —  `R-CARD-OGN-032`  —  card:OGN-032 (Ravenborn Tome / 邪鸦魔典)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-032` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0019 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[E]: The next spell you play deals 1 Bonus Damage. (Each instance of damage the
spell deals is increased by 1.)
```

**new_content**:

```
[E]: The next spell you play this turn deals 1 Bonus Damage. (Each instance of
damage the spell deals is increased by 1.)
```

### `R-CARD-OGN-036`  —  card:OGN-036 (Vi, Destructive / 蔚) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-036-EV-CN-ER-0056  —  `R-CARD-OGN-036`  —  card:OGN-036 (Vi, Destructive / 蔚)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-036` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0056 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[游走]（我可以向其他战场进行移动。）
你可以从废牌堆回收一张卡牌，然后让我本回合内战力+1（可重复执行）。
```

**new_content**:

```
[游走]（我可以向其他战场进行移动。）
从你的废牌堆回收一张卡牌：给予我在本回合内[S]+1。
```

### `R-CARD-OGN-044`  —  card:OGN-044 (Clockwork Keeper / 小小守护者) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-044-EV-CN-ER-0004  —  `R-CARD-OGN-044`  —  card:OGN-044 (Clockwork Keeper / 小小守护者)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-044` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `replacement` |
| reason | official errata EV-CN-ER-0004 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
打出我时，你可以选择额外支付[C]来抽一张牌。
```

**new_content**:

```
你可以选择支付[C]，作为打出我的额外费用。
当你打出我时，如果你支付了该额外费用，则抽一张牌。
```

#### CHG-4B-T2ER-OGN-044-EV-EN-ER-0005  —  `R-CARD-OGN-044`  —  card:OGN-044 (Clockwork Keeper / 小小守护者)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-044` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0005 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
As you play me, you may pay [C] as an additional cost. If you do, draw 1.
```

**new_content**:

```
You may pay [C] as an additional cost to play me.
When you play me, if you paid the additional cost, draw 1.
```

### `R-CARD-OGN-048`  —  card:OGN-048 (Meditation / 冥想) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-048-EV-CN-ER-0060  —  `R-CARD-OGN-048`  —  card:OGN-048 (Meditation / 冥想)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-048` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0060 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[反应]（可在任意时机打出，甚至先于其他法术和技能的结算。）
抽一张牌。你可以选择让一名友方单位变为休眠状态作为额外费用，以此再抽一张牌。
```

**new_content**:

```
[反应]（可在任意时机打出，甚至先于其他法术和技能的结算。）
你可以选择让一名友方单位变为休眠状态作为额外费用。若如此做，则抽两张牌。否则，抽一张
牌。
```

### `R-CARD-OGN-056`  —  card:OGN-056 (Adaptatron / 自适应机器人) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-056-EV-CN-ER-0058  —  `R-CARD-OGN-056`  —  card:OGN-056 (Adaptatron / 自适应机器人)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-056` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0058 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当我征服一处战场时，你可以选择摧毁一件装备，以此给予我增益。（如果我未拥有增益则获得
一个战力+1 增益。）
```

**new_content**:

```
当我征服一处战场时，你可以选择摧毁一件装备。若如此做，则给予我增益。（如果我未拥有增
益，则获得一个[S]+1 增益。）
```

### `R-CARD-OGN-062`  —  card:OGN-062 (Reinforce / 增援) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-062-EV-CN-ER-0065  —  `R-CARD-OGN-062`  —  card:OGN-062 (Reinforce / 增援)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-062` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0065 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
查看你主牌堆顶部的五张牌。你可以从中选择一名单位，将它的法力费用减少[5]后打出，然后回
收其余卡牌。
```

**new_content**:

```
查看你主牌堆顶部的五张牌。你可以选择从中放逐一名单位，然后将其打出，其费用减少[5]。回
收其余的卡牌。
```

#### CHG-4B-T2ER-OGN-062-EV-EN-ER-0035  —  `R-CARD-OGN-062`  —  card:OGN-062 (Reinforce / 增援)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-062` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0035 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
Look at the top 5 cards of your Main Deck. You may play a unit from among them.
Its Energy cost is reduced by [5]. Then recycle the remaining cards.
```

**new_content**:

```
Look at the top 5 cards of your Main Deck. You may banish a unit from among
them, then play it, reducing its cost by [5]. Recycle the remaining cards.
```

### `R-CARD-OGN-073`  —  card:OGN-073 (Sona, Harmonious / 娑娜) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-073-EV-CN-ER-0021  —  `R-CARD-OGN-073`  —  card:OGN-073 (Sona, Harmonious / 娑娜)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-073` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0021 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
在你的回合结束时，如果我位于战场上，则让四枚友方符文变为活跃状态。
```

**new_content**:

```
在你的回合结束时，如果我位于战场上，则让最多四枚友方符文变为活跃状态。
```

#### CHG-4B-T2ER-OGN-073-EV-EN-ER-0022  —  `R-CARD-OGN-073`  —  card:OGN-073 (Sona, Harmonious / 娑娜)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-073` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0022 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
While I'm at a battlefield, ready 4 friendly runes at the end of your turn.
```

**new_content**:

```
At the end of your turn, if I'm at a battlefield, ready up to 4 friendly runes.
```

### `R-CARD-OGN-077`  —  card:OGN-077 (Zhonya's Hourglass / 中娅沙漏) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-077-EV-CN-ER-0031  —  `R-CARD-OGN-077`  —  card:OGN-077 (Zhonya's Hourglass / 中娅沙漏)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-077` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0031 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
下一次当友方单位被摧毁时，改为将此牌摧毁，然后以休眠状态将该单位召回。（把该单位送回
基地，此行动不算作移动。）
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
如果一名友方单位被摧毁，则改为将此牌摧毁。移除该单位所受伤害，让其进入休眠状态，并将
其召回。（把该单位送回基地，此行动不算作移动。）
```

#### CHG-4B-T2ER-OGN-077-EV-EN-ER-0032  —  `R-CARD-OGN-077`  —  card:OGN-077 (Zhonya's Hourglass / 中娅沙漏)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-077` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0032 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
The next time a friendly unit would die, kill this instead. Recall that unit exhausted.
(Send it to base. This isn't a move.)
```

**new_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
If a friendly unit would die, kill this instead. Heal that unit, exhaust it, and recall it.
(Send it to base. This isn't a move.)
```

### `R-CARD-OGN-102`  —  card:OGN-102 (Portal Rescue / 传送门大营救) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-102-EV-CN-ER-0016  —  `R-CARD-OGN-102`  —  card:OGN-102 (Portal Rescue / 传送门大营救)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-102` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0016 (source_002) applied per Stage 4B; effective_scope=english_card_text_only |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[迅捷]（可在你的回合或法术对决中打出。）
放逐一名友方单位，然后将其打出到基地，无视费用。
```

**new_content**:

```
[迅捷]（可在你的回合或法术对决中打出。）
放逐一名友方单位，然后让其拥有者将它打出到其所属的基地，无视费用。
```

#### CHG-4B-T2ER-OGN-102-EV-EN-ER-0017  —  `R-CARD-OGN-102`  —  card:OGN-102 (Portal Rescue / 传送门大营救)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-102` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0017 (source_013) applied per Stage 4B; effective_scope=english_card_text_only |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Action] (Play on your turn or in showdowns.)
Banish a friendly unit, then play it to base, ignoring its cost.
```

**new_content**:

```
[Action] (Play on your turn or in showdowns.)
Banish a friendly unit, then its owner plays it to their base, ignoring its cost.
```

### `R-CARD-OGN-107`  —  card:OGN-107 (Ava Achiever / 斥候标兵 艾娃) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-107-EV-CN-ER-0001  —  `R-CARD-OGN-107`  —  card:OGN-107 (Ava Achiever / 斥候标兵 艾娃)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-107` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0001 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当我进攻时，你可以选择支付[C]，以此从你的手牌中正面朝上打出一张带有[待命]技能的卡牌，
无视费用。
```

**new_content**:

```
当我进攻时，你可以选择支付[C]，以此从你的手牌中正面朝上打出一张带有[待命]技能的卡牌，
无视费用。如果其为单位，则将其打出到此处。
```

#### CHG-4B-T2ER-OGN-107-EV-EN-ER-0002  —  `R-CARD-OGN-107`  —  card:OGN-107 (Ava Achiever / 斥候标兵 艾娃)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-107` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0002 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When I attack, you may pay [C] to play a card with [Hidden] from your hand here,
ignoring its cost.
```

**new_content**:

```
When I attack, you may pay [C] to play a card with [Hidden] from your hand,
ignoring its cost. If it’s a unit, play it here.
```

### `R-CARD-OGN-108`  —  card:OGN-108 (Convergent Mutation / 聚合变异) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-108-EV-CN-ER-0005  —  `R-CARD-OGN-108`  —  card:OGN-108 (Convergent Mutation / 聚合变异)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-108` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0005 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[反应]（可在任意时机打出，甚至先于其他法术和技能的结算。）
选择一名友方单位。如果其战力低于另一名友方单位，则让其在本回合内变为后者的战力。
```

**new_content**:

```
[反应]（可在任意时机打出，甚至先于其他法术和技能的结算。）
选择一名友方单位。本回合内，将其战力提升至与另一名友方单位战力相同。
```

#### CHG-4B-T2ER-OGN-108-EV-EN-ER-0006  —  `R-CARD-OGN-108`  —  card:OGN-108 (Convergent Mutation / 聚合变异)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-108` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0006 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Reaction] (Play any time, even before spells and abilities resolve.)
Choose a friendly unit. Increase its Might until it equals the Might of another
friendly unit.
```

**new_content**:

```
[Reaction] (Play any time, even before spells and abilities resolve.)
Choose a friendly unit. This turn, increase its Might to the Might of another friendly
unit.
```

### `R-CARD-OGN-115`  —  card:OGN-115 (Promising Future / 光明未来) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-115-EV-CN-ER-0017  —  `R-CARD-OGN-115`  —  card:OGN-115 (Promising Future / 光明未来)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-115` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0017 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
每名玩家可以查看主牌堆顶部的五张牌，从中选择一张，然后回收其余的卡牌。从下一名玩家开
始，每名玩家打出这些卡牌，无视其法力费用。（仍需支付所有符能费用。）
```

**new_content**:

```
每名玩家查看其主牌堆顶部的五张牌，放逐其中一张，然后回收其余的卡牌。从下一名玩家开
始，每名玩家打出这些被放逐的卡牌，无视其法力费用。（仍需支付所有符能费用。）
```

#### CHG-4B-T2ER-OGN-115-EV-EN-ER-0018  —  `R-CARD-OGN-115`  —  card:OGN-115 (Promising Future / 光明未来)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-115` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0018 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
Each player looks at the top 5 cards of their Main Deck, chooses one, then recycles
the rest. Starting with the next player, each player plays those cards, ignoring
Energy costs. (They must still pay Power costs.)
```

**new_content**:

```
Each player looks at the top 5 cards of their Main Deck, banishes one of them, then
recycles the rest. Starting with the next player, each player plays those cards,
ignoring Energy costs. (They must still pay Power costs.)
```

### `R-CARD-OGN-121`  —  card:OGN-121 (Teemo, Strategist / 提莫) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-121-EV-CN-ER-0023  —  `R-CARD-OGN-121`  —  card:OGN-121 (Teemo, Strategist / 提莫)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-121` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0023 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守一处战场、或从正面朝下的[待命]状态中打出时，展示你主牌堆顶部的五张牌，当中每
有一张带有[待命]技能的卡牌，就对此处的一名敌方单位造成1 点伤害，然后将展示的牌回收。
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守时，选择一名此处的敌方单位，展示你主牌堆顶部的五张牌。当中每有一张带有[待命]
技能的卡牌，便对该单位造成1 点伤害，然后将展示的牌回收。
```

#### CHG-4B-T2ER-OGN-121-EV-EN-ER-0024  —  `R-CARD-OGN-121`  —  card:OGN-121 (Teemo, Strategist / 提莫)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-121` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0024 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
When I defend or I'm played from [Hidden], reveal the top 5 cards of your Main
Deck. Deal 1 to an enemy unit here for each card with [Hidden], then recycle them.
```

**new_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
When I defend, choose an enemy unit here and reveal the top 5 cards of your Main
Deck. Deal 1 to that unit for each card with [Hidden] revealed this way, then recycle
the revealed cards.
```

### `R-CARD-OGN-121a`  —  card:OGN-121a (Teemo, Strategist / 提莫) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-121a-EV-CN-ER-0023  —  `R-CARD-OGN-121a`  —  card:OGN-121a (Teemo, Strategist / 提莫)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-121a` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0023 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守一处战场、或从正面朝下的[待命]状态中打出时，展示你主牌堆顶部的五张牌，当中每
有一张带有[待命]技能的卡牌，就对此处的一名敌方单位造成1 点伤害，然后将展示的牌回收。
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守时，选择一名此处的敌方单位，展示你主牌堆顶部的五张牌。当中每有一张带有[待命]
技能的卡牌，便对该单位造成1 点伤害，然后将展示的牌回收。
```

#### CHG-4B-T2ER-OGN-121a-EV-EN-ER-0024  —  `R-CARD-OGN-121a`  —  card:OGN-121a (Teemo, Strategist / 提莫)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-121a` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0024 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
When I defend or I'm played from [Hidden], reveal the top 5 cards of your Main
Deck. Deal 1 to an enemy unit here for each card with [Hidden], then recycle them.
```

**new_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
When I defend, choose an enemy unit here and reveal the top 5 cards of your Main
Deck. Deal 1 to that unit for each card with [Hidden] revealed this way, then recycle
the revealed cards.
```

### `R-CARD-OGN-122`  —  card:OGN-122 (Time Warp / 时间扭曲) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-122-EV-CN-ER-0089  —  `R-CARD-OGN-122`  —  card:OGN-122 (Time Warp / 时间扭曲)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-122` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `10_2026-07-24_9fe1f19110dd4678a6ad7bd96e791bba.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0089 (source_010) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
在当前回合结束后，再进行一个回合，然后放逐此牌。
```

**new_content**:

```
在本回合后再进行一个回合。放逐此牌。
```

### `R-CARD-OGN-131`  —  card:OGN-131 (Dune Drake / 沙丘亚龙) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-131-EV-CN-ER-0010  —  `R-CARD-OGN-131`  —  card:OGN-131 (Dune Drake / 沙丘亚龙)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-131` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0010 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当我进攻时，如果此处有处于活跃状态的敌方单位，则让我[M]+2。
```

**new_content**:

```
当我进攻时，如果此处有处于活跃状态的敌方单位，则让我在本回合内[M]+2。
```

#### CHG-4B-T2ER-OGN-131-EV-EN-ER-0011  —  `R-CARD-OGN-131`  —  card:OGN-131 (Dune Drake / 沙丘亚龙)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-131` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0011 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When I attack, give me +2 [M] if there is a ready enemy unit here.
```

**new_content**:

```
When I attack, give me +2 [M] this turn if there is a ready enemy unit here.
```

### `R-CARD-OGN-141`  —  card:OGN-141 (Kinkou Monk / 均衡僧侣) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-141-EV-CN-ER-0013  —  `R-CARD-OGN-141`  —  card:OGN-141 (Kinkou Monk / 均衡僧侣)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-141` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0013 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你打出我时，给予其他两名友方单位增益。（每名未拥有增益的单位获得一个[M]+1 增益。）
```

**new_content**:

```
当你打出我时，给予最多两名其他友方单位增益。（每名未拥有增益的单位获得一个[M]+1 增
益。）
```

#### CHG-4B-T2ER-OGN-141-EV-EN-ER-0014  —  `R-CARD-OGN-141`  —  card:OGN-141 (Kinkou Monk / 均衡僧侣)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-141` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0014 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When you play me, buff two other friendly units. (Each one that doesn't have a buff
gets a +1 [M] buff.)
```

**new_content**:

```
When you play me, buff up to two other friendly units. (Each one that doesn't have
a buff gets a +1 [M] buff.)
```

### `R-CARD-OGN-146`  —  card:OGN-146 (Wallop / 痛殴) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-146-EV-CN-ER-0061  —  `R-CARD-OGN-146`  —  card:OGN-146 (Wallop / 痛殴)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-146` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0061 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[迅捷]（可在你的回合或法术对决中打出。）
当你打出此牌时，你可以选择消耗一个增益作为额外费用，以此无视此法术的费用。让一名单位
变为活跃状态。
```

**new_content**:

```
[迅捷]（可在你的回合或法术对决中打出。）
打出此牌时，你可以选择消耗一个增益作为额外费用。若如此做，则无视此法术的费用。
让一名单位变为活跃状态。
```

### `R-CARD-OGN-160`  —  card:OGN-160 (Dazzling Aurora / 闪耀极光) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-160-EV-CN-ER-0007  —  `R-CARD-OGN-160`  —  card:OGN-160 (Dazzling Aurora / 闪耀极光)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-160` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0007 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
在你的回合即将结束时，从主牌堆顶部开始逐一展示卡牌，直到翻出一名单位为止，然后将其打
出，无视费用，并回收其余的卡牌。
```

**new_content**:

```
在你的回合结束时，从主牌堆顶部开始逐一展示卡牌，直到翻出一名单位为止，将其放逐，然后
将其打出，无视费用，并回收其余的卡牌。
```

#### CHG-4B-T2ER-OGN-160-EV-EN-ER-0008  —  `R-CARD-OGN-160`  —  card:OGN-160 (Dazzling Aurora / 闪耀极光)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-160` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0008 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
At the end of your turn, reveal cards from the top of your Main Deck until you reveal
a unit. Play it, ignoring its cost, and recycle the rest.
```

**new_content**:

```
At the end of your turn, reveal cards from the top of your Main Deck until you reveal
a unit and banish it. Play it, ignoring its cost, and recycle the rest.
```

### `R-CARD-OGN-181`  —  card:OGN-181 (Pack of Wonders / 奇妙行囊) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-181-EV-CN-ER-0015  —  `R-CARD-OGN-181`  —  card:OGN-181 (Pack of Wonders / 奇妙行囊)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-181` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0015 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[E]:让另一张友方装备、单位或[待命]卡牌返回其所属的手牌。
```

**new_content**:

```
[E]:让另一张友方装备、单位或正面朝下的卡牌返回其所属的手牌。
```

#### CHG-4B-T2ER-OGN-181-EV-EN-ER-0016  —  `R-CARD-OGN-181`  —  card:OGN-181 (Pack of Wonders / 奇妙行囊)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-181` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0016 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[E]: Return another friendly gear, unit, or [Hidden] card to its owner's hand.
```

**new_content**:

```
[E]: Return another friendly gear, unit, or facedown card to its owner's hand.
```

### `R-CARD-OGN-184`  —  card:OGN-184 (The Syren / 塞壬号) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-184-EV-CN-ER-0026  —  `R-CARD-OGN-184`  —  card:OGN-184 (The Syren / 塞壬号)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-184` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0026 (source_002) applied per Stage 4B; effective_scope=english_card_text_only |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
支付[1]，[E]：将战场上的一名友方单位移动到你的基地。
```

**new_content**:

```
支付[1]，[E]：将战场上的一名友方单位移动到其所属的基地。
```

#### CHG-4B-T2ER-OGN-184-EV-EN-ER-0027  —  `R-CARD-OGN-184`  —  card:OGN-184 (The Syren / 塞壬号)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-184` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0027 (source_013) applied per Stage 4B; effective_scope=english_card_text_only |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[1], [E]: Move a friendly unit at a battlefield to your base.
```

**new_content**:

```
[1], [E]: Move a friendly unit at a battlefield to its base.
```

### `R-CARD-OGN-193`  —  card:OGN-193 (Miss Fortune, Buccaneer / 厄运小姐) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-193-EV-CN-ER-0046  —  `R-CARD-OGN-193`  —  card:OGN-193 (Miss Fortune, Buccaneer / 厄运小姐)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-193` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0046 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
你可以选择将我打出到一处开放的战场。
当我在场上时,你可以选择将友方单位打出到一处开放的战场。
```

**new_content**:

```
你可以选择将我打出到一处开放的战场。
友方单位可以被打出到开放的战场。
```

### `R-CARD-OGN-193a`  —  card:OGN-193a (Miss Fortune, Buccaneer / 厄运小姐) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-193a-EV-CN-ER-0046  —  `R-CARD-OGN-193a`  —  card:OGN-193a (Miss Fortune, Buccaneer / 厄运小姐)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-193a` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0046 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
你可以选择将我打出到一处开放的战场。
当我在场上时,你可以选择将友方单位打出到一处开放的战场。
```

**new_content**:

```
你可以选择将我打出到一处开放的战场。
友方单位可以被打出到开放的战场。
```

### `R-CARD-OGN-193b`  —  card:OGN-193b (厄运小姐) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-193b-EV-CN-ER-0046  —  `R-CARD-OGN-193b`  —  card:OGN-193b (厄运小姐)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-193b` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0046 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
你可以选择将我打出到一处开放的战场。
当我在场上时,你可以选择将友方单位打出到一处开放的战场。
```

**new_content**:

```
你可以选择将我打出到一处开放的战场。
友方单位可以被打出到开放的战场。
```

### `R-CARD-OGN-194`  —  card:OGN-194 (Nocturne, Horrifying / 魔腾) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-194-EV-CN-ER-0014  —  `R-CARD-OGN-194`  —  card:OGN-194 (Nocturne, Horrifying / 魔腾)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-194` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0014 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[游走]（我可以向其他战场进行移动。）
当你查看主牌堆顶部的卡牌（不是抽牌）并看到我时，可以支付[A]将我打出。
```

**new_content**:

```
[游走]（我可以向其他战场进行移动。）
你查看或展示主牌堆顶部的卡牌并看到我时，可以选择将我放逐。如选择放逐，则你可以选择支
付[A]将我打出。
```

#### CHG-4B-T2ER-OGN-194-EV-EN-ER-0015  —  `R-CARD-OGN-194`  —  card:OGN-194 (Nocturne, Horrifying / 魔腾)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-194` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0015 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Ganking] (I can move from battlefield to battlefield.)
When you look at cards from the top of your deck (and don't draw them) and see
me, you may play me for [A].
```

**new_content**:

```
[Ganking] (I can move from battlefield to battlefield.)
As you look at or reveal me from the top of your deck, you may banish me. If you do,
you may play me for [A].
```

### `R-CARD-OGN-196`  —  card:OGN-196 (Soulgorger / 咂魂者) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-196-EV-CN-ER-0057  —  `R-CARD-OGN-196`  —  card:OGN-196 (Soulgorger / 咂魂者)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-196` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0057 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你打出我时，你可以选择从废牌堆中打出一名单位，无视其法力费用（仍需支付所有符能费
用）。
```

**new_content**:

```
当你打出我时，你可以选择从你的废牌堆中打出一名单位，无视其法力费用（仍需支付所有符能
费用）。
```

### `R-CARD-OGN-197`  —  card:OGN-197 (Teemo, Scout / 提莫) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-197-EV-CN-ER-0023  —  `R-CARD-OGN-197`  —  card:OGN-197 (Teemo, Scout / 提莫)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-197` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0023 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守一处战场、或从正面朝下的[待命]状态中打出时，展示你主牌堆顶部的五张牌，当中每
有一张带有[待命]技能的卡牌，就对此处的一名敌方单位造成1 点伤害，然后将展示的牌回收。
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守时，选择一名此处的敌方单位，展示你主牌堆顶部的五张牌。当中每有一张带有[待命]
技能的卡牌，便对该单位造成1 点伤害，然后将展示的牌回收。
```

### `R-CARD-OGN-197a`  —  card:OGN-197a (Teemo, Scout / 提莫) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-197a-EV-CN-ER-0023  —  `R-CARD-OGN-197a`  —  card:OGN-197a (Teemo, Scout / 提莫)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-197a` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0023 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守一处战场、或从正面朝下的[待命]状态中打出时，展示你主牌堆顶部的五张牌，当中每
有一张带有[待命]技能的卡牌，就对此处的一名敌方单位造成1 点伤害，然后将展示的牌回收。
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守时，选择一名此处的敌方单位，展示你主牌堆顶部的五张牌。当中每有一张带有[待命]
技能的卡牌，便对该单位造成1 点伤害，然后将展示的牌回收。
```

### `R-CARD-OGN-197b`  —  card:OGN-197b (提莫) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-197b-EV-CN-ER-0023  —  `R-CARD-OGN-197b`  —  card:OGN-197b (提莫)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-197b` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0023 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守一处战场、或从正面朝下的[待命]状态中打出时，展示你主牌堆顶部的五张牌，当中每
有一张带有[待命]技能的卡牌，就对此处的一名敌方单位造成1 点伤害，然后将展示的牌回收。
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守时，选择一名此处的敌方单位，展示你主牌堆顶部的五张牌。当中每有一张带有[待命]
技能的卡牌，便对该单位造成1 点伤害，然后将展示的牌回收。
```

### `R-CARD-OGN-199`  —  card:OGN-199 (Tideturner / 控潮者) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-199-EV-CN-ER-0027  —  `R-CARD-OGN-199`  —  card:OGN-199 (Tideturner / 控潮者)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-199` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0027 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当你打出我时，你可以选择受你控制的一名单位，然后把我移动到其所在位置，再将其移动到我
原来的位置。
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当你打出我时，你可以选择一名在其他位置受你控制的单位。把我移动到其所在位置，将其移动
到我原来的位置。
```

#### CHG-4B-T2ER-OGN-199-EV-EN-ER-0028  —  `R-CARD-OGN-199`  —  card:OGN-199 (Tideturner / 控潮者)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-199` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0028 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
When you play me, you may choose a friendly unit. Move me to its location and it to
my original location.
```

**new_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
When you play me, you may choose a unit you control at another location. Move me
to its location and it to my original location.
```

### `R-CARD-OGN-207`  —  card:OGN-207 (Call to Glory / 荣耀召唤) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-207-EV-CN-ER-0062  —  `R-CARD-OGN-207`  —  card:OGN-207 (Call to Glory / 荣耀召唤)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-207` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0062 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[反应]（可在任意时机打出，甚至先于其他法术和技能的结算。）
打出此牌时，你可以选择消耗一个增益作为额外费用，以此无视本法术的费用。让一名单位本回
合内战力+3。
```

**new_content**:

```
[反应]（可在任意时机打出，甚至先于其他法术和技能的结算。）
打出此牌时，你可以选择消耗一个增益作为额外费用。若如此做，则无视此法术的费用。
给予一名单位在本回合内[S]+3。
```

### `R-CARD-OGN-224`  —  card:OGN-224 (Salvage / 废物利用) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-224-EV-CN-ER-0019  —  `R-CARD-OGN-224`  —  card:OGN-224 (Salvage / 废物利用)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-224` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0019 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[迅捷]（可在你的回合或法术对决中打出。）
你可以选择摧毁一件装备，然后抽一张牌。
```

**new_content**:

```
[迅捷]（可在你的回合或法术对决中打出。）
你可以选择摧毁最多一件装备。抽一张牌。
```

#### CHG-4B-T2ER-OGN-224-EV-EN-ER-0020  —  `R-CARD-OGN-224`  —  card:OGN-224 (Salvage / 废物利用)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-224` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0020 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Action] (Play on your turn or in showdowns.)
You may kill a gear. Draw 1.
```

**new_content**:

```
[Action] (Play on your turn or in showdowns.)
You may kill up to one gear. Draw 1.
```

### `R-CARD-OGN-235`  —  card:OGN-235 (Karma, Channeler / 卡尔玛) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-235-EV-CN-ER-0012  —  `R-CARD-OGN-235`  —  card:OGN-235 (Karma, Channeler / 卡尔玛)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-235` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0012 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[预知]（当你打出我时，查看主牌堆顶部的一张牌，你可以选择将其回收。）
每当你回收任意数量的卡牌时，给予一名友方单位增益。（如果该单位未拥有增益，则获得一个
[M]+1 增益。符文不被视为卡牌。）
```

**new_content**:

```
[预知]（当你打出我时，查看主牌堆顶部的一张牌，你可以选择将其回收。）
每当你将任意数量的卡牌回收到自己的主牌堆时，给予一名友方单位增益。（如果该单位未拥有
增益，则获得一个[M]+1 增益。符文不被视为卡牌。）
```

#### CHG-4B-T2ER-OGN-235-EV-EN-ER-0013  —  `R-CARD-OGN-235`  —  card:OGN-235 (Karma, Channeler / 卡尔玛)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-235` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0013 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Vision] (When you play me, look at the top card of your Main Deck. You may recycle
it.)
When you recycle one or more cards, buff a friendly unit. (If it doesn't have a buff, it
gets a +1 [M] buff. Runes aren't cards.)
```

**new_content**:

```
[Vision] (When you play me, look at the top card of your Main Deck. You may recycle
it.)
When you recycle one or more cards to your Main Deck, buff a friendly unit. (If it
doesn't have a buff, it gets a +1 [M] buff. Runes aren't cards.)
```

### `R-CARD-OGN-236`  —  card:OGN-236 (Karthus, Eternal / 卡尔萨斯) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-236-EV-CN-ER-0045  —  `R-CARD-OGN-236`  —  card:OGN-236 (Karthus, Eternal / 卡尔萨斯)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-236` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0045 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
你的所有[绝念]效果可以额外触发一次。
```

**new_content**:

```
你的所有[绝念]效果额外触发一次。
```

### `R-CARD-OGN-242`  —  card:OGN-242 (Baited Hook / 海兽钓钩) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-242-EV-CN-ER-0002  —  `R-CARD-OGN-242`  —  card:OGN-242 (Baited Hook / 海兽钓钩)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-242` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0002 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
支付[1][C]，[E]：摧毁一名友方单位，然后查看主牌堆顶部的五张牌。你可以选择从中打出一名
战力比被摧毁单位最多高1 点的单位卡牌，无视费用，然后回收其余的卡牌。
```

**new_content**:

```
支付[1][C]，[E]：摧毁一名友方单位。查看你主牌堆顶部的五张牌。你可以选择从中放逐一名战
力比被摧毁单位最多高1 点的单位卡牌，然后将其打出，无视费用。然后回收其余的卡牌。
```

#### CHG-4B-T2ER-OGN-242-EV-EN-ER-0003  —  `R-CARD-OGN-242`  —  card:OGN-242 (Baited Hook / 海兽钓钩)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-242` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0003 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[1][C], [E]: Kill a friendly unit. Look at the top 5 cards of your Main Deck. You may play
a unit from among them that has Might up to 1 more than the killed unit, ignoring
its cost. Then recycle the rest.
```

**new_content**:

```
[1][C], [E]: Kill a friendly unit. Look at the top 5 cards of your Main Deck. You may
banish a unit from among them that has Might up to 1 more than the killed unit
and play it, ignoring its cost. Then recycle the rest.
```

### `R-CARD-OGN-244`  —  card:OGN-244 (Divine Judgment / 圣裁之刻) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-244-EV-CN-ER-0043  —  `R-CARD-OGN-244`  —  card:OGN-244 (Divine Judgment / 圣裁之刻)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-244` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0043 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
每名玩家分别选择自己的两名单位、两件装备、两枚符文和两张手牌留在原位，然后回收其余卡
牌。
```

**new_content**:

```
每名玩家分别选择两名单位、两件装备、两枚符文和自己的两张手牌。回收其余的单位、装备、
符文和手牌。
```

### `R-CARD-OGN-248`  —  card:OGN-248 (Icathian Rain / 艾卡西亚暴雨) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-248-EV-CN-ER-0064  —  `R-CARD-OGN-248`  —  card:OGN-248 (Icathian Rain / 艾卡西亚暴雨)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-248` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `replacement` |
| reason | official errata EV-CN-ER-0064 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
进行六次：
对一名单位造成2 点伤害。（可以选择不同的单位。）
```

**new_content**:

```
对一名单位造成2 点伤害。
对一名单位造成2 点伤害。
对一名单位造成2 点伤害。
对一名单位造成2 点伤害。
对一名单位造成2 点伤害。
对一名单位造成2 点伤害。
```

#### CHG-4B-T2ER-OGN-248-EV-EN-ER-0034  —  `R-CARD-OGN-248`  —  card:OGN-248 (Icathian Rain / 艾卡西亚暴雨)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-248` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `replacement` |
| reason | official errata EV-EN-ER-0034 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
Do this 6 times:
Deal 2 to a unit. (You can choose different units.)
```

**new_content**:

```
Deal 2 to a unit.
Deal 2 to a unit.
Deal 2 to a unit.
Deal 2 to a unit.
Deal 2 to a unit.
Deal 2 to a unit.
```

### `R-CARD-OGN-258`  —  card:OGN-258 (Dragon's Rage / 猛龙摆尾) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-258-EV-CN-ER-0009  —  `R-CARD-OGN-258`  —  card:OGN-258 (Dragon's Rage / 猛龙摆尾)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-258` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `effect_change` |
| reason | official errata EV-CN-ER-0009 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
移动一名敌方单位。然后，在其目的地处选择另一名敌方单位，让这两名单位相互以自身战力给
对方造成伤害。
```

**new_content**:

```
移动一名敌方单位。然后进行一次：在该单位终点位置处选择另一名敌方单位。让这两名单位相
互以自身战力给对方造成伤害。
```

#### CHG-4B-T2ER-OGN-258-EV-EN-ER-0010  —  `R-CARD-OGN-258`  —  card:OGN-258 (Dragon's Rage / 猛龙摆尾)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-258` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `effect_change` |
| reason | official errata EV-EN-ER-0010 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
Move an enemy unit. Then choose another enemy unit at its destination. They deal
damage equal to their Mights to each other.
```

**new_content**:

```
Move an enemy unit. Then do this: Choose another enemy unit at its destination.
They deal damage equal to their Mights to each other.
```

### `R-CARD-OGN-259`  —  card:OGN-259 (Unforgiven / 疾风剑豪) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-259-EV-CN-ER-0028  —  `R-CARD-OGN-259`  —  card:OGN-259 (Unforgiven / 疾风剑豪)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-259` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0028 (source_002) applied per Stage 4B; effective_scope=english_card_text_only |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
支付[2]，[E]：在战场和你的基地之间移动一名友方单位。
```

**new_content**:

```
支付[2]，[E]：在战场和其所属基地之间移动一名友方单位。
```

#### CHG-4B-T2ER-OGN-259-EV-EN-ER-0029  —  `R-CARD-OGN-259`  —  card:OGN-259 (Unforgiven / 疾风剑豪)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-259` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0029 (source_013) applied per Stage 4B; effective_scope=english_card_text_only |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[2], [E]: Move a friendly unit to or from your base.
```

**new_content**:

```
[2], [E]: Move a friendly unit to or from its base.
```

### `R-CARD-OGN-263`  —  card:OGN-263 (Swift Scout / 迅捷斥候) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-263-EV-CN-ER-0023  —  `R-CARD-OGN-263`  —  card:OGN-263 (Swift Scout / 迅捷斥候)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-263` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0023 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守一处战场、或从正面朝下的[待命]状态中打出时，展示你主牌堆顶部的五张牌，当中每
有一张带有[待命]技能的卡牌，就对此处的一名敌方单位造成1 点伤害，然后将展示的牌回收。
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守时，选择一名此处的敌方单位，展示你主牌堆顶部的五张牌。当中每有一张带有[待命]
技能的卡牌，便对该单位造成1 点伤害，然后将展示的牌回收。
```

### `R-CARD-OGN-263a`  —  card:OGN-263a (迅捷斥候) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-263a-EV-CN-ER-0023  —  `R-CARD-OGN-263a`  —  card:OGN-263a (迅捷斥候)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-263a` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0023 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守一处战场、或从正面朝下的[待命]状态中打出时，展示你主牌堆顶部的五张牌，当中每
有一张带有[待命]技能的卡牌，就对此处的一名敌方单位造成1 点伤害，然后将展示的牌回收。
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守时，选择一名此处的敌方单位，展示你主牌堆顶部的五张牌。当中每有一张带有[待命]
技能的卡牌，便对该单位造成1 点伤害，然后将展示的牌回收。
```

### `R-CARD-OGN-264`  —  card:OGN-264 (Guerilla Warfare / 游击战) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-264-EV-CN-ER-0023  —  `R-CARD-OGN-264`  —  card:OGN-264 (Guerilla Warfare / 游击战)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-264` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0023 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守一处战场、或从正面朝下的[待命]状态中打出时，展示你主牌堆顶部的五张牌，当中每
有一张带有[待命]技能的卡牌，就对此处的一名敌方单位造成1 点伤害，然后将展示的牌回收。
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守时，选择一名此处的敌方单位，展示你主牌堆顶部的五张牌。当中每有一张带有[待命]
技能的卡牌，便对该单位造成1 点伤害，然后将展示的牌回收。
```

### `R-CARD-OGN-269`  —  card:OGN-269 (The Boss / 腕豪) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-269-EV-CN-ER-0024  —  `R-CARD-OGN-269`  —  card:OGN-269 (The Boss / 腕豪)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-269` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0024 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
每当一名拥有增益且受你控制的单位被摧毁时，你可以选择支付[C]让我变为休眠状态，以此消耗
该单位身上的增益，然后改为以休眠状态将其召回。（把该单位送回基地，此行动不算作移
动。）
当你征服一处战场时，让我变为活跃状态。
```

**new_content**:

```
如果一名拥有增益且受你控制的单位被摧毁，则你可以选择支付[C]、让我变为休眠状态并消耗该
单位身上的增益，以此改为移除该单位所受伤害，让其进入休眠状态，并将其召回。（把该单位
送回基地，此行动不算作移动。）
当你征服一处战场时，让我变为活跃状态。
```

#### CHG-4B-T2ER-OGN-269-EV-EN-ER-0025  —  `R-CARD-OGN-269`  —  card:OGN-269 (The Boss / 腕豪)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-269` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0025 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When a buffed unit you control would die, you may pay [C] and exhaust me to
spend its buff and recall it exhausted instead. (Send it to base. This isn't a move.)
When you conquer, ready me.
```

**new_content**:

```
If a buffed unit you control would die, you may pay [C], exhaust me, and spend its
buff to heal it, exhaust it, and recall it instead. (Send it to base. This isn't a move.)
When you conquer, ready me.
```

### `R-CARD-OGN-287`  —  card:OGN-287 (Sigil of the Storm / 雷霆之纹) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-287-EV-CN-ER-0020  —  `R-CARD-OGN-287`  —  card:OGN-287 (Sigil of the Storm / 雷霆之纹)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-287` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0020 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你征服此处时，回收一枚你的符文。
```

**new_content**:

```
当你征服此处时，你必须回收一枚你的符文。（此行动不会做出任何选择。）
```

#### CHG-4B-T2ER-OGN-287-EV-EN-ER-0021  —  `R-CARD-OGN-287`  —  card:OGN-287 (Sigil of the Storm / 雷霆之纹)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-287` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0021 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When you conquer here, recycle one of your runes.
```

**new_content**:

```
When you conquer here, you must recycle one of your runes. (This doesn’t choose
anything.)
```

### `R-CARD-OGN-289`  —  card:OGN-289 (Targon's Peak / 巨神峰之巅) — 本规则共 3 条变更

#### CHG-4B-T2ER-OGN-289-EV-CN-ER-0022  —  `R-CARD-OGN-289`  —  card:OGN-289 (Targon's Peak / 巨神峰之巅)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-289` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0022 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: earlier zh errata in chain; canonical carried by later errata |

**original_content**:

```
当你征服此处时，选择两枚符文，并在本回合结束时，让它们变为活跃状态。
```

**new_content**:

```
当你征服此处时，选择最多两枚符文，并在本回合结束时，让它们变为活跃状态。
```

#### CHG-4B-T2ER-OGN-289-EV-CN-ER-0092  —  `R-CARD-OGN-289`  —  card:OGN-289 (Targon's Peak / 巨神峰之巅)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-289` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `10_2026-07-24_9fe1f19110dd4678a6ad7bd96e791bba.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0092 (source_010) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你征服此处时，选择最多两枚符文，并在本回合结束时，让它们变为活跃状态。
```

**new_content**:

```
当你征服此处时，让最多两枚符文在本回合结束时变为活跃状态。
```

#### CHG-4B-T2ER-OGN-289-EV-EN-ER-0023  —  `R-CARD-OGN-289`  —  card:OGN-289 (Targon's Peak / 巨神峰之巅)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-289` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0023 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When you conquer here, ready 2 runes at the end of this turn.
```

**new_content**:

```
When you conquer here, ready up to 2 runes at the end of this turn.
```

### `R-CARD-OGN-292`  —  card:OGN-292 (The Dreaming Tree / 幻梦之树) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-292-EV-CN-ER-0025  —  `R-CARD-OGN-292`  —  card:OGN-292 (The Dreaming Tree / 幻梦之树)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-292` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0025 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
每回合首次：当你对此处的友方单位使用法术时，抽一张牌。
```

**new_content**:

```
每回合首次，当玩家将此处的一名友方单位选为法术目标时，该玩家抽一张牌。
```

#### CHG-4B-T2ER-OGN-292-EV-EN-ER-0026  —  `R-CARD-OGN-292`  —  card:OGN-292 (The Dreaming Tree / 幻梦之树)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-292` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0026 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
The first time you choose a friendly unit with a spell here each turn, draw 1.
```

**new_content**:

```
When a player chooses a friendly unit here with a spell for the first time each turn,
they draw 1.
```

### `R-CARD-OGN-293`  —  card:OGN-293 (The Grand Plaza / 宏伟广场) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-293-EV-CN-ER-0044  —  `R-CARD-OGN-293`  —  card:OGN-293 (The Grand Plaza / 宏伟广场)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-293` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0044 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你据守此处，且在此处拥有至少七名单位时，你赢得游戏胜利。
```

**new_content**:

```
当你据守此处时，如果你在此拥有至少七名单位，则你赢得游戏胜利。
```

### `R-CARD-OGN-293a`  —  card:OGN-293a (宏伟广场) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-293a-EV-CN-ER-0044  —  `R-CARD-OGN-293a`  —  card:OGN-293a (宏伟广场)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-293a` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0044 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你据守此处，且在此处拥有至少七名单位时，你赢得游戏胜利。
```

**new_content**:

```
当你据守此处时，如果你在此拥有至少七名单位，则你赢得游戏胜利。
```

### `R-CARD-OGN-296`  —  card:OGN-296 (Void Gate / 虚空之门) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-296-EV-CN-ER-0030  —  `R-CARD-OGN-296`  —  card:OGN-296 (Void Gate / 虚空之门)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-296` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0030 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
以此处的单位作为目标的法术或技能，造成的伤害+1（每段伤害都+1）。
```

**new_content**:

```
法术和技能对此处的单位造成的伤害+1（每段伤害都+1）。
```

#### CHG-4B-T2ER-OGN-296-EV-EN-ER-0031  —  `R-CARD-OGN-296`  —  card:OGN-296 (Void Gate / 虚空之门)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-296` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0031 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
Spells and abilities affecting units here each deal 1 Bonus Damage. (Each instance
of damage the spell deals is increased by 1.)
```

**new_content**:

```
Spells and abilities deal 1 Bonus Damage to units here. (Each instance of damage
the spell deals to a unit here is increased by 1.)
```

### `R-CARD-OGN-305*`  —  card:OGN-305* (Unforgiven / 疾风剑豪) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-305*-EV-CN-ER-0028  —  `R-CARD-OGN-305*`  —  card:OGN-305* (Unforgiven / 疾风剑豪)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-305*` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0028 (source_002) applied per Stage 4B; effective_scope=english_card_text_only |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
支付[2]，[E]：在战场和你的基地之间移动一名友方单位。
```

**new_content**:

```
支付[2]，[E]：在战场和其所属基地之间移动一名友方单位。
```

#### CHG-4B-T2ER-OGN-305*-EV-EN-ER-0029  —  `R-CARD-OGN-305*`  —  card:OGN-305* (Unforgiven / 疾风剑豪)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-305*` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0029 (source_013) applied per Stage 4B; effective_scope=english_card_text_only |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[2], [E]: Move a friendly unit to or from your base.
```

**new_content**:

```
[2], [E]: Move a friendly unit to or from its base.
```

### `R-CARD-OGN-305`  —  card:OGN-305 (Unforgiven / 疾风剑豪) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-305-EV-CN-ER-0028  —  `R-CARD-OGN-305`  —  card:OGN-305 (Unforgiven / 疾风剑豪)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-305` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0028 (source_002) applied per Stage 4B; effective_scope=english_card_text_only |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
支付[2]，[E]：在战场和你的基地之间移动一名友方单位。
```

**new_content**:

```
支付[2]，[E]：在战场和其所属基地之间移动一名友方单位。
```

#### CHG-4B-T2ER-OGN-305-EV-EN-ER-0029  —  `R-CARD-OGN-305`  —  card:OGN-305 (Unforgiven / 疾风剑豪)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-305` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0029 (source_013) applied per Stage 4B; effective_scope=english_card_text_only |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[2], [E]: Move a friendly unit to or from your base.
```

**new_content**:

```
[2], [E]: Move a friendly unit to or from its base.
```

### `R-CARD-OGN-307*`  —  card:OGN-307* (Swift Scout / 迅捷斥候) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-307*-EV-CN-ER-0023  —  `R-CARD-OGN-307*`  —  card:OGN-307* (Swift Scout / 迅捷斥候)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-307*` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0023 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守一处战场、或从正面朝下的[待命]状态中打出时，展示你主牌堆顶部的五张牌，当中每
有一张带有[待命]技能的卡牌，就对此处的一名敌方单位造成1 点伤害，然后将展示的牌回收。
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守时，选择一名此处的敌方单位，展示你主牌堆顶部的五张牌。当中每有一张带有[待命]
技能的卡牌，便对该单位造成1 点伤害，然后将展示的牌回收。
```

### `R-CARD-OGN-307`  —  card:OGN-307 (Swift Scout / 迅捷斥候) — 本规则共 1 条变更

#### CHG-4B-T2ER-OGN-307-EV-CN-ER-0023  —  `R-CARD-OGN-307`  —  card:OGN-307 (Swift Scout / 迅捷斥候)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-307` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0023 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守一处战场、或从正面朝下的[待命]状态中打出时，展示你主牌堆顶部的五张牌，当中每
有一张带有[待命]技能的卡牌，就对此处的一名敌方单位造成1 点伤害，然后将展示的牌回收。
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守时，选择一名此处的敌方单位，展示你主牌堆顶部的五张牌。当中每有一张带有[待命]
技能的卡牌，便对该单位造成1 点伤害，然后将展示的牌回收。
```

### `R-CARD-OGN-310*`  —  card:OGN-310* (The Boss / 腕豪) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-310*-EV-CN-ER-0024  —  `R-CARD-OGN-310*`  —  card:OGN-310* (The Boss / 腕豪)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-310*` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0024 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
每当一名拥有增益且受你控制的单位被摧毁时，你可以选择支付[C]让我变为休眠状态，以此消耗
该单位身上的增益，然后改为以休眠状态将其召回。（把该单位送回基地，此行动不算作移
动。）
当你征服一处战场时，让我变为活跃状态。
```

**new_content**:

```
如果一名拥有增益且受你控制的单位被摧毁，则你可以选择支付[C]、让我变为休眠状态并消耗该
单位身上的增益，以此改为移除该单位所受伤害，让其进入休眠状态，并将其召回。（把该单位
送回基地，此行动不算作移动。）
当你征服一处战场时，让我变为活跃状态。
```

#### CHG-4B-T2ER-OGN-310*-EV-EN-ER-0025  —  `R-CARD-OGN-310*`  —  card:OGN-310* (The Boss / 腕豪)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-310*` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0025 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When a buffed unit you control would die, you may pay [C] and exhaust me to
spend its buff and recall it exhausted instead. (Send it to base. This isn't a move.)
When you conquer, ready me.
```

**new_content**:

```
If a buffed unit you control would die, you may pay [C], exhaust me, and spend its
buff to heal it, exhaust it, and recall it instead. (Send it to base. This isn't a move.)
When you conquer, ready me.
```

### `R-CARD-OGN-310`  —  card:OGN-310 (The Boss / 腕豪) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGN-310-EV-CN-ER-0024  —  `R-CARD-OGN-310`  —  card:OGN-310 (The Boss / 腕豪)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-310` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0024 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
每当一名拥有增益且受你控制的单位被摧毁时，你可以选择支付[C]让我变为休眠状态，以此消耗
该单位身上的增益，然后改为以休眠状态将其召回。（把该单位送回基地，此行动不算作移
动。）
当你征服一处战场时，让我变为活跃状态。
```

**new_content**:

```
如果一名拥有增益且受你控制的单位被摧毁，则你可以选择支付[C]、让我变为休眠状态并消耗该
单位身上的增益，以此改为移除该单位所受伤害，让其进入休眠状态，并将其召回。（把该单位
送回基地，此行动不算作移动。）
当你征服一处战场时，让我变为活跃状态。
```

#### CHG-4B-T2ER-OGN-310-EV-EN-ER-0025  —  `R-CARD-OGN-310`  —  card:OGN-310 (The Boss / 腕豪)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGN-310` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0025 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When a buffed unit you control would die, you may pay [C] and exhaust me to
spend its buff and recall it exhausted instead. (Send it to base. This isn't a move.)
When you conquer, ready me.
```

**new_content**:

```
If a buffed unit you control would die, you may pay [C], exhaust me, and spend its
buff to heal it, exhaust it, and recall it instead. (Send it to base. This isn't a move.)
When you conquer, ready me.
```

### `R-CARD-OGS-017`  —  card:OGS-017 (Dark Child - Starter / 黑暗之女) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGS-017-EV-CN-ER-0006  —  `R-CARD-OGS-017`  —  card:OGS-017 (Dark Child - Starter / 黑暗之女)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGS-017` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0006 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
在你回合结束时，让两枚符文变为活跃状态。
```

**new_content**:

```
在你回合结束时，让最多两枚符文变为活跃状态。
```

#### CHG-4B-T2ER-OGS-017-EV-EN-ER-0007  —  `R-CARD-OGS-017`  —  card:OGS-017 (Dark Child - Starter / 黑暗之女)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGS-017` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0007 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
At the end of your turn, ready 2 runes.
```

**new_content**:

```
At the end of your turn, ready up to 2 runes.
```

### `R-CARD-OGS-020`  —  card:OGS-020 (Highlander / 高原血统) — 本规则共 2 条变更

#### CHG-4B-T2ER-OGS-020-EV-CN-ER-0011  —  `R-CARD-OGS-020`  —  card:OGS-020 (Highlander / 高原血统)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGS-020` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0011 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[反应]（可在任意时机打出，甚至先于其他法术和技能的结算。）
选择一名友方单位。如果该单位在本回合内被摧毁，则改为以休眠状态将其召回。（把该单位送
回基地，此行动不算作移动。）
```

**new_content**:

```
[反应]（可在任意时机打出，甚至先于其他法术和技能的结算。）
选择一名友方单位。本回合内，在该单位下次被摧毁时，改为移除其所受伤害、将其变为休眠状
态、并将其召回。（把该单位送回基地，此行动不算作移动。）
```

#### CHG-4B-T2ER-OGS-020-EV-EN-ER-0012  —  `R-CARD-OGS-020`  —  card:OGS-020 (Highlander / 高原血统)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-OGS-020` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0012 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Reaction] (Play any time, even before spells and abilities resolve.)
Choose a friendly unit. The next time it dies this turn, recall it exhausted instead.
(Send it to base. This isn't a move.)
```

**new_content**:

```
[Reaction] (Play any time, even before spells and abilities resolve.)
Choose a friendly unit. The next time it would die this turn, heal it, exhaust it, and
recall it instead. (Send it to base. This isn't a move.)
```

### `R-CARD-SFD-003`  —  card:SFD-003 (Blood Rush / 血性冲刺) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-003-EV-CN-ER-0067  —  `R-CARD-SFD-003`  —  card:SFD-003 (Blood Rush / 血性冲刺)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-003` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0067 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[迅捷]（可在你的回合或法术对决中打出。）
[回响][1]（你可以选择支付此额外费用，以重复此法术效果。）
让一名单位获得[强攻2]。（如果它是进攻方，则[M]+2。）
```

**new_content**:

```
[迅捷]（可在你的回合或法术对决中打出。）
[回响][1]（你可以选择支付此额外费用，以重复此法术效果。）
让一名单位本回合内获得[强攻2]。（如果它是进攻方，则[M]+2。）
```

#### CHG-4B-T2ER-SFD-003-EV-EN-ER-0037  —  `R-CARD-SFD-003`  —  card:SFD-003 (Blood Rush / 血性冲刺)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-003` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0037 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Action] (Play on your turn or in showdowns.)
[Repeat] [1] (You may pay the additional cost to repeat this spell's effect.)
Give a unit [Assault 2]. (+2 [M] while it's an attacker.)
```

**new_content**:

```
[Action] (Play on your turn or in showdowns.)
[Repeat] [1] (You may pay the additional cost to repeat this spell's effect.)
Give a unit [Assault 2] this turn. (+2 [M] while it's an attacker.)
```

### `R-CARD-SFD-020`  —  card:SFD-020 (Draven, Vanquisher / 德莱文) — 本规则共 3 条变更

#### CHG-4B-T2ER-SFD-020-EV-CN-ER-0051  —  `R-CARD-SFD-020`  —  card:SFD-020 (Draven, Vanquisher / 德莱文)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-020` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0051 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: zh translation-fix errata superseded by later zh errata on same card |

**original_content**:

```
当我赢得战斗时，打出一个休眠的“金币”装备指示物。
当我进攻或防守时，你可以选择支付[C]，以此让我在本回合内战力+2。
```

**new_content**:

```
当我赢得战斗时，打出一个休眠的“金币”装备指示物。
当我进攻或防守时，你可以选择支付[C]。若如此做，则让我在本回合内[S]+2。
```

#### CHG-4B-T2ER-SFD-020-EV-CN-ER-0081  —  `R-CARD-SFD-020`  —  card:SFD-020 (Draven, Vanquisher / 德莱文)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-020` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `10_2026-07-24_9fe1f19110dd4678a6ad7bd96e791bba.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0081 (source_010) applied per Stage 4B; effective_scope=printed_text_alignment |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当我赢得战斗时，打出一个休眠的“金币”装备指示物。
当我进攻或防守时，你可以选择支付[C]。若如此做，则让我在本回合内[M]+2。
```

**new_content**:

```
当我赢得战斗时，打出一个休眠的“金币”装备指示物。
当我进攻或防守时，你可以选择支付[C]，以此给予我在本回合内[M]+2。
```

#### CHG-4B-T2ER-SFD-020-EV-EN-ER-0059  —  `R-CARD-SFD-020`  —  card:SFD-020 (Draven, Vanquisher / 德莱文)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-020` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `09_2026-07-23_Vendetta_Errata.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0059 (source_020) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When I win a combat, play a Gold gear token exhausted.
When I attack or defend, you may pay [C]. If you do, give me +2 [M] this turn.
```

**new_content**:

```
When I win a combat, play a Gold gear token exhausted.
When I attack or defend, you may pay [C] to give me +2 [M] this turn.
```

### `R-CARD-SFD-020a`  —  card:SFD-020a (Draven, Vanquisher / 德莱文) — 本规则共 3 条变更

#### CHG-4B-T2ER-SFD-020a-EV-CN-ER-0051  —  `R-CARD-SFD-020a`  —  card:SFD-020a (Draven, Vanquisher / 德莱文)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-020a` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0051 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: zh translation-fix errata superseded by later zh errata on same card |

**original_content**:

```
当我赢得战斗时，打出一个休眠的“金币”装备指示物。
当我进攻或防守时，你可以选择支付[C]，以此让我在本回合内战力+2。
```

**new_content**:

```
当我赢得战斗时，打出一个休眠的“金币”装备指示物。
当我进攻或防守时，你可以选择支付[C]。若如此做，则让我在本回合内[S]+2。
```

#### CHG-4B-T2ER-SFD-020a-EV-CN-ER-0081  —  `R-CARD-SFD-020a`  —  card:SFD-020a (Draven, Vanquisher / 德莱文)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-020a` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `10_2026-07-24_9fe1f19110dd4678a6ad7bd96e791bba.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0081 (source_010) applied per Stage 4B; effective_scope=printed_text_alignment |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当我赢得战斗时，打出一个休眠的“金币”装备指示物。
当我进攻或防守时，你可以选择支付[C]。若如此做，则让我在本回合内[M]+2。
```

**new_content**:

```
当我赢得战斗时，打出一个休眠的“金币”装备指示物。
当我进攻或防守时，你可以选择支付[C]，以此给予我在本回合内[M]+2。
```

#### CHG-4B-T2ER-SFD-020a-EV-EN-ER-0059  —  `R-CARD-SFD-020a`  —  card:SFD-020a (Draven, Vanquisher / 德莱文)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-020a` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `09_2026-07-23_Vendetta_Errata.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0059 (source_020) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When I win a combat, play a Gold gear token exhausted.
When I attack or defend, you may pay [C]. If you do, give me +2 [M] this turn.
```

**new_content**:

```
When I win a combat, play a Gold gear token exhausted.
When I attack or defend, you may pay [C] to give me +2 [M] this turn.
```

### `R-CARD-SFD-024`  —  card:SFD-024 (Rell, Magnetic / 芮尔) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-024-EV-CN-ER-0074  —  `R-CARD-SFD-024`  —  card:SFD-024 (Rell, Magnetic / 芮尔)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-024` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0074 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[壁垒]（我在战斗中首先承担伤害。）
当我进攻时，你可以选择打出一件法力费用不高于[2]的武装，无视其费用，然后将其贴附到我身
上。
```

**new_content**:

```
[壁垒]（我在战斗中首先承担伤害。）
当我进攻时，你可以选择打出一件法力费用不高于[2]的武装，无视其费用。若如此做，则进行一
次：将其贴附到我身上。
```

#### CHG-4B-T2ER-SFD-024-EV-EN-ER-0044  —  `R-CARD-SFD-024`  —  card:SFD-024 (Rell, Magnetic / 芮尔)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-024` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `effect_change` |
| reason | official errata EV-EN-ER-0044 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Tank] (I must be assigned combat damage first.)
When I attack, you may play an Equipment with Energy cost no more than [2],
ignoring its cost, and attach it to me.
```

**new_content**:

```
[Tank] (I must be assigned combat damage first.)
When I attack, you may play an Equipment with Energy cost no more than [2],
ignoring its cost. If you do, then do this: Attach it to me.
```

### `R-CARD-SFD-026`  —  card:SFD-026 (Rumble, Hotheaded / 兰博) — 本规则共 1 条变更

#### CHG-4B-T2ER-SFD-026-EV-CN-ER-0049  —  `R-CARD-SFD-026`  —  card:SFD-026 (Rumble, Hotheaded / 兰博)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-026` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0049 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
你的“机械”属性单位获得强攻。（如果它是进攻方，则战力+1。）
当我征服一处战场时，你可以选择回收另一名友方单位，以此从废牌堆中打出一名“机械”属性
单位，将其所需法力费用减去被回收单位的战力。
```

**new_content**:

```
你的“机械”属性单位获得强攻。（如果它是进攻方，则战力+1。）
当我征服一处战场时，你可以选择回收另一名友方单位，以此从你的废牌堆中打出一名“机械”
属性单位，将其所需法力费用减去被回收单位的战力。
```

### `R-CARD-SFD-026a`  —  card:SFD-026a (Rumble, Hotheaded / 兰博) — 本规则共 1 条变更

#### CHG-4B-T2ER-SFD-026a-EV-CN-ER-0049  —  `R-CARD-SFD-026a`  —  card:SFD-026a (Rumble, Hotheaded / 兰博)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-026a` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0049 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
你的“机械”属性单位获得强攻。（如果它是进攻方，则战力+1。）
当我征服一处战场时，你可以选择回收另一名友方单位，以此从废牌堆中打出一名“机械”属性
单位，将其所需法力费用减去被回收单位的战力。
```

**new_content**:

```
你的“机械”属性单位获得强攻。（如果它是进攻方，则战力+1。）
当我征服一处战场时，你可以选择回收另一名友方单位，以此从你的废牌堆中打出一名“机械”
属性单位，将其所需法力费用减去被回收单位的战力。
```

### `R-CARD-SFD-053`  —  card:SFD-053 (Janna, Savior / 迦娜) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-053-EV-CN-ER-0070  —  `R-CARD-SFD-053`  —  card:SFD-053 (Janna, Savior / 迦娜)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-053` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0070 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[反应]（可在任意时机打出，甚至先于其他法术和技能的结算，并能打出到你控制的战场。）
当你打出我时，为此处你的所有单位移除伤害，然后将一名敌方单位从此处移动到其所属的基
地。
```

**new_content**:

```
[反应]（可在任意时机打出，甚至先于其他法术和技能的结算，并能打出到你控制的战场。）
当你打出我时，为此处你的所有单位移除伤害，然后将最多一名敌方单位从此处移动到其所属的
基地。
```

#### CHG-4B-T2ER-SFD-053-EV-EN-ER-0040  —  `R-CARD-SFD-053`  —  card:SFD-053 (Janna, Savior / 迦娜)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-053` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0040 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Reaction] (Play any time, even before spells and abilities resolve, including to a
battlefield you control.)
When you play me, heal your units here, then move an enemy unit from here to its
base.
```

**new_content**:

```
[Reaction] (Play any time, even before spells and abilities resolve, including to a
battlefield you control.)
When you play me, heal your units here, then move up to one enemy unit from
here to its base.
```

### `R-CARD-SFD-054`  —  card:SFD-054 (Jax, Unmatched / 贾克斯) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-054-EV-CN-ER-0071  —  `R-CARD-SFD-054`  —  card:SFD-054 (Jax, Unmatched / 贾克斯)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-054` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0071 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[法盾]（对手必须支付[A]才能将我选作法术或技能的目标。）
你手牌中的每一件武装都获得[灵便]。（其获得[反应]。当你打出此牌时，将其贴附到你控制的一
名单位上。）
```

**new_content**:

```
[法盾]（对手必须支付[A]才能将我选作法术或技能的目标。）
你各处的武装都获得[灵便]。（每件武装获得[反应]。当你打出此牌时，将其贴附到你控制的一名
单位上。）
```

#### CHG-4B-T2ER-SFD-054-EV-EN-ER-0041  —  `R-CARD-SFD-054`  —  card:SFD-054 (Jax, Unmatched / 贾克斯)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-054` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0041 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Deflect] (Opponents must pay [A] to choose me with a spell or ability.)
Each Equipment in your hand has [Quick-Draw]. (It gains [Reaction]. When you play
it, attach it to a unit you control.)
```

**new_content**:

```
[Deflect] (Opponents must pay [A] to choose me with a spell or ability.)
Your Equipment everywhere have [Quick-Draw]. (Each gains [Reaction]. When you
play it, attach it to a unit you control.)
```

### `R-CARD-SFD-054a`  —  card:SFD-054a (Jax, Unmatched / 贾克斯) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-054a-EV-CN-ER-0071  —  `R-CARD-SFD-054a`  —  card:SFD-054a (Jax, Unmatched / 贾克斯)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-054a` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0071 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[法盾]（对手必须支付[A]才能将我选作法术或技能的目标。）
你手牌中的每一件武装都获得[灵便]。（其获得[反应]。当你打出此牌时，将其贴附到你控制的一
名单位上。）
```

**new_content**:

```
[法盾]（对手必须支付[A]才能将我选作法术或技能的目标。）
你各处的武装都获得[灵便]。（每件武装获得[反应]。当你打出此牌时，将其贴附到你控制的一名
单位上。）
```

#### CHG-4B-T2ER-SFD-054a-EV-EN-ER-0041  —  `R-CARD-SFD-054a`  —  card:SFD-054a (Jax, Unmatched / 贾克斯)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-054a` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0041 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Deflect] (Opponents must pay [A] to choose me with a spell or ability.)
Each Equipment in your hand has [Quick-Draw]. (It gains [Reaction]. When you play
it, attach it to a unit you control.)
```

**new_content**:

```
[Deflect] (Opponents must pay [A] to choose me with a spell or ability.)
Your Equipment everywhere have [Quick-Draw]. (Each gains [Reaction]. When you
play it, attach it to a unit you control.)
```

### `R-CARD-SFD-060`  —  card:SFD-060 (Tianna Crownguard / 缇亚娜·冕卫) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-060-EV-CN-ER-0075  —  `R-CARD-SFD-060`  —  card:SFD-060 (Tianna Crownguard / 缇亚娜·冕卫)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-060` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0075 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[法盾]（对手必须支付[A]才能将我选作法术或技能的目标。）
如果我位于战场上，则对手无法得分。
```

**new_content**:

```
[法盾]（对手必须支付[A]才能将我选作法术或技能的目标。）
如果我位于战场上，则对手无法获得分数。
```

#### CHG-4B-T2ER-SFD-060-EV-EN-ER-0045  —  `R-CARD-SFD-060`  —  card:SFD-060 (Tianna Crownguard / 缇亚娜·冕卫)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-060` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0045 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Deflect] (Opponents must pay [A] to choose me with a spell or ability.)
While I'm at a battlefield, opponents can't score points.
```

**new_content**:

```
[Deflect] (Opponents must pay [A] to choose me with a spell or ability.)
While I'm at a battlefield, opponents can't gain points.
```

### `R-CARD-SFD-074`  —  card:SFD-074 (Pickpocket / 暗巷神偷) — 本规则共 1 条变更

#### CHG-4B-T2ER-SFD-074-EV-CN-ER-0052  —  `R-CARD-SFD-074`  —  card:SFD-074 (Pickpocket / 暗巷神偷)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-074` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0052 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你打出我时，你可以选择摧毁一件法力费用不高于[1]的装备，以此打出一个休眠的“金币”装
备指示物。
```

**new_content**:

```
当你打出我时，你可以选择摧毁一件法力费用不高于[1]的装备。若如此做，则打出一个休眠的
“金币”装备指示物。
```

### `R-CARD-SFD-084`  —  card:SFD-084 (Jayce, Man of Progress / 杰斯) — 本规则共 1 条变更

#### CHG-4B-T2ER-SFD-084-EV-CN-ER-0050  —  `R-CARD-SFD-084`  —  card:SFD-084 (Jayce, Man of Progress / 杰斯)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-084` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0050 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你打出我时，你可以选择摧毁一件友方装备，以此在本回合内可以从手牌中打出一件法力费用
不高于[7]的装备，无视其法力费用（仍需支付所有符能费用）。
```

**new_content**:

```
当你打出我时，你可以选择摧毁一件友方装备。若如此做，则在本回合内，你可以选择从手牌中
打出一件法力费用不高于[7]的装备，无视其法力费用（仍需支付所有符能费用）。
```

### `R-CARD-SFD-112`  —  card:SFD-112 (Kato the Arm / 巨腕加藤) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-112-EV-CN-ER-0072  —  `R-CARD-SFD-112`  —  card:SFD-112 (Kato the Arm / 巨腕加藤)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-112` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0072 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[法盾]（对手必须支付[A]才能将我选作法术或技能的目标。）
当我移动到一处战场时，让一名友方单位在本回合内获得我的关键词和等同于我战力的+[M]加
成。
```

**new_content**:

```
[法盾]（对手必须支付[A]才能将我选作法术或技能的目标。）
当我移动到一处战场时，让另一名友方单位在本回合内获得我的关键词和等同于我战力的+[M]加
成。
```

#### CHG-4B-T2ER-SFD-112-EV-EN-ER-0042  —  `R-CARD-SFD-112`  —  card:SFD-112 (Kato the Arm / 巨腕加藤)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-112` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0042 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Deflect] (Opponents must pay [A] to choose me with a spell or ability.)
When I move to a battlefield, give a friendly unit my keywords and +[M] equal to my
Might this turn.
```

**new_content**:

```
[Deflect] (Opponents must pay [A] to choose me with a spell or ability.)
When I move to a battlefield, give another friendly unit my keywords and +[M] equal
to my Might this turn.
```

### `R-CARD-SFD-116`  —  card:SFD-116 (Yone, Blademaster / 永恩) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-116-EV-CN-ER-0078  —  `R-CARD-SFD-116`  —  card:SFD-116 (Yone, Blademaster / 永恩)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-116` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0078 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[百炼]（当你打出我时，你可以选择为我[装配]你的一件武装，其装配费用减少[A]。可选择已贴
附的武装。）
当我征服一处开放的战场时，对基地中的一名敌方单位造成等同于我战力的伤害。
```

**new_content**:

```
[百炼]（当你打出我时，你可以选择为我[装配]你的一件武装，其装配费用减少[A]。可选择已贴
附的武装。）
当我征服一处未受控制的战场时，对基地中的一名敌方单位造成等同于我战力的伤害。
```

#### CHG-4B-T2ER-SFD-116-EV-EN-ER-0048  —  `R-CARD-SFD-116`  —  card:SFD-116 (Yone, Blademaster / 永恩)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-116` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0048 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Weaponmaster] (When you play me, you may [Equip] one of your Equipment to
me for [A] less, even if it's already attached.)
When I conquer an open battlefield, deal damage equal to my Might to an enemy
unit in a base.
```

**new_content**:

```
[Weaponmaster] (When you play me, you may [Equip] one of your Equipment to
me for [A] less, even if it's already attached.)
When I conquer a battlefield that was uncontrolled, deal damage equal to my
Might to an enemy unit in a base.
```

### `R-CARD-SFD-126`  —  card:SFD-126 (Loyal Pup / 忠诚的猎犬) — 本规则共 1 条变更

#### CHG-4B-T2ER-SFD-126-EV-CN-ER-0091  —  `R-CARD-SFD-126`  —  card:SFD-126 (Loyal Pup / 忠诚的猎犬)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-126` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `10_2026-07-24_9fe1f19110dd4678a6ad7bd96e791bba.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0091 (source_010) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你防守一处战场时，可以选择将我移动到此战场
```

**new_content**:

```
当你防守一处战场时，可以选择将我移动到该处。
```

### `R-CARD-SFD-139`  —  card:SFD-139 (Edge of Night / 夜之锋刃) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-139-EV-CN-ER-0069  —  `R-CARD-SFD-139`  —  card:SFD-139 (Edge of Night / 夜之锋刃)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-139` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0069 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当你将此牌从正面朝下的状态打出时，将其贴附到此处你控制的一名单位上。
[装配][C]（支付[C]：将此牌贴附到你控制的一名单位上。）
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当你将此牌从正面朝下的状态打出时，将其贴附到你（在此处）控制的一名单位上。
[装配][C]（支付[C]：将此牌贴附到你控制的一名单位上。）
```

#### CHG-4B-T2ER-SFD-139-EV-EN-ER-0039  —  `R-CARD-SFD-139`  —  card:SFD-139 (Edge of Night / 夜之锋刃)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-139` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `numeric_change` |
| reason | official errata EV-EN-ER-0039 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
When you play this from face down, attach it to a unit you control here.
[Equip] [C] ([C]: Attach this to a unit you control.)
```

**new_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
When you play this from face down, attach it to a unit you control (here).
[Equip] [C] ([C]: Attach this to a unit you control.)
```

### `R-CARD-SFD-140`  —  card:SFD-140 (Fizz, Trickster / 菲兹) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-140-EV-CN-ER-0083  —  `R-CARD-SFD-140`  —  card:SFD-140 (Fizz, Trickster / 菲兹)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-140` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `10_2026-07-24_9fe1f19110dd4678a6ad7bd96e791bba.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0083 (source_010) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你打出我时，你可以选择从你的废牌堆中打出一个法力费用不高于[3]的法术，无需支付其法力
费用（仍需支付所有符能费用）。打出该法术后，将其回收。
```

**new_content**:

```
当你打出我时，你可以选择从你的废牌堆中打出一个法力费用不高于[3]的法术，无视其法力费
用。然后将其回收。（仍需支付所有符能费用。）
```

#### CHG-4B-T2ER-SFD-140-EV-EN-ER-0061  —  `R-CARD-SFD-140`  —  card:SFD-140 (Fizz, Trickster / 菲兹)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-140` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `09_2026-07-23_Vendetta_Errata.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0061 (source_020) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When you play me, you may play a spell from your trash with Energy cost no more than [3], ignoring its Energy cost. Recycle that spell
after you play it. (You must still pay its Power cost.)
```

**new_content**:

```
When you play me, you may play a spell from your trash with Energy cost no more than [3], ignoring its Energy cost. Then recycle it. (You
must still pay its Power cost.)
```

### `R-CARD-SFD-149`  —  card:SFD-149 (Ezreal, Prodigy / 伊泽瑞尔) — 本规则共 1 条变更

#### CHG-4B-T2ER-SFD-149-EV-CN-ER-0047  —  `R-CARD-SFD-149`  —  card:SFD-149 (Ezreal, Prodigy / 伊泽瑞尔)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-149` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0047 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你打出我时，弃置一张手牌，然后抽两张牌。
你可以将其他卡牌的可选额外费用减少[1]或[A]后支付。
```

**new_content**:

```
当你打出我时，弃置一张手牌，然后抽两张牌。
你支付的可选额外费用，其费用减少[1]或[A]。
```

### `R-CARD-SFD-149a`  —  card:SFD-149a (Ezreal, Prodigy / 伊泽瑞尔) — 本规则共 1 条变更

#### CHG-4B-T2ER-SFD-149a-EV-CN-ER-0047  —  `R-CARD-SFD-149a`  —  card:SFD-149a (Ezreal, Prodigy / 伊泽瑞尔)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-149a` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0047 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你打出我时，弃置一张手牌，然后抽两张牌。
你可以将其他卡牌的可选额外费用减少[1]或[A]后支付。
```

**new_content**:

```
当你打出我时，弃置一张手牌，然后抽两张牌。
你支付的可选额外费用，其费用减少[1]或[A]。
```

### `R-CARD-SFD-150`  —  card:SFD-150 (Last Rites / 临终仪式) — 本规则共 1 条变更

#### CHG-4B-T2ER-SFD-150-EV-CN-ER-0053  —  `R-CARD-SFD-150`  —  card:SFD-150 (Last Rites / 临终仪式)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-150` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0053 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[装配] — 支付[C]，从你的废牌堆回收两张卡牌。（支付此费用：将此牌贴附到你控制的一名单位
上。）
当我征服或据守一处战场时，你可以选择从你的弃牌堆中打出一名单位。（仍需支付其费用。）
```

**new_content**:

```
[装配] — 支付[C]，从你的废牌堆回收两张卡牌。（支付此费用：将此牌贴附到你控制的一名单位
上。）
当我征服或据守一处战场时，你可以选择从你的废牌堆中打出一名单位。（仍需支付其费用。）
```

### `R-CARD-SFD-154`  —  card:SFD-154 (Guards! / 护驾！) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-154-EV-CN-ER-0032  —  `R-CARD-SFD-154`  —  card:SFD-154 (Guards! / 护驾！)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-154` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `effect_change` |
| reason | official errata EV-CN-ER-0032 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
打出一名2[M]的“黄沙士兵”。你可以选择支付[C]，以此让其变为活跃状态。
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
打出一名2[M]的“黄沙士兵”。然后进行一次：你可以选择支付[C]，以此让其变为活跃状态。
```

#### CHG-4B-T2ER-SFD-154-EV-EN-ER-0050  —  `R-CARD-SFD-154`  —  card:SFD-154 (Guards! / 护驾！)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-154` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `06_2026-04-03_Unleashed_Errata.pdf` |
| version | `v2026` |
| date | `2026-04-03` |
| modification_type | `effect_change` |
| reason | official errata EV-EN-ER-0050 (source_017) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
Play a 2 [M] Sand Soldier unit token. You may pay [C] to ready it.
```

**new_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
Play a 2 [M] Sand Soldier unit token. Then do this: You may pay [C] to ready it.
```

### `R-CARD-SFD-163`  —  card:SFD-163 (Deathgrip / 断魂一扼) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-163-EV-CN-ER-0068  —  `R-CARD-SFD-163`  —  card:SFD-163 (Deathgrip / 断魂一扼)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-163` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0068 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[反应]（可在任意时机打出，甚至先于其他法术和技能的结算。）
摧毁一名友方单位，让另一名友方单位在本回合内获得等同于被摧毁单位战力的+[M]加成。抽一
张牌。
```

**new_content**:

```
[反应]（可在任意时机打出，甚至先于其他法术和技能的结算。）
摧毁一名友方单位。若如此做，则让另一名友方单位在本回合内获得等同于前者战力的+[M]加
成。
抽一张牌。
```

#### CHG-4B-T2ER-SFD-163-EV-EN-ER-0038  —  `R-CARD-SFD-163`  —  card:SFD-163 (Deathgrip / 断魂一扼)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-163` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0038 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Reaction] (Play any time, even before spells and abilities resolve.)
Kill a friendly unit to give +[M] equal to its Might to another friendly unit this turn.
Draw 1.
```

**new_content**:

```
[Reaction] (Play any time, even before spells and abilities resolve.)
Kill a friendly unit. If you do, give +[M] equal to its Might to another friendly unit this
turn.
Draw 1.
```

### `R-CARD-SFD-170`  —  card:SFD-170 (Rek'Sai, Swarm Queen / 雷克塞) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-170-EV-CN-ER-0073  —  `R-CARD-SFD-170`  —  card:SFD-170 (Rek'Sai, Swarm Queen / 雷克塞)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-170` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0073 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当我进攻时，你可以选择展示你主牌堆顶部的两张牌。你可以选择打出其中一张牌，然后回收其
余的卡牌。如果以此方式打出的卡牌为单位，则可以选择将其打出到此处。
```

**new_content**:

```
当我进攻时，你可以选择展示你主牌堆顶部的两张牌。你可以选择放逐其中一张，然后将其打
出。如果打出的卡牌为单位，则可以选择将其打出到此处。回收其余的卡牌。
```

#### CHG-4B-T2ER-SFD-170-EV-EN-ER-0043  —  `R-CARD-SFD-170`  —  card:SFD-170 (Rek'Sai, Swarm Queen / 雷克塞)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-170` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0043 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When I attack, you may reveal the top 2 cards of your Main Deck. You may play one.
Then recycle the rest. If the played card is a unit, you may play it here.
```

**new_content**:

```
When I attack, you may reveal the top 2 cards of your Main Deck. You may banish
one, then play it. If it is a unit, you may play it here. Recycle the rest.
```

### `R-CARD-SFD-170a`  —  card:SFD-170a (Rek'Sai, Swarm Queen / 雷克塞) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-170a-EV-CN-ER-0073  —  `R-CARD-SFD-170a`  —  card:SFD-170a (Rek'Sai, Swarm Queen / 雷克塞)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-170a` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0073 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当我进攻时，你可以选择展示你主牌堆顶部的两张牌。你可以选择打出其中一张牌，然后回收其
余的卡牌。如果以此方式打出的卡牌为单位，则可以选择将其打出到此处。
```

**new_content**:

```
当我进攻时，你可以选择展示你主牌堆顶部的两张牌。你可以选择放逐其中一张，然后将其打
出。如果打出的卡牌为单位，则可以选择将其打出到此处。回收其余的卡牌。
```

#### CHG-4B-T2ER-SFD-170a-EV-EN-ER-0043  —  `R-CARD-SFD-170a`  —  card:SFD-170a (Rek'Sai, Swarm Queen / 雷克塞)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-170a` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0043 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When I attack, you may reveal the top 2 cards of your Main Deck. You may play one.
Then recycle the rest. If the played card is a unit, you may play it here.
```

**new_content**:

```
When I attack, you may reveal the top 2 cards of your Main Deck. You may banish
one, then play it. If it is a unit, you may play it here. Recycle the rest.
```

### `R-CARD-SFD-184`  —  card:SFD-184 (Relentless Pursuit / 冷酷追击) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-184-EV-CN-ER-0033  —  `R-CARD-SFD-184`  —  card:SFD-184 (Relentless Pursuit / 冷酷追击)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-184` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0033 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[迅捷]（可在你的回合或法术对决中打出。）
移动一名友方单位。你可以选择为其贴附其控制者的一件武装。在本回合内，该单位拥有“当我征
服一处战场时，你可以选择将我移动到我的基地”。
```

**new_content**:

```
[迅捷]（可在你的回合或法术对决中打出。）
移动一名友方单位。你可以选择为其贴附其控制者的最多一件武装。在本回合内，该单位拥有“当
我征服一处战场时，你可以选择将我移动到我的基地”。
```

#### CHG-4B-T2ER-SFD-184-EV-EN-ER-0051  —  `R-CARD-SFD-184`  —  card:SFD-184 (Relentless Pursuit / 冷酷追击)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-184` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `06_2026-04-03_Unleashed_Errata.pdf` |
| version | `v2026` |
| date | `2026-04-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0051 (source_017) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Action] (Play on your turn or in showdowns.)
Move a friendly unit. You may attach an Equipment with the same controller to it. This turn, that unit has "When I conquer, you may move
me to my base."
```

**new_content**:

```
[Action] (Play on your turn or in showdowns.)
Move a friendly unit. You may attach up to one Equipment with the same controller to it. This turn, that unit has "When I conquer, you
may move me to my base."
```

### `R-CARD-SFD-187`  —  card:SFD-187 (Void Burrower / 虚空遁地兽) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-187-EV-CN-ER-0076  —  `R-CARD-SFD-187`  —  card:SFD-187 (Void Burrower / 虚空遁地兽)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-187` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0076 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你征服一处战场时，你可以选择让我变为休眠状态，以此展示你主牌堆顶部的两张牌。你可以
选择打出其中一张牌，然后回收其余的卡牌。
```

**new_content**:

```
当你征服一处战场时，你可以选择让我变为休眠状态，以此展示你主牌堆顶部的两张牌。你可以
选择放逐其中一张，然后将其打出。回收其余的卡牌。
```

#### CHG-4B-T2ER-SFD-187-EV-EN-ER-0046  —  `R-CARD-SFD-187`  —  card:SFD-187 (Void Burrower / 虚空遁地兽)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-187` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0046 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When you conquer, you may exhaust me to reveal the top 2 cards of your Main
Deck. You may play one. Then recycle the rest.
```

**new_content**:

```
When you conquer, you may exhaust me to reveal the top 2 cards of your Main
Deck. You may banish one, then play it. Recycle the rest.
```

### `R-CARD-SFD-188`  —  card:SFD-188 (Void Rush / 虚空猛冲) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-188-EV-CN-ER-0077  —  `R-CARD-SFD-188`  —  card:SFD-188 (Void Rush / 虚空猛冲)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-188` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0077 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
展示你主牌堆顶部的两张牌。你可以选择其中一张，将其费用减少[2]后打出。抽取其中未以此方
式打出的卡牌。
```

**new_content**:

```
展示你主牌堆顶部的两张牌。你可以选择放逐其中一张，然后将其打出，其费用减少[2]。抽取其
中未被放逐的卡牌。
```

#### CHG-4B-T2ER-SFD-188-EV-EN-ER-0047  —  `R-CARD-SFD-188`  —  card:SFD-188 (Void Rush / 虚空猛冲)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-188` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0047 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
Reveal the top 2 cards of your Main Deck. You may play one of them, reducing its
cost by [2]. Draw any you did not play this way.
```

**new_content**:

```
Reveal the top 2 cards of your Main Deck. You may banish one, then play it,
reducing its cost by [2]. Draw any you didn't banish.
```

### `R-CARD-SFD-198`  —  card:SFD-198 (Arise! / 沙兵现身) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-198-EV-CN-ER-0066  —  `R-CARD-SFD-198`  —  card:SFD-198 (Arise! / 沙兵现身)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-198` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `effect_change` |
| reason | official errata EV-CN-ER-0066 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
你每控制一件武装，便打出一名2[M]的“黄沙士兵”。然后让两名“黄沙士兵”变为活跃状态。
```

**new_content**:

```
你每控制一件武装，便打出一名2[M]的“黄沙士兵”。然后进行一次：让其中最多两名“黄沙士兵”
变为活跃状态。
```

#### CHG-4B-T2ER-SFD-198-EV-EN-ER-0036  —  `R-CARD-SFD-198`  —  card:SFD-198 (Arise! / 沙兵现身)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-198` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `effect_change` |
| reason | official errata EV-EN-ER-0036 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
Play a 2 [M] Sand Soldier unit token for each Equipment you control. Then ready
two of them.
```

**new_content**:

```
Play a 2 [M] Sand Soldier unit token for each Equipment you control. Then do this:
Ready up to two of them.
```

### `R-CARD-SFD-207`  —  card:SFD-207 (Emperor's Dais / 帝王神坛) — 本规则共 3 条变更

#### CHG-4B-T2ER-SFD-207-EV-CN-ER-0055  —  `R-CARD-SFD-207`  —  card:SFD-207 (Emperor's Dais / 帝王神坛)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-207` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0055 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: zh translation-fix errata superseded by later zh errata on same card |

**original_content**:

```
当你征服此处时，你可以选择支付[1]并让你在此处控制的一名单位返回其所属的手牌，以此在此
处打出一名2 战力的“黄沙士兵”。
```

**new_content**:

```
当你征服此处时，你可以选择支付[1]并让你在此处控制的一名单位返回其所属的手牌。若如此
做，则在此处打出一名2[S]的“黄沙士兵”。
```

#### CHG-4B-T2ER-SFD-207-EV-CN-ER-0082  —  `R-CARD-SFD-207`  —  card:SFD-207 (Emperor's Dais / 帝王神坛)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-207` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `10_2026-07-24_9fe1f19110dd4678a6ad7bd96e791bba.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0082 (source_010) applied per Stage 4B; effective_scope=printed_text_alignment |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你征服此处时，你可以选择支付[1]并让你在此处控制的一名单位返回其所属的手牌。若如此
做，则在此处打出一名2[M]的“黄沙士兵”。
```

**new_content**:

```
当你征服此处时，你可以选择支付[1]并让你在此处控制的一名单位返回其所属的手牌，以此在此
处打出一名2[M]的“黄沙士兵”单位指示物。
```

#### CHG-4B-T2ER-SFD-207-EV-EN-ER-0060  —  `R-CARD-SFD-207`  —  card:SFD-207 (Emperor's Dais / 帝王神坛)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-207` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `09_2026-07-23_Vendetta_Errata.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0060 (source_020) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When you conquer here, you may pay [1] and return a unit you control here to its owner's hand. If you do, play a 2 [M] Sand Soldier unit
token here.
```

**new_content**:

```
When you conquer here, you may pay [1] and return a unit you control here to its owner's hand to play a 2 [M] Sand Soldier unit token
here.
```

### `R-CARD-SFD-209`  —  card:SFD-209 (Forgotten Monument / 遗忘丰碑) — 本规则共 1 条变更

#### CHG-4B-T2ER-SFD-209-EV-CN-ER-0080  —  `R-CARD-SFD-209`  —  card:SFD-209 (Forgotten Monument / 遗忘丰碑)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-209` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0080 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
每名玩家在各自的第三回合开始前，无法从此处获得分数。
```

**new_content**:

```
每名玩家在各自的第三回合开始前，无法从此处得分。
```

### `R-CARD-SFD-213`  —  card:SFD-213 (Ornn's Forge / 奥恩的锻炉) — 本规则共 1 条变更

#### CHG-4B-T2ER-SFD-213-EV-CN-ER-0054  —  `R-CARD-SFD-213`  —  card:SFD-213 (Ornn's Forge / 奥恩的锻炉)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-213` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0054 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
如果此战场受你控制，则每回合打出的第一件友方装备的费用减少[1]，不包括指示物。
```

**new_content**:

```
如果此战场受你控制，则每回合打出的第一件友方非指示物装备的费用减少[1]。
```

### `R-CARD-SFD-218`  —  card:SFD-218 (Sunken Temple / 沉没神庙) — 本规则共 1 条变更

#### CHG-4B-T2ER-SFD-218-EV-CN-ER-0079  —  `R-CARD-SFD-218`  —  card:SFD-218 (Sunken Temple / 沉没神庙)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-218` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0079 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你征服此处时，如果此战场上留存至少一名[强力]单位，则你可以选择支付[1]来抽一张牌。
（战力达到5 或以上时，即为强力单位。）
```

**new_content**:

```
当你以[强力]单位征服此处时，你可以选择支付[1]来抽一张牌。（战力达到5 或以上时，即为强
力单位。）
```

### `R-CARD-SFD-230*`  —  card:SFD-230* (Teemo, Strategist / 提莫) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-230*-EV-CN-ER-0023  —  `R-CARD-SFD-230*`  —  card:SFD-230* (Teemo, Strategist / 提莫)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-230*` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0023 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守一处战场、或从正面朝下的[待命]状态中打出时，展示你主牌堆顶部的五张牌，当中每
有一张带有[待命]技能的卡牌，就对此处的一名敌方单位造成1 点伤害，然后将展示的牌回收。
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守时，选择一名此处的敌方单位，展示你主牌堆顶部的五张牌。当中每有一张带有[待命]
技能的卡牌，便对该单位造成1 点伤害，然后将展示的牌回收。
```

#### CHG-4B-T2ER-SFD-230*-EV-EN-ER-0024  —  `R-CARD-SFD-230*`  —  card:SFD-230* (Teemo, Strategist / 提莫)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-230*` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0024 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
When I defend or I'm played from [Hidden], reveal the top 5 cards of your Main
Deck. Deal 1 to an enemy unit here for each card with [Hidden], then recycle them.
```

**new_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
When I defend, choose an enemy unit here and reveal the top 5 cards of your Main
Deck. Deal 1 to that unit for each card with [Hidden] revealed this way, then recycle
the revealed cards.
```

### `R-CARD-SFD-230`  —  card:SFD-230 (Teemo, Strategist / 提莫) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-230-EV-CN-ER-0023  —  `R-CARD-SFD-230`  —  card:SFD-230 (Teemo, Strategist / 提莫)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-230` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `condition_change` |
| reason | official errata EV-CN-ER-0023 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守一处战场、或从正面朝下的[待命]状态中打出时，展示你主牌堆顶部的五张牌，当中每
有一张带有[待命]技能的卡牌，就对此处的一名敌方单位造成1 点伤害，然后将展示的牌回收。
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
当我防守时，选择一名此处的敌方单位，展示你主牌堆顶部的五张牌。当中每有一张带有[待命]
技能的卡牌，便对该单位造成1 点伤害，然后将展示的牌回收。
```

#### CHG-4B-T2ER-SFD-230-EV-EN-ER-0024  —  `R-CARD-SFD-230`  —  card:SFD-230 (Teemo, Strategist / 提莫)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-230` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0024 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
When I defend or I'm played from [Hidden], reveal the top 5 cards of your Main
Deck. Deal 1 to an enemy unit here for each card with [Hidden], then recycle them.
```

**new_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
When I defend, choose an enemy unit here and reveal the top 5 cards of your Main
Deck. Deal 1 to that unit for each card with [Hidden] revealed this way, then recycle
the revealed cards.
```

### `R-CARD-SFD-233*`  —  card:SFD-233* (Yone, Blademaster / 永恩) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-233*-EV-CN-ER-0078  —  `R-CARD-SFD-233*`  —  card:SFD-233* (Yone, Blademaster / 永恩)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-233*` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0078 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[百炼]（当你打出我时，你可以选择为我[装配]你的一件武装，其装配费用减少[A]。可选择已贴
附的武装。）
当我征服一处开放的战场时，对基地中的一名敌方单位造成等同于我战力的伤害。
```

**new_content**:

```
[百炼]（当你打出我时，你可以选择为我[装配]你的一件武装，其装配费用减少[A]。可选择已贴
附的武装。）
当我征服一处未受控制的战场时，对基地中的一名敌方单位造成等同于我战力的伤害。
```

#### CHG-4B-T2ER-SFD-233*-EV-EN-ER-0048  —  `R-CARD-SFD-233*`  —  card:SFD-233* (Yone, Blademaster / 永恩)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-233*` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0048 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Weaponmaster] (When you play me, you may [Equip] one of your Equipment to
me for [A] less, even if it's already attached.)
When I conquer an open battlefield, deal damage equal to my Might to an enemy
unit in a base.
```

**new_content**:

```
[Weaponmaster] (When you play me, you may [Equip] one of your Equipment to
me for [A] less, even if it's already attached.)
When I conquer a battlefield that was uncontrolled, deal damage equal to my
Might to an enemy unit in a base.
```

### `R-CARD-SFD-233`  —  card:SFD-233 (Yone, Blademaster / 永恩) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-233-EV-CN-ER-0078  —  `R-CARD-SFD-233`  —  card:SFD-233 (Yone, Blademaster / 永恩)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-233` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0078 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[百炼]（当你打出我时，你可以选择为我[装配]你的一件武装，其装配费用减少[A]。可选择已贴
附的武装。）
当我征服一处开放的战场时，对基地中的一名敌方单位造成等同于我战力的伤害。
```

**new_content**:

```
[百炼]（当你打出我时，你可以选择为我[装配]你的一件武装，其装配费用减少[A]。可选择已贴
附的武装。）
当我征服一处未受控制的战场时，对基地中的一名敌方单位造成等同于我战力的伤害。
```

#### CHG-4B-T2ER-SFD-233-EV-EN-ER-0048  —  `R-CARD-SFD-233`  —  card:SFD-233 (Yone, Blademaster / 永恩)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-233` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0048 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Weaponmaster] (When you play me, you may [Equip] one of your Equipment to
me for [A] less, even if it's already attached.)
When I conquer an open battlefield, deal damage equal to my Might to an enemy
unit in a base.
```

**new_content**:

```
[Weaponmaster] (When you play me, you may [Equip] one of your Equipment to
me for [A] less, even if it's already attached.)
When I conquer a battlefield that was uncontrolled, deal damage equal to my
Might to an enemy unit in a base.
```

### `R-CARD-SFD-237*`  —  card:SFD-237* (Karma, Channeler / 卡尔玛) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-237*-EV-CN-ER-0012  —  `R-CARD-SFD-237*`  —  card:SFD-237* (Karma, Channeler / 卡尔玛)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-237*` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0012 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[预知]（当你打出我时，查看主牌堆顶部的一张牌，你可以选择将其回收。）
每当你回收任意数量的卡牌时，给予一名友方单位增益。（如果该单位未拥有增益，则获得一个
[M]+1 增益。符文不被视为卡牌。）
```

**new_content**:

```
[预知]（当你打出我时，查看主牌堆顶部的一张牌，你可以选择将其回收。）
每当你将任意数量的卡牌回收到自己的主牌堆时，给予一名友方单位增益。（如果该单位未拥有
增益，则获得一个[M]+1 增益。符文不被视为卡牌。）
```

#### CHG-4B-T2ER-SFD-237*-EV-EN-ER-0013  —  `R-CARD-SFD-237*`  —  card:SFD-237* (Karma, Channeler / 卡尔玛)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-237*` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0013 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Vision] (When you play me, look at the top card of your Main Deck. You may recycle
it.)
When you recycle one or more cards, buff a friendly unit. (If it doesn't have a buff, it
gets a +1 [M] buff. Runes aren't cards.)
```

**new_content**:

```
[Vision] (When you play me, look at the top card of your Main Deck. You may recycle
it.)
When you recycle one or more cards to your Main Deck, buff a friendly unit. (If it
doesn't have a buff, it gets a +1 [M] buff. Runes aren't cards.)
```

### `R-CARD-SFD-237`  —  card:SFD-237 (Karma, Channeler / 卡尔玛) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-237-EV-CN-ER-0012  —  `R-CARD-SFD-237`  —  card:SFD-237 (Karma, Channeler / 卡尔玛)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-237` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0012 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[预知]（当你打出我时，查看主牌堆顶部的一张牌，你可以选择将其回收。）
每当你回收任意数量的卡牌时，给予一名友方单位增益。（如果该单位未拥有增益，则获得一个
[M]+1 增益。符文不被视为卡牌。）
```

**new_content**:

```
[预知]（当你打出我时，查看主牌堆顶部的一张牌，你可以选择将其回收。）
每当你将任意数量的卡牌回收到自己的主牌堆时，给予一名友方单位增益。（如果该单位未拥有
增益，则获得一个[M]+1 增益。符文不被视为卡牌。）
```

#### CHG-4B-T2ER-SFD-237-EV-EN-ER-0013  —  `R-CARD-SFD-237`  —  card:SFD-237 (Karma, Channeler / 卡尔玛)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-237` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0013 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Vision] (When you play me, look at the top card of your Main Deck. You may recycle
it.)
When you recycle one or more cards, buff a friendly unit. (If it doesn't have a buff, it
gets a +1 [M] buff. Runes aren't cards.)
```

**new_content**:

```
[Vision] (When you play me, look at the top card of your Main Deck. You may recycle
it.)
When you recycle one or more cards to your Main Deck, buff a friendly unit. (If it
doesn't have a buff, it gets a +1 [M] buff. Runes aren't cards.)
```

### `R-CARD-SFD-243`  —  card:SFD-243 (Void Burrower / 虚空遁地兽) — 本规则共 2 条变更

#### CHG-4B-T2ER-SFD-243-EV-CN-ER-0076  —  `R-CARD-SFD-243`  —  card:SFD-243 (Void Burrower / 虚空遁地兽)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-243` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `04_2026-04-15_铸魂淬炼系列_勘误汇总_260114.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0076 (source_004) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你征服一处战场时，你可以选择让我变为休眠状态，以此展示你主牌堆顶部的两张牌。你可以
选择打出其中一张牌，然后回收其余的卡牌。
```

**new_content**:

```
当你征服一处战场时，你可以选择让我变为休眠状态，以此展示你主牌堆顶部的两张牌。你可以
选择放逐其中一张，然后将其打出。回收其余的卡牌。
```

#### CHG-4B-T2ER-SFD-243-EV-EN-ER-0046  —  `R-CARD-SFD-243`  —  card:SFD-243 (Void Burrower / 虚空遁地兽)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-243` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `04_2026-01-14_Spiritforged_Errata.pdf` |
| version | `v2026` |
| date | `2026-01-14` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0046 (source_015) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When you conquer, you may exhaust me to reveal the top 2 cards of your Main
Deck. You may play one. Then recycle the rest.
```

**new_content**:

```
When you conquer, you may exhaust me to reveal the top 2 cards of your Main
Deck. You may banish one, then play it. Recycle the rest.
```

### `R-CARD-UNL-079`  —  card:UNL-079 (Diana, Lunari / 黛安娜) — 本规则共 3 条变更

#### CHG-4B-T2ER-UNL-079-EV-CN-ER-0048  —  `R-CARD-UNL-079`  —  card:UNL-079 (Diana, Lunari / 黛安娜)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-079` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0048 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: zh translation-fix errata superseded by later zh errata on same card |

**original_content**:

```
当法术对决在此处开始时，你可以选择支付[1]，以此进行洞察，然后展示你主牌堆顶部的一张
牌。如果是一张法术牌，则抽取该卡牌。（洞察时，查看你主牌堆顶部的一张牌。你可以选择将
其回收。）
```

**new_content**:

```
当法术对决在此处开始时，你可以选择支付[1]。若如此做，则进行[洞察]，然后展示你主牌堆顶
部的一张牌。如果是一张法术牌，则抽取该卡牌。（洞察时，查看你主牌堆顶部的一张牌。你可
以选择将其回收。）
```

#### CHG-4B-T2ER-UNL-079-EV-CN-ER-0084  —  `R-CARD-UNL-079`  —  card:UNL-079 (Diana, Lunari / 黛安娜)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-079` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `10_2026-07-24_9fe1f19110dd4678a6ad7bd96e791bba.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0084 (source_010) applied per Stage 4B; effective_scope=printed_text_alignment |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当法术对决在此处开始时，你可以选择支付[1]。若如此做，则进行[洞察]，然后展示你主牌堆顶
部的一张牌。如果是一张法术牌，则抽取该卡牌。（洞察时，查看你主牌堆顶部的一张牌。你可
以选择将其回收。）
```

**new_content**:

```
当法术对决在此处开始时，你可以选择支付[1]，以此进行[洞察]，然后展示你主牌堆顶部的一张
牌。如果是一张法术牌，则抽取该卡牌。（洞察时，查看你主牌堆顶部的一张牌。你可以选择将
其回收。）
```

#### CHG-4B-T2ER-UNL-079-EV-EN-ER-0062  —  `R-CARD-UNL-079`  —  card:UNL-079 (Diana, Lunari / 黛安娜)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-079` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `09_2026-07-23_Vendetta_Errata.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0062 (source_020) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When a showdown begins here, you may pay [1]. If you do, [Predict], then reveal the top card of your Main Deck. If it's a spell, draw it. (To
Predict, look at the top card of your Main Deck. You may recycle it.)
```

**new_content**:

```
When a showdown begins here, you may pay [1] to [Predict], then reveal the top card of your Main Deck. If it's a spell, draw it. (To
Predict, look at the top card of your Main Deck. You may recycle it.)
```

### `R-CARD-UNL-079a`  —  card:UNL-079a (Diana, Lunari / 黛安娜) — 本规则共 3 条变更

#### CHG-4B-T2ER-UNL-079a-EV-CN-ER-0048  —  `R-CARD-UNL-079a`  —  card:UNL-079a (Diana, Lunari / 黛安娜)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-079a` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0048 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: zh translation-fix errata superseded by later zh errata on same card |

**original_content**:

```
当法术对决在此处开始时，你可以选择支付[1]，以此进行洞察，然后展示你主牌堆顶部的一张
牌。如果是一张法术牌，则抽取该卡牌。（洞察时，查看你主牌堆顶部的一张牌。你可以选择将
其回收。）
```

**new_content**:

```
当法术对决在此处开始时，你可以选择支付[1]。若如此做，则进行[洞察]，然后展示你主牌堆顶
部的一张牌。如果是一张法术牌，则抽取该卡牌。（洞察时，查看你主牌堆顶部的一张牌。你可
以选择将其回收。）
```

#### CHG-4B-T2ER-UNL-079a-EV-CN-ER-0084  —  `R-CARD-UNL-079a`  —  card:UNL-079a (Diana, Lunari / 黛安娜)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-079a` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `10_2026-07-24_9fe1f19110dd4678a6ad7bd96e791bba.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0084 (source_010) applied per Stage 4B; effective_scope=printed_text_alignment |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当法术对决在此处开始时，你可以选择支付[1]。若如此做，则进行[洞察]，然后展示你主牌堆顶
部的一张牌。如果是一张法术牌，则抽取该卡牌。（洞察时，查看你主牌堆顶部的一张牌。你可
以选择将其回收。）
```

**new_content**:

```
当法术对决在此处开始时，你可以选择支付[1]，以此进行[洞察]，然后展示你主牌堆顶部的一张
牌。如果是一张法术牌，则抽取该卡牌。（洞察时，查看你主牌堆顶部的一张牌。你可以选择将
其回收。）
```

#### CHG-4B-T2ER-UNL-079a-EV-EN-ER-0062  —  `R-CARD-UNL-079a`  —  card:UNL-079a (Diana, Lunari / 黛安娜)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-079a` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `09_2026-07-23_Vendetta_Errata.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0062 (source_020) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When a showdown begins here, you may pay [1]. If you do, [Predict], then reveal the top card of your Main Deck. If it's a spell, draw it. (To
Predict, look at the top card of your Main Deck. You may recycle it.)
```

**new_content**:

```
When a showdown begins here, you may pay [1] to [Predict], then reveal the top card of your Main Deck. If it's a spell, draw it. (To
Predict, look at the top card of your Main Deck. You may recycle it.)
```

### `R-CARD-UNL-081`  —  card:UNL-081 (Keeper of Masks / 赐面守侍) — 本规则共 2 条变更

#### CHG-4B-T2ER-UNL-081-EV-CN-ER-0038  —  `R-CARD-UNL-081`  —  card:UNL-081 (Keeper of Masks / 赐面守侍)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-081` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `effect_change` |
| reason | official errata EV-CN-ER-0038 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
[瞬息]（在我控制者的下个开始阶段开始时，结算得分之前将我摧毁。）
当你打出我时，在此处打出两名“映像”。它们变为我的复制体。
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
[瞬息]（在我控制者的下个开始阶段开始时，结算得分之前将我摧毁。）
当你打出我时，在此处打出两名“映像”。然后进行一次：它们变为我的复制体。
```

#### CHG-4B-T2ER-UNL-081-EV-EN-ER-0056  —  `R-CARD-UNL-081`  —  card:UNL-081 (Keeper of Masks / 赐面守侍)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-081` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `06_2026-04-03_Unleashed_Errata.pdf` |
| version | `v2026` |
| date | `2026-04-03` |
| modification_type | `effect_change` |
| reason | official errata EV-EN-ER-0056 (source_017) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
[Temporary] (Kill me at the start of my controller's Beginning Phase, before scoring.)
When you play me, play two Reflection unit tokens here. They become copies of me.
```

**new_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
[Temporary] (Kill me at the start of my controller's Beginning Phase, before scoring.)
When you play me, play two Reflection unit tokens here. Then do this: They become copies of me.
```

### `R-CARD-UNL-087`  —  card:UNL-087 (Blue Sentinel / 苍蓝雕纹魔像) — 本规则共 1 条变更

#### CHG-4B-T2ER-UNL-087-EV-CN-ER-0042  —  `R-CARD-UNL-087`  —  card:UNL-087 (Blue Sentinel / 苍蓝雕纹魔像)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-087` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0042 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[坚守2]（如果我是防守方，则[S]+2。）
你据守此处时的据守效果额外触发一次。
当我据守一处战场时，你在下一个主阶段开始时[获得][A]。（获得费用资源的技能无法成为其他
法术的反应目标。）
```

**new_content**:

```
[坚守2]（如果我是防守方，则[S]+2。）
你据守此处时的据守效果额外触发一次。
当我据守一处战场时，在你的下一个主阶段开始时[获得][A]。（获得费用资源的技能无法成为其
他法术的反应目标。）
```

### `R-CARD-UNL-087a`  —  card:UNL-087a (Blue Sentinel / 苍蓝雕纹魔像) — 本规则共 1 条变更

#### CHG-4B-T2ER-UNL-087a-EV-CN-ER-0042  —  `R-CARD-UNL-087a`  —  card:UNL-087a (Blue Sentinel / 苍蓝雕纹魔像)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-087a` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0042 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[坚守2]（如果我是防守方，则[S]+2。）
你据守此处时的据守效果额外触发一次。
当我据守一处战场时，你在下一个主阶段开始时[获得][A]。（获得费用资源的技能无法成为其他
法术的反应目标。）
```

**new_content**:

```
[坚守2]（如果我是防守方，则[S]+2。）
你据守此处时的据守效果额外触发一次。
当我据守一处战场时，在你的下一个主阶段开始时[获得][A]。（获得费用资源的技能无法成为其
他法术的反应目标。）
```

### `R-CARD-UNL-088`  —  card:UNL-088 (Gutter Palace / 倾颓宫殿) — 本规则共 1 条变更

#### CHG-4B-T2ER-UNL-088-EV-CN-ER-0040  —  `R-CARD-UNL-088`  —  card:UNL-088 (Gutter Palace / 倾颓宫殿)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-088` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0040 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
在你的开始阶段开始时，如果你有且仅有四张手牌，且在各处战场上有且仅有你的四名单位，则
立即赢得对局。
弃置一张手牌，横置：打出一名1 战力的“战鹰”它拥有法盾。(对手必须支付[A]才能将其选作
法术或技能的目标。)
```

**new_content**:

```
在你的开始阶段开始时，如果你有且仅有四张手牌，且你在各处战场上有且仅有四名单位，则立
即赢得对局。
弃置一张手牌，[T]：打出一名1[S]的“战鹰”，它拥有[法盾]。（对手必须支付[A]才能将其选作
法术或技能的目标。）
```

### `R-CARD-UNL-106`  —  card:UNL-106 (Repulse / 击退) — 本规则共 1 条变更

#### CHG-4B-T2ER-UNL-106-EV-CN-ER-0041  —  `R-CARD-UNL-106`  —  card:UNL-106 (Repulse / 击退)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-106` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0041 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
反应（可在任意时机打出，甚至先于其他法术和技能的结算。）
选择战场上的一名友方单位。无效化一个只以该单位为目标的敌方法术或技能。
```

**new_content**:

```
[反应]（可在任意时机打出，甚至先于其他法术和技能的结算。）
选择战场上的一名友方单位。无效化一个以该单位为目标且不以其他友方单位为目标的敌方法术
或技能。
```

### `R-CARD-UNL-120`  —  card:UNL-120 (Rengar, Trophy Hunter / 雷恩加尔) — 本规则共 2 条变更

#### CHG-4B-T2ER-UNL-120-EV-CN-ER-0039  —  `R-CARD-UNL-120`  —  card:UNL-120 (Rengar, Trophy Hunter / 雷恩加尔)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-120` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0039 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[伏击]（你可以选择将我作为[反应]牌，打出到有己方单位的战场。）
我可以被打出至有敌方单位的战场（即使你在该处没有单位）。
```

**new_content**:

```
[伏击]（你可以选择将我作为[反应]牌，打出到有己方单位的战场。）
我可以[伏击]到有敌方单位的战场，即使你在该处没有单位。
```

#### CHG-4B-T2ER-UNL-120-EV-EN-ER-0057  —  `R-CARD-UNL-120`  —  card:UNL-120 (Rengar, Trophy Hunter / 雷恩加尔)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-120` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `06_2026-04-03_Unleashed_Errata.pdf` |
| version | `v2026` |
| date | `2026-04-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0057 (source_017) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Ambush] (You may play me as a [Reaction] to a battlefield where you have units.)
I can be played to a battlefield where there are enemy units (even if you don't have units there).
```

**new_content**:

```
[Ambush] (You may play me as a [Reaction] to a battlefield where you have units.)
I can [Ambush] to a battlefield where there are enemy units, even if you don't have units there.
```

### `R-CARD-UNL-120a`  —  card:UNL-120a (Rengar, Trophy Hunter / 雷恩加尔) — 本规则共 2 条变更

#### CHG-4B-T2ER-UNL-120a-EV-CN-ER-0039  —  `R-CARD-UNL-120a`  —  card:UNL-120a (Rengar, Trophy Hunter / 雷恩加尔)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-120a` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0039 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[伏击]（你可以选择将我作为[反应]牌，打出到有己方单位的战场。）
我可以被打出至有敌方单位的战场（即使你在该处没有单位）。
```

**new_content**:

```
[伏击]（你可以选择将我作为[反应]牌，打出到有己方单位的战场。）
我可以[伏击]到有敌方单位的战场，即使你在该处没有单位。
```

#### CHG-4B-T2ER-UNL-120a-EV-EN-ER-0057  —  `R-CARD-UNL-120a`  —  card:UNL-120a (Rengar, Trophy Hunter / 雷恩加尔)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-120a` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `06_2026-04-03_Unleashed_Errata.pdf` |
| version | `v2026` |
| date | `2026-04-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0057 (source_017) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Ambush] (You may play me as a [Reaction] to a battlefield where you have units.)
I can be played to a battlefield where there are enemy units (even if you don't have units there).
```

**new_content**:

```
[Ambush] (You may play me as a [Reaction] to a battlefield where you have units.)
I can [Ambush] to a battlefield where there are enemy units, even if you don't have units there.
```

### `R-CARD-UNL-139`  —  card:UNL-139 (Bone Skewer / 透骨尖钉) — 本规则共 2 条变更

#### CHG-4B-T2ER-UNL-139-EV-CN-ER-0035  —  `R-CARD-UNL-139`  —  card:UNL-139 (Bone Skewer / 透骨尖钉)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-139` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `effect_change` |
| reason | official errata EV-CN-ER-0035 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
选择一处战场。让一名对手展示自己的手牌。你可以从中选择一名单位。让该对手将该单位打出
到该战场，无视一切费用。当对手如此做时，[眩晕]该单位。（使其在本回合内无法造成战斗伤
害。）
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
选择一处战场。让一名对手展示自己的手牌。你可以从中选择一名单位。该对手将该单位打出到
该战场，无视一切费用。若其如此做，则进行一次：[眩晕]该单位。（使其在本回合内无法造成
战斗伤害。）
```

#### CHG-4B-T2ER-UNL-139-EV-EN-ER-0053  —  `R-CARD-UNL-139`  —  card:UNL-139 (Bone Skewer / 透骨尖钉)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-139` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `06_2026-04-03_Unleashed_Errata.pdf` |
| version | `v2026` |
| date | `2026-04-03` |
| modification_type | `effect_change` |
| reason | official errata EV-EN-ER-0053 (source_017) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
Choose a battlefield. An opponent reveals their hand. You may choose a unit from it. They play that unit to that battlefield, ignoring any
and all costs. When they do, [Stun] it. (It doesn't deal combat damage this turn.)
```

**new_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
Choose a battlefield. An opponent reveals their hand. You may choose a unit from it. They play that unit to that battlefield, ignoring any
and all costs. If they do, then do this: [Stun] it. (It doesn't deal combat damage this turn.)
```

### `R-CARD-UNL-166`  —  card:UNL-166 (Stalking Wolf / 追猎雪狼) — 本规则共 2 条变更

#### CHG-4B-T2ER-UNL-166-EV-CN-ER-0085  —  `R-CARD-UNL-166`  —  card:UNL-166 (Stalking Wolf / 追猎雪狼)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-166` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `10_2026-07-24_9fe1f19110dd4678a6ad7bd96e791bba.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0085 (source_010) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[伏击]（你可以选择将我作为[反应]牌，打出到有己方单位的战场。）
你必须摧毁一名自己控制的“鸟类”、“猫科”、“犬形”或“魄罗”属性单位，作为打出我的额外费用。
你可以选择将我打出至该单位所在的战场（即使你在该处没有其他单位）。
```

**new_content**:

```
[伏击]（你可以选择将我作为[反应]牌，打出到有己方单位的战场。）
你必须摧毁一名自己控制的“鸟类”、“猫科”、“犬形”或“魄罗”属性单位，作为打出我的额外费用。
你可以选择将我[伏击]至该单位所在的战场，即使你在该处没有其他单位。
```

#### CHG-4B-T2ER-UNL-166-EV-EN-ER-0063  —  `R-CARD-UNL-166`  —  card:UNL-166 (Stalking Wolf / 追猎雪狼)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-166` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `09_2026-07-23_Vendetta_Errata.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0063 (source_020) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Ambush] (You may play me as a [Reaction] to a battlefield where you have units.)
As an additional cost to play me, kill a Bird, Cat, Dog, or Poro you control. You may play me to its battlefield (even if you don't have other
units there).
```

**new_content**:

```
[Ambush] (You may play me as a [Reaction] to a battlefield where you have units.)
As an additional cost to play me, kill a Bird, Cat, Dog, or Poro you control. You may [Ambush] me to its battlefield, even if you don't have
other units there.
```

### `R-CARD-UNL-186`  —  card:UNL-186 (Death from Below / 涌泉之恨) — 本规则共 3 条变更

#### CHG-4B-T2ER-UNL-186-EV-CN-ER-0034  —  `R-CARD-UNL-186`  —  card:UNL-186 (Death from Below / 涌泉之恨)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-186` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `effect_change` |
| reason | official errata EV-CN-ER-0034 (source_003) applied per Stage 4B; effective_scope=english_card_text_only |
| final_conclusion | recorded: earlier zh errata in chain; canonical carried by later errata |

**original_content**:

```
摧毁战场上的一名单位。然后，如果该单位不高于3[M]，则你可以选择支付[A]，以此将此牌从废
牌堆中打出。
```

**new_content**:

```
摧毁战场上的一名单位。然后，如果该单位不高于3[M]，则进行一次：你可以选择支付[A]，以此
将此牌从废牌堆中打出。
```

#### CHG-4B-T2ER-UNL-186-EV-CN-ER-0090  —  `R-CARD-UNL-186`  —  card:UNL-186 (Death from Below / 涌泉之恨)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-186` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `10_2026-07-24_9fe1f19110dd4678a6ad7bd96e791bba.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0090 (source_010) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
摧毁战场上的一名单位。然后，如果该单位不高于3 战力，则进行一次：你可以选择支付[A]以此
将此牌从废牌堆中打出。
```

**new_content**:

```
摧毁战场上的一名单位。然后，如果该单位不高于3 战力，则进行一次：你可以选择支付[A]以此
将此牌从你的废牌堆中打出。
```

#### CHG-4B-T2ER-UNL-186-EV-EN-ER-0052  —  `R-CARD-UNL-186`  —  card:UNL-186 (Death from Below / 涌泉之恨)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-186` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `06_2026-04-03_Unleashed_Errata.pdf` |
| version | `v2026` |
| date | `2026-04-03` |
| modification_type | `effect_change` |
| reason | official errata EV-EN-ER-0052 (source_017) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
Kill a unit at a battlefield. Then, if it had 3 [M] or less, you may play this from your trash for [A].
```

**new_content**:

```
Kill a unit at a battlefield. Then, if it had 3 [M] or less, do this: You may play this from your trash for [A].
```

### `R-CARD-UNL-199`  —  card:UNL-199 (Deceiver / 诡术妖姬) — 本规则共 2 条变更

#### CHG-4B-T2ER-UNL-199-EV-CN-ER-0036  —  `R-CARD-UNL-199`  —  card:UNL-199 (Deceiver / 诡术妖姬)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-199` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `effect_change` |
| reason | official errata EV-CN-ER-0036 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你征服或据守一处战场时，你可以选择弃置一张手牌并让我变为休眠状态，以此在该处打出一
名处于活跃状态的“映像”。该“映像”变为该处另一名单位的复制体。让其获得[瞬息]。
```

**new_content**:

```
当你征服或据守一处战场时，你可以选择弃置一张手牌并让我变为休眠状态，以此在该处打出一
名处于活跃状态的“映像”。然后进行一次：该“映像”变为该处另一名单位的复制体。让其获得[瞬
息]。
```

#### CHG-4B-T2ER-UNL-199-EV-EN-ER-0054  —  `R-CARD-UNL-199`  —  card:UNL-199 (Deceiver / 诡术妖姬)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-199` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `06_2026-04-03_Unleashed_Errata.pdf` |
| version | `v2026` |
| date | `2026-04-03` |
| modification_type | `effect_change` |
| reason | official errata EV-EN-ER-0054 (source_017) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When you conquer or hold, you may discard 1 and exhaust me to play a ready Reflection unit token there. It becomes a copy of another
unit there. Give it [Temporary].
```

**new_content**:

```
When you conquer or hold, you may discard 1 and exhaust me to play a ready Reflection unit token there. Then do this: It becomes a
copy of another unit there. Give it [Temporary].
```

### `R-CARD-UNL-200`  —  card:UNL-200 (Mirror Image / 镜花水月) — 本规则共 2 条变更

#### CHG-4B-T2ER-UNL-200-EV-CN-ER-0037  —  `R-CARD-UNL-200`  —  card:UNL-200 (Mirror Image / 镜花水月)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-200` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `effect_change` |
| reason | official errata EV-CN-ER-0037 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
选择一名单位。将一名活跃状态的“映像”打出到你的基地。该“映像”变为所选单位的复制体。并让
其获得[瞬息]。（在其控制者的开始阶段开始时，结算得分之前将其摧毁。）
```

**new_content**:

```
选择一名单位。将一名活跃状态的“映像”打出到你的基地。然后进行一次：该“映像”变为所选单位
的复制体。让其获得[瞬息]。（在其控制者的开始阶段开始时，结算得分之前将其摧毁。）
```

#### CHG-4B-T2ER-UNL-200-EV-EN-ER-0055  —  `R-CARD-UNL-200`  —  card:UNL-200 (Mirror Image / 镜花水月)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-200` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `06_2026-04-03_Unleashed_Errata.pdf` |
| version | `v2026` |
| date | `2026-04-03` |
| modification_type | `effect_change` |
| reason | official errata EV-EN-ER-0055 (source_017) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
Choose a unit. Play a ready Reflection unit token to your base. It becomes a copy of that unit. Give it [Temporary]. (Kill it at the start of its
controller's Beginning Phase, before scoring.)
```

**new_content**:

```
Choose a unit. Play a ready Reflection unit token to your base. Then do this: It becomes a copy of that unit. Give it [Temporary]. (Kill it at
the start of its controller's Beginning Phase, before scoring.)
```

### `R-CARD-UNL-235*`  —  card:UNL-235* (Deceiver / 诡术妖姬) — 本规则共 2 条变更

#### CHG-4B-T2ER-UNL-235*-EV-CN-ER-0036  —  `R-CARD-UNL-235*`  —  card:UNL-235* (Deceiver / 诡术妖姬)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-235*` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `effect_change` |
| reason | official errata EV-CN-ER-0036 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你征服或据守一处战场时，你可以选择弃置一张手牌并让我变为休眠状态，以此在该处打出一
名处于活跃状态的“映像”。该“映像”变为该处另一名单位的复制体。让其获得[瞬息]。
```

**new_content**:

```
当你征服或据守一处战场时，你可以选择弃置一张手牌并让我变为休眠状态，以此在该处打出一
名处于活跃状态的“映像”。然后进行一次：该“映像”变为该处另一名单位的复制体。让其获得[瞬
息]。
```

#### CHG-4B-T2ER-UNL-235*-EV-EN-ER-0054  —  `R-CARD-UNL-235*`  —  card:UNL-235* (Deceiver / 诡术妖姬)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-235*` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `06_2026-04-03_Unleashed_Errata.pdf` |
| version | `v2026` |
| date | `2026-04-03` |
| modification_type | `effect_change` |
| reason | official errata EV-EN-ER-0054 (source_017) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When you conquer or hold, you may discard 1 and exhaust me to play a ready Reflection unit token there. It becomes a copy of another
unit there. Give it [Temporary].
```

**new_content**:

```
When you conquer or hold, you may discard 1 and exhaust me to play a ready Reflection unit token there. Then do this: It becomes a
copy of another unit there. Give it [Temporary].
```

### `R-CARD-UNL-235`  —  card:UNL-235 (Deceiver / 诡术妖姬) — 本规则共 2 条变更

#### CHG-4B-T2ER-UNL-235-EV-CN-ER-0036  —  `R-CARD-UNL-235`  —  card:UNL-235 (Deceiver / 诡术妖姬)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-235` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `effect_change` |
| reason | official errata EV-CN-ER-0036 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你征服或据守一处战场时，你可以选择弃置一张手牌并让我变为休眠状态，以此在该处打出一
名处于活跃状态的“映像”。该“映像”变为该处另一名单位的复制体。让其获得[瞬息]。
```

**new_content**:

```
当你征服或据守一处战场时，你可以选择弃置一张手牌并让我变为休眠状态，以此在该处打出一
名处于活跃状态的“映像”。然后进行一次：该“映像”变为该处另一名单位的复制体。让其获得[瞬
息]。
```

#### CHG-4B-T2ER-UNL-235-EV-EN-ER-0054  —  `R-CARD-UNL-235`  —  card:UNL-235 (Deceiver / 诡术妖姬)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-235` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `06_2026-04-03_Unleashed_Errata.pdf` |
| version | `v2026` |
| date | `2026-04-03` |
| modification_type | `effect_change` |
| reason | official errata EV-EN-ER-0054 (source_017) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When you conquer or hold, you may discard 1 and exhaust me to play a ready Reflection unit token there. It becomes a copy of another
unit there. Give it [Temporary].
```

**new_content**:

```
When you conquer or hold, you may discard 1 and exhaust me to play a ready Reflection unit token there. Then do this: It becomes a
copy of another unit there. Give it [Temporary].
```

### `R-CARD-VEN-034`  —  card:VEN-034 (Resonating Strike / 回音击) — 本规则共 2 条变更

#### CHG-4B-T2ER-VEN-034-EV-CN-ER-0088  —  `R-CARD-VEN-034`  —  card:VEN-034 (Resonating Strike / 回音击)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-VEN-034` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `10_2026-07-24_9fe1f19110dd4678a6ad7bd96e791bba.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0088 (source_010) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
[反应]（可在你的回合或法术对决中打出。）
选择一处受你控制的战场，和一名位于其他位置且受你控制的单位。将该单位移动到该战场，并
给予其在本回合内[M]+2。
```

**new_content**:

```
[待命]（支付[A]正面朝下放置此牌，之后可支付[0]将其当作反应牌打出。）
[反应]（可在任意时机打出，甚至先于其他法术和技能的结算。）
选择一处受你控制的战场，和一名位于其他位置且受你控制的单位。将该单位移动到该战场，并
给予其在本回合内[M]+2。
```

#### CHG-4B-T2ER-VEN-034-EV-EN-ER-0066  —  `R-CARD-VEN-034`  —  card:VEN-034 (Resonating Strike / 回音击)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-VEN-034` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `09_2026-07-23_Vendetta_Errata.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0066 (source_020) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
[Reaction] (Play on your turn or in showdowns.)
Choose a battlefield you control and a unit you control at a different location. Move that unit to that battlefield and give it +2 [S] this
turn.
```

**new_content**:

```
[Hidden] (Hide now for [A] to react with later for [0].)
[Reaction] (Play any time, even before spells and abilities resolve.)
Choose a battlefield you control and a unit you control at a different location. Move that unit to that battlefield and give it +2 [S] this
turn.
```

### `R-CARD-VEN-044`  —  card:VEN-044 (Astral Heron / 星界灵鹭) — 本规则共 2 条变更

#### CHG-4B-T2ER-VEN-044-EV-CN-ER-0086  —  `R-CARD-VEN-044`  —  card:VEN-044 (Astral Heron / 星界灵鹭)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-VEN-044` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `10_2026-07-24_9fe1f19110dd4678a6ad7bd96e791bba.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0086 (source_010) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你打出每回合你的首张卡牌时，如果我位于战场上，则你下一张卡牌的费用减少[2]和[A][A]。
```

**new_content**:

```
当你打出每回合你的首张卡牌时，如果我位于战场上，则你在本回合内打出的下一张卡牌的费用
减少[2]和[A][A]。
```

#### CHG-4B-T2ER-VEN-044-EV-EN-ER-0064  —  `R-CARD-VEN-044`  —  card:VEN-044 (Astral Heron / 星界灵鹭)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-VEN-044` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `09_2026-07-23_Vendetta_Errata.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0064 (source_020) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
When you play your first card each turn, if I'm at a battlefield, your next card costs [2][A][A] less.
```

**new_content**:

```
When you play your first card each turn, if I'm at a battlefield, the next card you play this turn costs [2][A][A] less.
```

### `R-CARD-VEN-079`  —  card:VEN-079 (Dame the Despoiler / 夺魂钩 妲姆) — 本规则共 1 条变更

#### CHG-4B-T2ER-VEN-079-EV-CN-ER-0093  —  `R-CARD-VEN-079`  —  card:VEN-079 (Dame the Despoiler / 夺魂钩 妲姆)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-VEN-079` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `10_2026-07-24_9fe1f19110dd4678a6ad7bd96e791bba.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0093 (source_010) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[强化] [5][C]（支付[5]和[C]：强化我。仅在未强化时可用。）
[已强化][>] 当我进攻或防守时，选择此处一名战力大于我的单位。在本回合内将我的战力提升至
与其战力相同，然后给予我在本回合内[S]+1。
```

**new_content**:

```
[强化] [5][C]（支付[5]和[C]：强化我。仅在未强化时可用。）
[已强化][>] 当我进攻或防守时，选择此处的一名单位。在本回合内将我的战力提升至与其战力相
同，然后给予我在本回合内[S]+1。
```

### `R-CARD-VEN-086`  —  card:VEN-086 (Gangplank, Naval / 普朗克) — 本规则共 2 条变更

#### CHG-4B-T2ER-VEN-086-EV-CN-ER-0087  —  `R-CARD-VEN-086`  —  card:VEN-086 (Gangplank, Naval / 普朗克)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-VEN-086` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `10_2026-07-24_9fe1f19110dd4678a6ad7bd96e791bba.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0087 (source_010) applied per Stage 4B; effective_scope=printed_text_alignment |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[强化] [C][C]（支付[C][C]：强化我。仅在未强化时可用。）
[已强化][>] 如果一个将我选作目标的法术或技能将眩晕我、或给予我-[M]、或把我送回手牌，则
改为给予我在本回合内[M]+3。
```

**new_content**:

```
[强化] [C][C]（支付[C][C]：强化我。仅在未强化时可用。）
[已强化][>] 如果一个将我选作目标的法术或技能将眩晕我、或给予我-[M]、或把我送回手牌，则
改为给予我在本回合内[M]+3。
```

#### CHG-4B-T2ER-VEN-086-EV-EN-ER-0065  —  `R-CARD-VEN-086`  —  card:VEN-086 (Gangplank, Naval / 普朗克)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-VEN-086` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `09_2026-07-23_Vendetta_Errata.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0065 (source_020) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Empower] [C][C] ([C][C]: Empower me. Use only if not Empowered.)
[Empowered][>] If a spell or ability that chooses me would stun me, give me -[M], or return me to hand, give me +3 [M] instead.
```

**new_content**:

```
[Empower] [C][C] ([C][C]: Empower me. Use only if not Empowered.)
[Empowered][>] If a spell or ability that chooses me would stun me, give me -[M], or return me to hand, give me +3 [M] this turn instead.
```

### `R-CARD-VEN-167`  —  card:VEN-167 (Vi, Destructive / 蔚) — 本规则共 1 条变更

#### CHG-4B-T2ER-VEN-167-EV-CN-ER-0056  —  `R-CARD-VEN-167`  —  card:VEN-167 (Vi, Destructive / 蔚)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-VEN-167` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0056 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[游走]（我可以向其他战场进行移动。）
你可以从废牌堆回收一张卡牌，然后让我本回合内战力+1（可重复执行）。
```

**new_content**:

```
[游走]（我可以向其他战场进行移动。）
从你的废牌堆回收一张卡牌：给予我在本回合内[S]+1。
```

### `R-CARD-VEN-175`  —  card:VEN-175 (Jayce, Man of Progress / 杰斯) — 本规则共 1 条变更

#### CHG-4B-T2ER-VEN-175-EV-CN-ER-0050  —  `R-CARD-VEN-175`  —  card:VEN-175 (Jayce, Man of Progress / 杰斯)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-VEN-175` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0050 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你打出我时，你可以选择摧毁一件友方装备，以此在本回合内可以从手牌中打出一件法力费用
不高于[7]的装备，无视其法力费用（仍需支付所有符能费用）。
```

**new_content**:

```
当你打出我时，你可以选择摧毁一件友方装备。若如此做，则在本回合内，你可以选择从手牌中
打出一件法力费用不高于[7]的装备，无视其法力费用（仍需支付所有符能费用）。
```

### `R-CARD-VEN-179`  —  card:VEN-179 (Rengar, Trophy Hunter / 雷恩加尔) — 本规则共 2 条变更

#### CHG-4B-T2ER-VEN-179-EV-CN-ER-0039  —  `R-CARD-VEN-179`  —  card:VEN-179 (Rengar, Trophy Hunter / 雷恩加尔)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-VEN-179` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0039 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[伏击]（你可以选择将我作为[反应]牌，打出到有己方单位的战场。）
我可以被打出至有敌方单位的战场（即使你在该处没有单位）。
```

**new_content**:

```
[伏击]（你可以选择将我作为[反应]牌，打出到有己方单位的战场。）
我可以[伏击]到有敌方单位的战场，即使你在该处没有单位。
```

#### CHG-4B-T2ER-VEN-179-EV-EN-ER-0057  —  `R-CARD-VEN-179`  —  card:VEN-179 (Rengar, Trophy Hunter / 雷恩加尔)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-VEN-179` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `06_2026-04-03_Unleashed_Errata.pdf` |
| version | `v2026` |
| date | `2026-04-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0057 (source_017) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Ambush] (You may play me as a [Reaction] to a battlefield where you have units.)
I can be played to a battlefield where there are enemy units (even if you don't have units there).
```

**new_content**:

```
[Ambush] (You may play me as a [Reaction] to a battlefield where you have units.)
I can [Ambush] to a battlefield where there are enemy units, even if you don't have units there.
```

### `R-CARD-VEN-181`  —  card:VEN-181 (Gangplank, Naval / 普朗克) — 本规则共 2 条变更

#### CHG-4B-T2ER-VEN-181-EV-CN-ER-0087  —  `R-CARD-VEN-181`  —  card:VEN-181 (Gangplank, Naval / 普朗克)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-VEN-181` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `10_2026-07-24_9fe1f19110dd4678a6ad7bd96e791bba.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0087 (source_010) applied per Stage 4B; effective_scope=printed_text_alignment |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
[强化] [C][C]（支付[C][C]：强化我。仅在未强化时可用。）
[已强化][>] 如果一个将我选作目标的法术或技能将眩晕我、或给予我-[M]、或把我送回手牌，则
改为给予我在本回合内[M]+3。
```

**new_content**:

```
[强化] [C][C]（支付[C][C]：强化我。仅在未强化时可用。）
[已强化][>] 如果一个将我选作目标的法术或技能将眩晕我、或给予我-[M]、或把我送回手牌，则
改为给予我在本回合内[M]+3。
```

#### CHG-4B-T2ER-VEN-181-EV-EN-ER-0065  —  `R-CARD-VEN-181`  —  card:VEN-181 (Gangplank, Naval / 普朗克)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-VEN-181` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `09_2026-07-23_Vendetta_Errata.pdf` |
| version | `v2026` |
| date | `2026-07-24` |
| modification_type | `partial_replacement` |
| reason | official errata EV-EN-ER-0065 (source_020) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
[Empower] [C][C] ([C][C]: Empower me. Use only if not Empowered.)
[Empowered][>] If a spell or ability that chooses me would stun me, give me -[M], or return me to hand, give me +3 [M] instead.
```

**new_content**:

```
[Empower] [C][C] ([C][C]: Empower me. Use only if not Empowered.)
[Empowered][>] If a spell or ability that chooses me would stun me, give me -[M], or return me to hand, give me +3 [M] this turn instead.
```

### `R-CARD-VEN-SP2`  —  card:VEN-SP2 (Sona, Harmonious / 娑娜) — 本规则共 2 条变更

#### CHG-4B-T2ER-VEN-SP2-EV-CN-ER-0021  —  `R-CARD-VEN-SP2`  —  card:VEN-SP2 (Sona, Harmonious / 娑娜)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-VEN-SP2` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `02_2025-12-03_符文战场_勘误汇总_1028.pdf` |
| version | `v2025` |
| date | `2025-12-03` |
| modification_type | `partial_replacement` |
| reason | official errata EV-CN-ER-0021 (source_002) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
在你的回合结束时，如果我位于战场上，则让四枚友方符文变为活跃状态。
```

**new_content**:

```
在你的回合结束时，如果我位于战场上，则让最多四枚友方符文变为活跃状态。
```

#### CHG-4B-T2ER-VEN-SP2-EV-EN-ER-0022  —  `R-CARD-VEN-SP2`  —  card:VEN-SP2 (Sona, Harmonious / 娑娜)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-VEN-SP2` |
| source_type | `errata` |
| source_language | `en` |
| source_document | `02_2025-10-28_Origins_Errata.pdf` |
| version | `v2025` |
| date | `2025-10-21` |
| modification_type | `condition_change` |
| reason | official errata EV-EN-ER-0022 (source_013) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | recorded: EN-language counterpart errata (zh canonical governed by paired zh errata) |

**original_content**:

```
While I'm at a battlefield, ready 4 friendly runes at the end of your turn.
```

**new_content**:

```
At the end of your turn, if I'm at a battlefield, ready up to 4 friendly runes.
```

### `R-CARD-VEN-SP5`  —  card:VEN-SP5 (Ezreal, Prodigy / 伊泽瑞尔) — 本规则共 1 条变更

#### CHG-4B-T2ER-VEN-SP5-EV-CN-ER-0047  —  `R-CARD-VEN-SP5`  —  card:VEN-SP5 (Ezreal, Prodigy / 伊泽瑞尔)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-VEN-SP5` |
| source_type | `errata` |
| source_language | `zh` |
| source_document | `03_2026-04-15_破限系列_勘误汇总_260403.pdf` |
| version | `v2026` |
| date | `2026-04-15` |
| modification_type | `terminology_fix` |
| reason | official errata EV-CN-ER-0047 (source_003) applied per Stage 4B; effective_scope=card_text |
| final_conclusion | applied: latest zh official errata defines canonical card text |

**original_content**:

```
当你打出我时，弃置一张手牌，然后抽两张牌。
你可以将其他卡牌的可选额外费用减少[1]或[A]后支付。
```

**new_content**:

```
当你打出我时，弃置一张手牌，然后抽两张牌。
你支付的可选额外费用，其费用减少[1]或[A]。
```

## 2. FAQ 内嵌规则变更 — 4B-B005（6 条）

> 过渡期官方 FAQ（source_007 / source_005）声明的旧规则对照；已核实全部并入 2026-07 核心规则（incorporated），仅记录、不重复应用。

### `R-CR-187.4`  —  187.4 Tokens — 本规则共 1 条变更

#### CHG-4B-T1F-0001  —  `R-CR-187.4`  —  187.4 Tokens

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CR-187.4` |
| source_type | `faq` |
| source_language | `zh` |
| source_document | `07_2026-04-30_破限系列_官方FAQ.pdf` |
| version | `v2026` |
| date | `2026-04-30` |
| modification_type | `other` |
| reason | FAQ(source_007) declares old 187.4.c contradicted cleanup rule 323.6; control-loss consolidated into 323.6 and 187.4.c removed (187.4 renumbered to Mech token def) |
| final_conclusion | incorporated into 2026-07 core rules; recorded, not applied |

**original_content**:

```
187.4.c.（旧）如果玩家在某战场上没有单位，且该回合处于开环状态，则除非该战场正在进行战斗或法术对决，否则该玩家会在后续的清理阶段失去该战场的控制权。
```

**new_content**:

```
323.6. 4.如果当前回合处于开环状态，且某处由某玩家控制的战场上没有正在进行的法术对决或战斗，若该处战场没有被该玩家控制的单位占据，则该玩家失去该战场的控制权。
```

### `R-CR-316.5`  —  316.5 Main Phase — 本规则共 1 条变更

#### CHG-4B-T1F-0002  —  `R-CR-316.5`  —  316.5 Main Phase

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CR-316.5` |
| source_type | `faq` |
| source_language | `zh` |
| source_document | `07_2026-04-30_破限系列_官方FAQ.pdf` |
| version | `v2026` |
| date | `2026-04-30` |
| modification_type | `condition_change` |
| reason | FAQ(source_007) declares 316.5.b wording change (uncontrolled-only -> any contested battlefield); rule relocated to 323.8; 316.5.b renumbered to Neutral Open State def |
| final_conclusion | incorporated into 2026-07 core rules at 323.8; recorded, not applied |

**original_content**:

```
316.5.b.（旧）当尚无控制者的战场进入争夺状态时，则将该战场上的法术对决标记为待发生。
```

**new_content**:

```
323.8. 6.如果战场进入了争夺状态，则将该战场上的法术对决标记为待发生。
```

### `R-CR-323.6`  —  323.6 .8 After a Move is completed — 本规则共 1 条变更

#### CHG-4B-T1F-0003  —  `R-CR-323.6`  —  323.6 .8 After a Move is completed

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CR-323.6` |
| source_type | `faq` |
| source_language | `zh` |
| source_document | `07_2026-04-30_破限系列_官方FAQ.pdf` |
| version | `v2026` |
| date | `2026-04-30` |
| modification_type | `condition_change` |
| reason | FAQ(source_007) declares 323.6 wording change (battlefield becomes uncontrolled -> player loses control of occupied battlefield), resolving contradiction with old 187.4.c |
| final_conclusion | incorporated into 2026-07 core rules (current 323.6, minor reword); recorded, not applied |

**original_content**:

```
323.6.（旧）4.如果当前回合处于开环状态，则没有单位占据且没有法术对决或战斗正在进行的战场将变为未受控制状态。
```

**new_content**:

```
323.6.（新）4.如果当前回合处于开环状态，且某处战场上没有正在进行的法术对决或战斗，则玩家将失去未被其单位占据的已控制战场的控制权。
```

### `R-CR-323.8`  —  323.8 .8 After a Move is completed — 本规则共 1 条变更

#### CHG-4B-T1F-0004  —  `R-CR-323.8`  —  323.8 .8 After a Move is completed

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CR-323.8` |
| source_type | `faq` |
| source_language | `zh` |
| source_document | `07_2026-04-30_破限系列_官方FAQ.pdf` |
| version | `v2026` |
| date | `2026-04-30` |
| modification_type | `condition_change` |
| reason | FAQ(source_007) declares showdown-marking now applies to any contested battlefield (cleanup-flow rule takes precedence); carries the 316.5.b NEW text at relocated position 323.8 |
| final_conclusion | incorporated into 2026-07 core rules; recorded, not applied |

**original_content**:

```
316.5.b.（旧）当尚无控制者的战场进入争夺状态时，则将该战场上的法术对决标记为待发生。
```

**new_content**:

```
323.8. 6.如果战场进入了争夺状态，则将该战场上的法术对决标记为待发生。
```

### `R-CR-344.2`  —  344.2 Showdowns — 本规则共 1 条变更

#### CHG-4B-T1F-0005  —  `R-CR-344.2`  —  344.2 Showdowns

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CR-344.2` |
| source_type | `faq` |
| source_language | `zh` |
| source_document | `07_2026-04-30_破限系列_官方FAQ.pdf` |
| version | `v2026` |
| date | `2026-04-30` |
| modification_type | `condition_change` |
| reason | FAQ(source_007) declares 344.2 condition change (uncontrolled-when-contested -> no units of different players present) |
| final_conclusion | incorporated into 2026-07 core rules (current 344.2 adds Neutral Open State qualifier); recorded, not applied |

**original_content**:

```
344.2.（旧）如果某处战场的控制权受到争夺，且在争夺发生时处于无人控制状态，则会在导致该战场进入争夺状态的行动结束后的清理步骤中展开法术对决。
```

**new_content**:

```
344.2.（新）如果某处战场的控制权受到争夺，且该战场上没有由不同玩家控制的单位，则会在导致该战场进入争夺状态的行动结束后的清理步骤中展开法术对决。
```

### `R-CR-461.3`  —  461.3 Combat — 本规则共 1 条变更

#### CHG-4B-T1F-0006  —  `R-CR-461.3`  —  461.3 Combat

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CR-461.3` |
| source_type | `faq` |
| source_language | `zh` |
| source_document | `07_2026-04-30_破限系列_官方FAQ.pdf` |
| version | `v2026` |
| date | `2026-04-30` |
| modification_type | `condition_change` |
| reason | FAQ(source_007) declares 461.3.d no-result condition adds recalled-units case; rule relocated to 466.3.d in 2026-07 renumbering |
| final_conclusion | incorporated into 2026-07 core rules at 466.3.d (verbatim incl. recall clause); recorded, not applied |

**original_content**:

```
461.3.d.（旧）如果在此步骤期间，双方玩家都拥有单位，或双方都没有单位，则战斗"无结果"。
```

**new_content**:

```
466.3.d. 如果在战斗清理的第3d 步骤时，有单位被召回、或双方玩家在此任务期间仍有单位在战场上、或双方玩家在此任务期间都没有单位在战场上，则战斗"无结果"。
```

## 3. 核心规则后官方改动 — 4B-B006（38 条）

> source_019 Vendetta Patch Notes（生效 2026-07-24，晚于核心规则，为权威方）APPLIED 的 new_rule_addition 37 条 + source_005 EV-CN-FAQ-0055 已并入 809.1.c 记录 1 条。原始内容为 NULL 表示新增规则（无原始文本，未伪造）。

### `R-MISC-source_019`  —  faq/oe ungrouped items (source_019, lang=en) — 本规则共 5 条变更

#### CHG-4B-T3-0001  —  `R-MISC-source_019`  —  faq/oe ungrouped items (source_019, lang=en)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-MISC-source_019` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Empower keyword added.
```

#### CHG-4B-T3-0002  —  `R-MISC-source_019`  —  faq/oe ungrouped items (source_019, lang=en)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-MISC-source_019` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Empowered keyword added.
```

#### CHG-4B-T3-0003  —  `R-MISC-source_019`  —  faq/oe ungrouped items (source_019, lang=en)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-MISC-source_019` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Empower action added.
```

#### CHG-4B-T3-0004  —  `R-MISC-source_019`  —  faq/oe ungrouped items (source_019, lang=en)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-MISC-source_019` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Disempower action added.
```

#### CHG-4B-T3-0005  —  `R-MISC-source_019`  —  faq/oe ungrouped items (source_019, lang=en)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-MISC-source_019` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Empowered state added.
```

### `R-TOPIC-CN-40`  —  faq topic [zh]: 预时之门 — 本规则共 1 条变更

#### CHG-4B-T3-0006  —  `R-TOPIC-CN-40`  —  faq topic [zh]: 预时之门

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-CN-40` |
| source_type | `faq` |
| source_language | `zh` |
| source_document | `05_2026-04-15_铸魂淬炼系列_官方FAQ_260114.pdf` |
| version | `-（无版本）` |
| date | `2026-04-15` |
| modification_type | `other` |
| reason | FAQ(source_005) declared 735.1.c revised text ('预时之门' 法盾费用语义); absorbed into 2026-07 core rules as 809.1.c (EV-CN-CR-2140; MR-2D-0007 + B005 precedent) |
| final_conclusion | incorporated into 2026-07 core rules; recorded, not applied |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
规则 735.1.c（修订后）
该关键词为以下功能的简称：“对手每次将我选为法术或技能的目标时，必须支付等同于[法
盾值]的符能作为额外费用，才能将我选为目标。”
```

### `R-TOPIC-EN-08`  —  faq topic [en]: Battlefield Ability Control — 本规则共 2 条变更

#### CHG-4B-T3-0007  —  `R-TOPIC-EN-08`  —  faq topic [en]: Battlefield Ability Control

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-08` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: If another spell or ability attempts to reference the number of game objects, players, or zones that a Finalized Chain
Item targets, it will include any mistargeted choices, but not any targets that have changed to a non-board zone. I’m Getting Activated
In the Unleashed FAQ, we acknowledged that “activate” when it appears on card text was underdefined in the rules. As of the Vendetta Rules Update, we have the technology!
```

#### CHG-4B-T3-0008  —  `R-TOPIC-EN-08`  —  faq topic [en]: Battlefield Ability Control

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-08` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Some effects may instruct a player to “activate” a named triggered ability. To do so, that player checks the condition
of all of the specified effects, as if they had fulfilled the named part of the condition Accelerate In the Unleashed FAQ, we clarified that Accelerate is an ability made up of two parts: an optional additional cost, and a delayed replacement effect that is generated when you pay the cost. This has now been reflected in the rules themselves.
```

### `R-TOPIC-EN-14`  —  faq topic [en]: Contested Removal — 本规则共 2 条变更

#### CHG-4B-T3-0009  —  `R-TOPIC-EN-14`  —  faq topic [en]: Contested Removal

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-14` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: In a cleanup, remove Contested status from each Battlefield without Units controlled by the player who applied
Contested to that Battlefield and without a Showdown or Combat ongoing there.
```

#### CHG-4B-T3-0010  —  `R-TOPIC-EN-14`  —  faq topic [en]: Contested Removal

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-14` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: That player cannot choose to have fewer Targets than they have damage to split when choosing which Targets
cease being Targets. 2v2 Rules Clarifications We’ve added some clarifications for the 2v2 specific rules! Firstly, points are shared by teams. This was probably obvious, but it wasn’t stated directly and there were important clarifications that needed to be made. Secondly, battlefields controlled by a teammate during the scoring step of a player’s beginning phase are now ineligible to be scored by that player’s team during that turn and count towards the final point rule.
```

### `R-TOPIC-EN-23`  —  faq topic [en]: Hidden Targeting — 本规则共 1 条变更

#### CHG-4B-T3-0011  —  `R-TOPIC-EN-23`  —  faq topic [en]: Hidden Targeting

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-23` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Game Effects may refer to a player’s Damage. This means the Damage marked by that player.
```

### `R-TOPIC-EN-39`  —  faq topic [en]: Rules Update: (Resource) Payment Optional — 本规则共 1 条变更

#### CHG-4B-T3-0012  —  `R-TOPIC-EN-39`  —  faq topic [en]: Rules Update: (Resource) Payment Optional

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-39` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: When a player is instructed to Pay a resource, that player may remove that resource from their Rune Pool if it exists
there. If they choose not to, the instruction is ignored. Rules Update: Costs on Multi-Domain Cards We’ve aligned that it was strange that signature cards’ power costs could be paid with power of any domain. The power cost symbols have the colors of their domains, and players felt intuitively that you should pay for their cost with only power of those domains. In order to align better with player intuition, the power cost rules have been updated for cards of multiple domains.
This means you’ll have to pay for a signature card’s power cost with a power of that card’s domains. If there is an [A] symbol in the card’s text, that can still be paid with power of any domain.
```

### `R-TOPIC-EN-40`  —  faq topic [en]: Rules Update: Applied Costs — 本规则共 1 条变更

#### CHG-4B-T3-0013  —  `R-TOPIC-EN-40`  —  faq topic [en]: Rules Update: Applied Costs

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-40` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Applied costs added.
```

### `R-TOPIC-EN-41`  —  faq topic [en]: Rules Update: Battlefield Reuse — 本规则共 3 条变更

#### CHG-4B-T3-0014  —  `R-TOPIC-EN-41`  —  faq topic [en]: Rules Update: Battlefield Reuse

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-41` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: In a Best of 5 match, during games 4 and 5 of the match players may present a battlefield that has been removed
from the game.
```

#### CHG-4B-T3-0015  —  `R-TOPIC-EN-41`  —  faq topic [en]: Rules Update: Battlefield Reuse

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-41` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Players may only re-use a battlefield in this way if they have already presented each of their battlefields at least
once during the match, and present a battlefield at most twice in a given match.
```

#### CHG-4B-T3-0016  —  `R-TOPIC-EN-41`  —  faq topic [en]: Rules Update: Battlefield Reuse

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-41` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: If no player won a game, the battlefields presented for that game may be reused in a subsequent game.
```

### `R-TOPIC-EN-42`  —  faq topic [en]: Rules Update: Deathknell and “When I Die” Alignment — 本规则共 1 条变更

#### CHG-4B-T3-0017  —  `R-TOPIC-EN-42`  —  faq topic [en]: Rules Update: Deathknell and “When I Die” Alignment

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-42` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Deathknell and “When I die” abilities aligned
```

### `R-TOPIC-EN-43`  —  faq topic [en]: Rules Update: Gone Before its Time — 本规则共 3 条变更

#### CHG-4B-T3-0018  —  `R-TOPIC-EN-43`  —  faq topic [en]: Rules Update: Gone Before its Time

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-43` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: If a Delayed Ability’s duration has ended before it was generated, the Delayed Ability is not generated and any
instructions related to it are ignored. Rules Update: Event Definition In the last several rules updates, we’ve done our best to define terms that were otherwise underdefined or underexplained. With more instances of replacement effects, and replacement effects that are replacing more complex events, we wanted to have a clear definition of what an event is outlined in the rules.
```

#### CHG-4B-T3-0019  —  `R-TOPIC-EN-43`  —  faq topic [en]: Rules Update: Gone Before its Time

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-43` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: An event is the singular moment that results from a Game Action being performed or from a Game Object
changing state. Rules Update: New Replacement Effects There are three categories of card text that were previously undefined. The rules now recognize all three as replacement effects: Abilities that describe how a unit enters, or an action to be performed as a unit enters, are replacement effects. They replace the unit entering as normal with the unit entering in the appropriate state. Abilities that instruct a game action to occur “as” an event happens are replacement effects that replace the stated event with that event and also the game action being performed. Abilities that instruct a player to “then banish it” or “then recycle it” are replacement effects that are short for “if it would leave the chain after becoming a finalized chain item, and leaving the chain wasn’t instructed by its own execution, perform the specified game action instead.”
```

#### CHG-4B-T3-0020  —  `R-TOPIC-EN-43`  —  faq topic [en]: Rules Update: Gone Before its Time

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-43` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: New replacement effects added
```

### `R-TOPIC-EN-57`  —  faq topic [en]: Vendetta Addition: Burn — 本规则共 2 条变更

#### CHG-4B-T3-0021  —  `R-TOPIC-EN-57`  —  faq topic [en]: Vendetta Addition: Burn

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-57` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Burn action added.
Danger and value go hand in hand. Vendetta Addition: Skip
For the first time, a card has been printed that allows a player to skip part of their turn. In order to support that functionality, we’ve added a new action: skip. Skip is a replacement effect that replaces the named event or procedure of the turn with nothing. Anything that would occur as a result of that event or procedure of the turn doesn’t happen instead.
```

#### CHG-4B-T3-0022  —  `R-TOPIC-EN-57`  —  faq topic [en]: Vendetta Addition: Burn

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-57` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Naming cards, types, and tags added.
```

### `R-TOPIC-EN-58`  —  faq topic [en]: Vendetta Addition: Flow — 本规则共 1 条变更

#### CHG-4B-T3-0023  —  `R-TOPIC-EN-58`  —  faq topic [en]: Vendetta Addition: Flow

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-58` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Flow keyword added.
```

### `R-TOPIC-EN-59`  —  faq topic [en]: Vendetta Support: Activated Ability Terminology — 本规则共 1 条变更

#### CHG-4B-T3-0024  —  `R-TOPIC-EN-59`  —  faq topic [en]: Vendetta Support: Activated Ability Terminology

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-59` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: “Use” and “play” supported for activated ability card text.
```

### `R-TOPIC-EN-60`  —  faq topic [en]: Vendetta Support: Cards with Multiple Types — 本规则共 1 条变更

#### CHG-4B-T3-0025  —  `R-TOPIC-EN-60`  —  faq topic [en]: Vendetta Support: Cards with Multiple Types

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-60` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Cards with multiple types added
```

### `R-TOPIC-EN-61`  —  faq topic [en]: Vendetta Support: Ignoring Effects — 本规则共 1 条变更

#### CHG-4B-T3-0026  —  `R-TOPIC-EN-61`  —  faq topic [en]: Vendetta Support: Ignoring Effects

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-61` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Ignoring effects added.
```

### `R-TOPIC-EN-62`  —  faq topic [en]: Vendetta Support: Making New Choices — 本规则共 1 条变更

#### CHG-4B-T3-0027  —  `R-TOPIC-EN-62`  —  faq topic [en]: Vendetta Support: Making New Choices

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-62` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Making new choices added.
```

### `R-TOPIC-EN-63`  —  faq topic [en]: Vendetta Support: Replacement Effects and Combat Damage — 本规则共 4 条变更

#### CHG-4B-T3-0028  —  `R-TOPIC-EN-63`  —  faq topic [en]: Vendetta Support: Replacement Effects and Combat Damage

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-63` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: When assigning damage during the combat damage step, replacement effects that would apply to the resulting
damage are considered to apply to the assignment instead. Rules Update: Copying Tokens Token is no longer a supertype. It being a supertype made several cards work in problematic ways, and it wasn’t entirely intuitive that it should be a supertype. Now, regardless of how a token is manipulated, copied, or altered, it will maintain its tokenness. Cards, similarly, cannot become tokens for any reason.
```

#### CHG-4B-T3-0029  —  `R-TOPIC-EN-63`  —  faq topic [en]: Vendetta Support: Replacement Effects and Combat Damage

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-63` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: “Token” is an intrinsic category of Game Objects, in the same way “card” is.
```

#### CHG-4B-T3-0030  —  `R-TOPIC-EN-63`  —  faq topic [en]: Vendetta Support: Replacement Effects and Combat Damage

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-63` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Token Game Objects cannot lose their token nature by any means.
```

#### CHG-4B-T3-0031  —  `R-TOPIC-EN-63`  —  faq topic [en]: Vendetta Support: Replacement Effects and Combat Damage

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-63` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Card Game Objects cannot become tokens by any means.
```

### `R-TOPIC-EN-64`  —  faq topic [en]: Vendetta Support: Untargetability — 本规则共 1 条变更

#### CHG-4B-T3-0032  —  `R-TOPIC-EN-64`  —  faq topic [en]: Vendetta Support: Untargetability

| 字段 | 值 |
| --- | --- |
| rule_id | `R-TOPIC-EN-64` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision |
| final_conclusion | applied as official change (recorded verbatim on rule); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Untargetability added.
```

### `R-CARD-SFD-111`  —  card:SFD-111 (Here to Help / 前来相助) — 本规则共 1 条变更

#### CHG-4B-T3-0033  —  `R-CARD-SFD-111`  —  card:SFD-111 (Here to Help / 前来相助)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-SFD-111` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE affecting this card's interaction space; authoritative side per MR-2D-0010 + B005 scope |
| final_conclusion | applied as official change (recorded in changes table; card canonical unchanged -- errata text remains canonical); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: If as a result of the removal of Contested status there are Units located at an uncontested Battlefield that their
controller does not control, their controller applies Contested status to that Battlefield. Targeting Clarification For the first time since the great big targeting list was codified in the second Origins rules update, we’ve added a new disqualification for something being a target. Thankfully in this case it should be relatively easy to remember: If a player, zone, or game object appears only as a restriction or permission for a game action, then it is not a target. This means Thrill of the Hunt, Here to Help, and similar effects that instruct you to perform an action “to a battlefield” don’t target that battlefield. The restriction or permission is applied to the resulting action and is not a decision made on finalization.
```

### `R-CARD-UNL-106`  —  card:UNL-106 (Repulse / 击退) — 本规则共 1 条变更

#### CHG-4B-T3-0034  —  `R-CARD-UNL-106`  —  card:UNL-106 (Repulse / 击退)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-106` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE affecting this card's interaction space; authoritative side per MR-2D-0010 + B005 scope |
| final_conclusion | applied as official change (recorded in changes table; card canonical unchanged -- errata text remains canonical); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: If an Ability of a Battlefield indicates that a specific player makes a choice, that player is the Ability’s controller. They
take responsibility for adding it to the chain if applicable and make all choices required by the ability. They and only they control the ability, regardless of who controls the Battlefield. Counting Targets We clarified what kinds of targets count and in what situations for effects that check the number of targets a spell has in the Unleashed FAQ; specifically for the purposes of cards like Repulse. That clarification has now been addressed directly in the Core Rules Document.
```

### `R-CARD-UNL-118`  —  card:UNL-118 (Elder Dragon / 远古巨龙) — 本规则共 1 条变更

#### CHG-4B-T3-0035  —  `R-CARD-UNL-118`  —  card:UNL-118 (Elder Dragon / 远古巨龙)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-118` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE affecting this card's interaction space; authoritative side per MR-2D-0010 + B005 scope |
| final_conclusion | applied as official change (recorded in changes table; card canonical unchanged -- errata text remains canonical); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Non-triggered abilities that check cards being played do so by means of referencing whether said cards have been
Finalized. Oh Damage, My Damage Lethal Damage was handled by the rules in a bit of a strange way. It was referenced obliquely in three different sections and only actually named in one of those sections. That made changes to the definition of Lethal Damage, like that in Elder Dragon’s passive ability, unclear as to which of those three sections it might apply. We clarified in the Unleashed FAQ that all three instances are referring to the same concept, and modification to one modifies all of them. Now the Core Rules Document has been updated to include that clarification in the text itself. On the topic of damage, we defined “your damage” in the Unleashed FAQ to be “damage you marked on units.” That definition has now been added to the rules directly.
```

### `R-CARD-UNL-118a`  —  card:UNL-118a (Elder Dragon / 远古巨龙) — 本规则共 1 条变更

#### CHG-4B-T3-0036  —  `R-CARD-UNL-118a`  —  card:UNL-118a (Elder Dragon / 远古巨龙)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-118a` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE affecting this card's interaction space; authoritative side per MR-2D-0010 + B005 scope |
| final_conclusion | applied as official change (recorded in changes table; card canonical unchanged -- errata text remains canonical); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Non-triggered abilities that check cards being played do so by means of referencing whether said cards have been
Finalized. Oh Damage, My Damage Lethal Damage was handled by the rules in a bit of a strange way. It was referenced obliquely in three different sections and only actually named in one of those sections. That made changes to the definition of Lethal Damage, like that in Elder Dragon’s passive ability, unclear as to which of those three sections it might apply. We clarified in the Unleashed FAQ that all three instances are referring to the same concept, and modification to one modifies all of them. Now the Core Rules Document has been updated to include that clarification in the text itself. On the topic of damage, we defined “your damage” in the Unleashed FAQ to be “damage you marked on units.” That definition has now been added to the rules directly.
```

### `R-CARD-UNL-138`  —  card:UNL-138 (The List / 夺命名单) — 本规则共 1 条变更

#### CHG-4B-T3-0037  —  `R-CARD-UNL-138`  —  card:UNL-138 (The List / 夺命名单)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-138` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE affecting this card's interaction space; authoritative side per MR-2D-0010 + B005 scope |
| final_conclusion | applied as official change (recorded in changes table; card canonical unchanged -- errata text remains canonical); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: Skip action added.
Poof! It’s gone. No triggers, no procedures, nada. Zip! Zilch!! Vendetta Support: Naming Cards, Types, and Tags In Vendetta, we’ve added a card that instructs a player to name a card, in addition to the List from Unleashed that instructs a player to name a tag. With a preponderance of these effects, it’s time to define their function and the process by which a player names a card, type, or tag. Naming a card in particular is more complex than either type or tag, and has some special rules to give players some flexibility with how they name cards.
```

### `R-CARD-UNL-184`  —  card:UNL-184 (Thrill of the Hunt / 狩猎律动) — 本规则共 1 条变更

#### CHG-4B-T3-0038  —  `R-CARD-UNL-184`  —  card:UNL-184 (Thrill of the Hunt / 狩猎律动)

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CARD-UNL-184` |
| source_type | `official_explanation` |
| source_language | `en` |
| source_document | `08_2026-07-17_Vendetta_Patch_Notes.pdf` |
| version | `-（无版本）` |
| date | `2026-07-24` |
| modification_type | `new_rule_addition` |
| reason | post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE affecting this card's interaction space; authoritative side per MR-2D-0010 + B005 scope |
| final_conclusion | applied as official change (recorded in changes table; card canonical unchanged -- errata text remains canonical); Stage 5 verification required |

**original_content**: *（NULL — 本条为新增规则，无原始规则文本；未伪造）*

**new_content**:

```
NEW RULE: If as a result of the removal of Contested status there are Units located at an uncontested Battlefield that their
controller does not control, their controller applies Contested status to that Battlefield. Targeting Clarification For the first time since the great big targeting list was codified in the second Origins rules update, we’ve added a new disqualification for something being a target. Thankfully in this case it should be relatively easy to remember: If a player, zone, or game object appears only as a restriction or permission for a game action, then it is not a target. This means Thrill of the Hunt, Here to Help, and similar effects that instruct you to perform an action “to a battlefield” don’t target that battlefield. The restriction or permission is applied to the resulting action and is not a decision made on finalization.
```

## 4. Stage 5 独立验证修复（1 条）

> verification 阶段确认的修正：R-CR-811.1.b 英文同版本持续条款在中文官方文本中遗漏，补充中文译写（CON-4B-T2-0001 resolved_stage5）。

### `R-CR-811.1.b`  —  811.1.b Hidden — 本规则共 1 条变更

#### CHG-5-0001  —  `R-CR-811.1.b`  —  811.1.b Hidden

| 字段 | 值 |
| --- | --- |
| rule_id | `R-CR-811.1.b` |
| source_type | `rule` |
| source_language | `en` |
| source_document | `07_2026-07-16_Core_Rules.pdf` |
| version | `v2026` |
| date | `2026-07-16` |
| modification_type | `condition_change` |
| reason | EN official core rules (same confirmed version, 2026-07-16) 811.1.b carries duration clause "for as long as you control that battlefield" omitted in zh official translation; per source-priority rule (same version: EN > zh), canonical supplemented with zh rendering of the EN clause |
| final_conclusion | CON-4B-T2-0001 resolved: canonical now semantically equivalent to EN official text |

**original_content**:

```
该关键词为以下功能的简称：“在你回合的开环状态下，如果此牌在你的手牌或你的英雄区域中，你可以选择支付[A]将此牌以正面朝下的方式布置到你已控制且目前没有正面朝下待命卡牌的战场上，此牌保持正面朝下待命状态，直至你不再控制该战场。从下回合开始，此牌将获得[反应]，你可以将此牌打出，无视其基础费用。”
```

**new_content**:

```
该关键词为以下功能的简称：“在你回合的开环状态下，如果此牌在你的手牌或你的英雄区域中，你可以选择支付[A]将此牌以正面朝下的方式布置到你已控制且目前没有正面朝下待命卡牌的战场上，此牌保持正面朝下待命状态，直至你不再控制该战场。从下回合开始，此牌将获得[反应]，你可以将此牌打出，无视其基础费用。”
```

---

*End of change_log.md — 267 entries. 复核请回查 workspace/rules_work.db 的 changes 表。*
