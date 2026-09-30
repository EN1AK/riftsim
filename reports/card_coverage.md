# 卡牌覆盖报告（cardfx per-card 脚本架构）

- 生成：2026-09-30，自动生成，幂等可重算
- 输入：cards_bilingual.db（sha256:715f31d8707b）；cardfx 注册表 535 条；card_db_version=cdb1:709fe8445661@cards_bilingual.db
- 口径：效果事实源 = cardfx/*.py 手写脚本（脚本未写的效果即不存在，脚本注释 CN 原文供逐项 review）

```stats_sha256:8e15f11e0779```

## 1 总览

| 分层 | 卡数 |
|---|---|
| 源表行数 | 1267 |
| 可加载 defs | 1224 |
| unsupported（schema 无法精确表示，非效果问题） | 43 |
| **已实现-完备**（cardfx + reviewed=True，人工逐项确认） | **55** |
| 已登记-草稿（迁移自解析层，逐 set review 队列） | 480 |
| 无需脚本（无 CN 印刷文本 vanilla，非符文） | 17 |
| 注：源表无 CN 文本共 85 = 66 基本符文（技能引擎统一供给 R-CR-164.2）+ 2 unsupported + 17 vanilla |  |
| 未适配（有文本、未登记） | 606 |

## 2 原语（kind）分布

| kind | 卡数 | 例 |
|---|---|---|
| equip | 32 | SFD-009, SFD-016, SFD-022 |
| gain_resource | 12 | OGN-040, OGN-081, OGN-120 |
| extra_cost | 9 | SFD-013, SFD-067, SFD-098 |
| enters_ready | 6 | ARC-004, OGN-159, OGS-009 |
| spell_draw | 6 | OGN-083, SFD-076, SFD-087 |
| location_open_battlefield | 6 | OGN-174, OGN-176, OGN-193 |
| last_damage | 5 | ARC-002, OGN-068, SFD-173 |
| spell_damage | 5 | OGN-009, OGN-014, OGN-085 |
| enters_exhausted | 5 | OGN-017, UNL-049, UNL-136 |
| on_play_draw | 5 | OGN-087, UNL-053, VEN-048 |
| spell_pump | 5 | OGN-154, SFD-034, SFD-066 |
| on_play_pump | 4 | FND-196, OGN-197, OGN-197a |
| no_combat_damage | 4 | SFD-082, SFD-082a, SFD-082b |
| trigger | 2 | SFD-115, SFD-118 |
| deal_damage | 1 | OGN-017 |

## 3 关键词分布

| 关键词 | 卡数 | 例 |
|---|---|---|
| action | 71 | OGN-004, OGN-005, OGN-008 |
| reaction | 59 | OGN-033, OGN-045, OGN-046 |
| empower | 49 | VEN-007, VEN-014, VEN-018 |
| hidden | 47 | FND-196, OGN-053, OGN-057 |
| deflect | 40 | OGN-013, OGN-041, OGN-041a |
| accelerate | 39 | OGN-001, OGN-010, OGN-030 |
| equip | 32 | SFD-009, SFD-016, SFD-022 |
| assault | 28 | OGN-003, OGN-030, OGN-030a |
| ganking | 25 | ARC-001, OGN-036, OGN-112 |
| shield | 24 | OGN-052, OGN-054, OGN-074 |
| deathknell | 24 | OGN-075, OGN-096, OGN-110 |
| tank | 23 | OGN-054, OGN-067, OGN-074 |
| ambush | 23 | UNL-002, UNL-012, UNL-021 |
| weaponmaster | 18 | SFD-002, SFD-008, SFD-085 |
| repeat | 17 | SFD-003, SFD-023, SFD-031 |
| hunt | 15 | UNL-016, UNL-034, UNL-040 |
| vision | 13 | OGN-086, OGN-100, OGN-171 |
| flow | 11 | VEN-003, VEN-012, VEN-031 |
| legion | 10 | OGN-012, OGN-016, OGN-020 |
| backline | 6 | UNL-043, UNL-090, UNL-090a |
| temporary | 5 | OGN-274, SFD-104, UNL-078 |
| quickdraw | 3 | SFD-022, SFD-056, SFD-064 |

## 4 按系列的适配进度

| 系列 | 已登记/总数 | 其中完备 |
|---|---|---|
| ARC | 3/6 | 0 |
| FND | 1/5 | 1 |
| OGN | 142/336 | 20 |
| OGS | 11/22 | 3 |
| SFD | 139/280 | 18 |
| SGN | 0/3 | 0 |
| UNL | 128/277 | 10 |
| VEN | 111/229 | 3 |

## 附：强制检查

- PASS：分层合计 = 可加载 defs 中非符文卡数（55+480+17+606=1158）
- PASS：登记卡全部存在于 defs（孤儿 0）
- PASS：报告全部数字由注册表与结构列直接统计，无文本解析依赖
