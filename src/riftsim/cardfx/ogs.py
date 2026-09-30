# 自动生成草稿（scripts/cards/gen_cardfx_from_defs.py）；人工 review 后为事实源。
# CN 原文注释为权威面；rules_ref 锚点随 AbilityDef 携带。
from ..cards import AbilityDef
from ..enums import Keyword
from . import card


# OGS-003 焚烧
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   对战场上的一名单位造成2点伤害。
card("OGS-003", reviewed=True, keywords={Keyword.ACTION}, abilities=(
    AbilityDef(ability_id="OGS-003:spell_damage:0", kind="spell_damage", timing="passive", immediate=False, rules_ref=("R-CR-157.1", "R-CR-417.1",), damage=2, target_scope="unit_at_battlefield"),
))

# OGS-005 和风贤者
#   {{坚守}}（如果我是防守方，则{{S}}+1。）
card("OGS-005", reviewed=True, keywords={Keyword.SHIELD})

# OGS-007 盖伦
#   {{强攻2}}（如果我是进攻方，则{{S}}+2。）
#   {{坚守2}}（如果我是防守方，则{{S}}+2。）
card("OGS-007", reviewed=True, keywords={Keyword.ASSAULT, Keyword.SHIELD}, keyword_values={"assault": 2, "shield": 2})

# OGS-008 绅士决斗
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   让一名友方单位本回合内{{S}}+3。随后，选择一名敌方单位，让这两名单位互相以自身战力给对方造成伤害。
card("OGS-008", keywords={Keyword.ACTION})

# OGS-009 易
#   {{游走}}（我可以向其他战场进行移动。）
#   我以活跃状态进场。
card("OGS-009", keywords={Keyword.GANKING}, abilities=(
    AbilityDef(ability_id="OGS-009:enters_ready:0", kind="enters_ready", timing="passive", immediate=False, rules_ref=("R-CR-369.3", "R-CR-359.2.c",)),
))

# OGS-011 闪现
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   将最多两名友方单位从战场上移动到基地。
card("OGS-011", keywords={Keyword.REACTION})

# OGS-012 爆能术
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   摧毁战场上的一名单位。
card("OGS-012", keywords={Keyword.ACTION})

# OGS-015 共同献身
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   打出四名1{{S}}的“随从”。（可以将其打出到你的基地或你已控制的战场。）
card("OGS-015", keywords={Keyword.ACTION})

# OGS-016 先锋扈从
#   我以活跃状态进场。
card("OGS-016", abilities=(
    AbilityDef(ability_id="OGS-016:enters_ready:0", kind="enters_ready", timing="passive", immediate=False, rules_ref=("R-CR-369.3", "R-CR-359.2.c",)),
))

# OGS-020 高原血统
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   选择一名友方单位。如果该单位在本回合内被摧毁，则改为以休眠状态将其召回。（把该单位送回基地，此行动不算作移动。）
card("OGS-020", keywords={Keyword.REACTION})

# OGS-022 终极闪光
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   对一名单位造成8点伤害。
card("OGS-022", keywords={Keyword.ACTION})

