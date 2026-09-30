# 自动生成草稿（scripts/cards/gen_cardfx_from_defs.py）；人工 review 后为事实源。
# CN 原文注释为权威面；rules_ref 锚点随 AbilityDef 携带。
from ..cards import AbilityDef
from ..enums import Keyword
from . import card


# ARC-001 蔚
#   {{游走}} （我可以向其他战场进行移动。）
#   你可以从废牌堆回收一张卡牌，然后让我本回合内{{S}}+1（可重复执行）。
card("ARC-001", keywords={Keyword.GANKING})

# ARC-002 凯特琳
#   我在战斗中最后承担伤害。
#   {{横置}}：对任意战场中的一个敌方单位造成等同于我战力的伤害。我必须位于战场中才能使用此技能。
card("ARC-002", abilities=(
    AbilityDef(ability_id="ARC-002:last_damage:0", kind="last_damage", timing="passive", immediate=False, rules_ref=("R-CR-465.2.c.2",)),
))

# ARC-004 沃里克
#   我以活跃状态进场。
#   当我进攻时，摧毁此处所有已受伤的敌方单位。
card("ARC-004", abilities=(
    AbilityDef(ability_id="ARC-004:enters_ready:0", kind="enters_ready", timing="passive", immediate=False, rules_ref=("R-CR-369.3", "R-CR-359.2.c",)),
))

