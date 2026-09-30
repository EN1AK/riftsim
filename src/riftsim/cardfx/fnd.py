# 自动生成草稿（scripts/cards/gen_cardfx_from_defs.py）；人工 review 后为事实源。
# CN 原文注释为权威面；rules_ref 锚点随 AbilityDef 携带。
from ..cards import AbilityDef
from ..enums import Keyword
from . import card


# FND-196 提莫
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   当你打出我时，让我本回合内{{S}}+3。
# 手写（rq-2a）：on_play_pump=+3（383.1 进场触发；317.2.c 回合结束失效）
card("FND-196", keywords={Keyword.HIDDEN}, reviewed=True, abilities=(
    AbilityDef(ability_id="FND-196:on_play_pump:1", kind="on_play_pump", timing="passive",
               immediate=False, rules_ref=("R-CR-383.1", "R-CR-317.2.c", "R-CR-474"),
               pump_value=3),
))

