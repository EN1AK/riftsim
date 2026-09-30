# 自动生成草稿（scripts/cards/gen_cardfx_from_defs.py）；人工 review 后为事实源。
# CN 原文注释为权威面；rules_ref 锚点随 AbilityDef 携带。
from ..cards import AbilityDef
from ..enums import Keyword
from . import card


# OGN-001 灼焰飞龙
#   {{急速}}（你可以选择额外支付{{1}}和{{红色}}，让我以活跃状态进场。）
card("OGN-001", reviewed=True, keywords={Keyword.ACCELERATE})

# OGN-003 炼金太保
#   {{强攻2}}（如果我是进攻方，则{{S}}+2。）
#   当你打出我时，弃置一张手牌。
card("OGN-003", keywords={Keyword.ASSAULT}, keyword_values={"assault": 2})

# OGN-004 顺劈
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   让一名单位本回合内获得{{强攻3}}。（如果它是进攻方，则{{S}}+3。）
card("OGN-004", keywords={Keyword.ACTION})

# OGN-005 碎裂之火
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   对战场上的一名单位造成3点伤害。如果该单位被此法术摧毁，则抽一张牌。
card("OGN-005", keywords={Keyword.ACTION})

# OGN-008 罪恶快感
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   弃置一张手牌。对战场上的一名单位造成等同于被弃置手牌的法力费用的伤害。（无视其符能费用。）
card("OGN-008", keywords={Keyword.ACTION})

# OGN-009 海克斯射线
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   对战场上的一名单位造成3点伤害。
card("OGN-009", reviewed=True, keywords={Keyword.ACTION}, abilities=(
    AbilityDef(ability_id="OGN-009:spell_damage:0", kind="spell_damage", timing="passive", immediate=False, rules_ref=("R-CR-157.1", "R-CR-417.1",), damage=3, target_scope="unit_at_battlefield"),
))

# OGN-010 军团后卫
#   {{急速}}（你可以选择额外支付{{1}}和{{红色}}，让我以活跃状态进场。）
card("OGN-010", reviewed=True, keywords={Keyword.ACCELERATE})

# OGN-012 诺克萨斯新兵
#   {{鼓舞}}—我的费用减少{{2}}。（如果你在本回合内已打出过其他卡牌，则发动此效果。）
card("OGN-012", keywords={Keyword.LEGION})

# OGN-013 呸呸魄罗
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标）
card("OGN-013", reviewed=True, keywords={Keyword.DEFLECT})

# OGN-014 霹天雳地
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   将我的法力费用减去你所控制单位中的最高战力值，即为打出我所需的法力。
#   对战场上的一名单位造成5点伤害。
card("OGN-014", keywords={Keyword.ACTION}, abilities=(
    AbilityDef(ability_id="OGN-014:spell_damage:0", kind="spell_damage", timing="passive", immediate=False, rules_ref=("R-CR-157.1", "R-CR-417.1",), damage=5, target_scope="unit_at_battlefield"),
))

# OGN-016 危险二人组
#   {{鼓舞}}—当你打出我时，让一名单位本回合内{{S}}+2。（如果你在本回合内已打出过其他卡牌，则发动此效果。）
card("OGN-016", keywords={Keyword.LEGION})

# OGN-017 钢铁弩炮
#   此牌以休眠状态进场。
#   {{横置}}：对战场上的一名单位造成2点伤害。
card("OGN-017", abilities=(
    AbilityDef(ability_id="OGN-017:enters_exhausted:0", kind="enters_exhausted", timing="passive", immediate=False, rules_ref=("R-CR-369.3", "R-CR-143.4", "R-CR-359.2.c",)),
    AbilityDef(ability_id="OGN-017:exhaust_deal_damage:1", kind="deal_damage", cost_exhaust_self=True, immediate=False, rules_ref=("R-CR-377.1", "R-CR-135.2.e.2", "R-CR-414.1", "R-CR-417.1",), damage=2, target_scope="unit_at_battlefield"),
))

# OGN-020 垃圾场小霸王
#   {{鼓舞}}—当你打出我时，弃置两张手牌，然后抽两张牌。（如果你在本回合内已打出过其他卡牌，则发动此效果。）
card("OGN-020", keywords={Keyword.LEGION})

# OGN-022 热电光束
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   摧毁所有装备。
card("OGN-022", keywords={Keyword.ACTION})

# OGN-024 虚空索敌
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   对战场上的一名单位造成4点伤害，然后抽一张牌。
card("OGN-024", keywords={Keyword.ACTION})

# OGN-025 暴怒冲动
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   每名对手展示其主牌堆顶部的一张牌。你从中选择一张，并当作自己的牌打出，无视费用，然后回收其余的卡牌。
card("OGN-025", keywords={Keyword.ACTION})

# OGN-030 金克丝
#   {{急速}}（你可以选择额外支付{{1}}和{{红色}}，让我以活跃状态进场。）
#   {{强攻2}}（如果我是进攻方，则{{S}}+2。）
#   当你打出我时，弃置两张手牌。
card("OGN-030", keywords={Keyword.ACCELERATE, Keyword.ASSAULT}, keyword_values={"assault": 2})

# OGN-030a 金克丝
#   {{急速}}（你可以选择额外支付{{1}}和{{红色}}，让我以活跃状态进场。）
#   {{强攻2}}（如果我是进攻方，则{{S}}+2。）
#   当你打出我时，弃置两张手牌。
card("OGN-030a", keywords={Keyword.ACCELERATE, Keyword.ASSAULT}, keyword_values={"assault": 2})

# OGN-033 巧取豪夺
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   选择一名敌方单位。除非其控制者选择让你抽两张牌，否则对该单位造成6点伤害。
card("OGN-033", keywords={Keyword.REACTION})

# OGN-035 薇恩
#   {{强攻3}}（如果我是进攻方，则{{S}}+3。）
#   如果对手已控制任意战场，则我以活跃状态进场。每当我征服一处战场时，你可以选择支付{{1}}来让我返回所属的手牌。
card("OGN-035", keywords={Keyword.ASSAULT}, keyword_values={"assault": 3})

# OGN-036 蔚
#   {{游走}} （我可以向其他战场进行移动。）
#   你可以从废牌堆回收一张卡牌，然后让我本回合内{{S}}+1（可重复执行）。
card("OGN-036", keywords={Keyword.GANKING})

# OGN-037 不朽凤凰
#   {{强攻2}}（如果我是进攻方，则{{S}}+2。）
#   当你使用法术摧毁一名单位时，你可以选择支付{{1}}和{{红色}}，以此从废牌堆中将我打出。
card("OGN-037", keywords={Keyword.ASSAULT}, keyword_values={"assault": 2})

# OGN-039 卡莎
#   {{急速}}（你可以选择额外支付{{1}}和{{红色}}，让我以活跃状态进场。）
#   当我征服一处战场时，抽一张牌。
card("OGN-039", keywords={Keyword.ACCELERATE})

# OGN-039a 卡莎
#   {{急速}}（你可以选择额外支付{{1}}和{{红色}}，让我以活跃状态进场。）
#   当我征服一处战场时，抽一张牌。
card("OGN-039a", keywords={Keyword.ACCELERATE})

# OGN-040 暴怒之印
#   {{横置}}：{{反应}}—{{获得}}{{红色}}，用以支付符能费用。（获得费用资源的技能无法成为其他法术的反应目标。）
card("OGN-040", abilities=(
    AbilityDef(ability_id="OGN-040:gear_gain_resource:0", kind="gain_resource", timing="reaction", cost_exhaust_self=True, rules_ref=("R-CR-377.1", "R-CR-357.1.a", "R-CR-429.3", "R-CR-444.2.c",), grant_power_domain="R"),
))

# OGN-041 沃利贝尔
#   {{法盾2}}（对手必须额外支付{{A}}{{A}}才能将我选为法术或技能的目标。）
#   当我进攻时，对此处的敌方单位造成共计5点伤害，可在多名敌方单位之间分摊。
card("OGN-041", keywords={Keyword.DEFLECT}, keyword_values={"deflect": 2})

# OGN-041a 沃利贝尔
#   {{法盾2}}（对手必须额外支付{{A}}{{A}}才能将我选为法术或技能的目标。）
#   当我进攻时，对此处的敌方单位造成共计5点伤害，可在多名敌方单位之间分摊。
card("OGN-041a", keywords={Keyword.DEFLECT}, keyword_values={"deflect": 2})

# OGN-045 蔑视
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   无效化一个法术，但其费用不得高于{{4}}，也不得高于{{A}}。
card("OGN-045", keywords={Keyword.REACTION})

# OGN-046 决斗架势
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   让一名友方单位本回合内{{S}}+1，如果它是你在该处唯一控制的单位，则它本回合内额外获得{{S}}+1。
card("OGN-046", keywords={Keyword.REACTION})

# OGN-047 御衡守念
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   如果对手得分距离胜利得分不超过3分，则此法术的费用减少{{2}}。
#   抽一张牌，然后召出一枚休眠的符文。
card("OGN-047", keywords={Keyword.ACTION})

# OGN-048 冥想
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   抽一张牌。你可以选择让一名友方单位变为休眠状态作为额外费用，以此再抽一张牌。
card("OGN-048", keywords={Keyword.REACTION})

# OGN-050 符文禁锢
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   眩晕一名单位。（使其在本回合内无法造成战斗伤害。）
card("OGN-050", keywords={Keyword.ACTION})

# OGN-052 强强魄罗
#   {{坚守}}（如果我是防守方，则{{S}}+1。）
card("OGN-052", reviewed=True, keywords={Keyword.SHIELD})

# OGN-053 秘奥义！慈悲度魂落
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   给予一名友方单位增益。（如果该单位未拥有增益，则获得一个{{S}}+1增益。）
#   在本回合内，所有增益可额外给予友方单位{{S}}+1。
card("OGN-053", keywords={Keyword.ACTION, Keyword.HIDDEN})

# OGN-054 日耀卫队
#   {{坚守}}（如果我是防守方，则{{S}}+1。）
#   {{壁垒}}（我在战斗中首先承担伤害。）
card("OGN-054", reviewed=True, keywords={Keyword.SHIELD, Keyword.TANK})

# OGN-057 格挡
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   让一名单位在本回合内获得{{坚守3}}和{{壁垒}}。（如果它是防守方，则{{S}}+3。它在战斗中首先承担伤害。）
card("OGN-057", keywords={Keyword.ACTION, Keyword.HIDDEN})

# OGN-058 训练有素
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   让一名单位在本回合内{{S}}+2，然后抽一张牌。
card("OGN-058", keywords={Keyword.REACTION})

# OGN-064 风之障壁
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   无效化一个法术。
card("OGN-064", keywords={Keyword.REACTION})

# OGN-067 布里茨
#   {{壁垒}}（我在战斗中首先承担伤害。）
#   每当你将我打出到一处战场时，你可以选择移动任意一名敌方单位到此处。
#   当我据守一处战场时，把我送回所属的手牌。
card("OGN-067", keywords={Keyword.TANK})

# OGN-068 凯特琳
#   我在战斗中最后承担伤害。
#   {{横置}}：对任意战场中的一个敌方单位造成等同于我战力的伤害。我必须位于战场中才能使用此技能。
card("OGN-068", abilities=(
    AbilityDef(ability_id="OGN-068:last_damage:0", kind="last_damage", timing="passive", immediate=False, rules_ref=("R-CR-465.2.c.2",)),
))

# OGN-069 背水一战
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   让一名友方单位在本回合内战力翻倍，并让其变为{{瞬息}}。（在你下个回合开始阶段，结算得分之前将其摧毁。）
card("OGN-069", keywords={Keyword.ACTION})

# OGN-074 塔里克
#   {{坚守}}（如果我是防守方，则{{S}}+1。）
#   {{壁垒}}（我在战斗中首先承担伤害。）
#   此处的其他友方单位获得{{坚守}}。
card("OGN-074", keywords={Keyword.SHIELD, Keyword.TANK})

# OGN-075 美味仙灵
#   {{急速}}（你可以选择额外支付{{1}}和{{绿色}}，让我以活跃状态进场。）
#   {{绝念}}—召出两枚休眠的符文，再抽一张牌。（当我被摧毁后，发动此效果。）
card("OGN-075", keywords={Keyword.ACCELERATE, Keyword.DEATHKNELL})

# OGN-077 中娅沙漏
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   下一次当友方单位被摧毁时，改为将此牌摧毁，然后以休眠状态将该单位召回。（把该单位送回基地，此行动不算作移动。）
card("OGN-077", keywords={Keyword.HIDDEN})

# OGN-078 李青
#   {{坚守}}（如果我是防守方，则{{S}}+1。）
#   {{横置}}：给予我增益。（我获得一个{{S}}+1增益。）
#   我可以拥有不限数量的增益。
card("OGN-078", keywords={Keyword.SHIELD})

# OGN-078a 李青
#   {{坚守}}（如果我是防守方，则{{S}}+1。）
#   {{横置}}：给予我增益。（我获得一个{{S}}+1增益。）
#   我可以拥有不限数量的增益。
card("OGN-078a", keywords={Keyword.SHIELD})

# OGN-080 倒转神通
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   获得一个法术的控制权。你可以选择为其指定新的目标。
card("OGN-080", keywords={Keyword.REACTION})

# OGN-081 专注之印
#   {{横置}}：{{反应}}—{{获得}}{{绿色}}，用以支付符能费用。（获得费用资源的技能无法成为其他法术的反应目标。）
card("OGN-081", abilities=(
    AbilityDef(ability_id="OGN-081:gear_gain_resource:0", kind="gain_resource", timing="reaction", cost_exhaust_self=True, rules_ref=("R-CR-377.1", "R-CR-357.1.a", "R-CR-429.3", "R-CR-444.2.c",), grant_power_domain="G"),
))

# OGN-083 借鉴历史
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   抽两张牌。
# 手写（fx-4）：spell_draw=2；OGN-083 原文「抽两张牌。」中文数字。
card("OGN-083", keywords={Keyword.HIDDEN, Keyword.REACTION}, reviewed=True, abilities=(
    AbilityDef(ability_id="OGN-083:spell_draw:0", kind="spell_draw", timing="passive",
               immediate=False, rules_ref=("R-CR-157.1", "R-CR-413.1"), draw_count=2),
))

# OGN-085 彗星坠击
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   对战场上的一名单位造成6点伤害。
card("OGN-085", reviewed=True, keywords={Keyword.ACTION}, abilities=(
    AbilityDef(ability_id="OGN-085:spell_damage:0", kind="spell_damage", timing="passive", immediate=False, rules_ref=("R-CR-157.1", "R-CR-417.1",), damage=6, target_scope="unit_at_battlefield"),
))

# OGN-086 宝石巨像
#   {{预知}}（当你打出我时，查看主牌堆顶部的一张牌，你可以选择将其回收。）
#   {{坚守}}（如果我是防守方，则{{S}}+1。）
card("OGN-086", reviewed=True, keywords={Keyword.SHIELD, Keyword.VISION})

# OGN-087 约德尔教官
#   {{壁垒}}（我在战斗中首先承担伤害。）
#   当你打出我时，抽一张牌。
card("OGN-087", reviewed=True, keywords={Keyword.TANK}, abilities=(
    AbilityDef(ability_id="OGN-087:on_play_draw:0", kind="on_play_draw", timing="trigger", immediate=False, rules_ref=("R-CR-383.1", "R-CR-413.1",), draw_count=1),
))

# OGN-093 烟幕弹
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   让一名单位在本回合内{{S}}-4，不得低于1{{S}}。
card("OGN-093", keywords={Keyword.REACTION})

# OGN-094 精灵召唤
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   打出一个处于活跃状态的3{{S}}“精灵”，它拥有{{瞬息}}。（在其控制者的下个回合开始阶段，结算得分之前将其摧毁。）
card("OGN-094", keywords={Keyword.ACTION, Keyword.HIDDEN})

# OGN-095 “敲”诈
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   让一名单位在本回合内{{S}}-1，不得低于1{{S}}。抽一张牌。
card("OGN-095", keywords={Keyword.REACTION})

# OGN-096 警觉的哨兵
#   {{绝念}}—抽一张牌。（当我被摧毁后，发动此效果。）
card("OGN-096", keywords={Keyword.DEATHKNELL})

# OGN-097 爆裂球果仙灵
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   当你打出我时，让一名单位本回合内{{S}}-2，不得低于1{{S}}。
card("OGN-097", keywords={Keyword.HIDDEN})

# OGN-100 宝石真知者
#   {{预知}}（当你打出我时，查看主牌堆顶部的一张牌，你可以选择将其回收。）
#   其他友方单位获得{{预知}}。
card("OGN-100", keywords={Keyword.VISION})

# OGN-102 传送门大营救
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   放逐一名友方单位，然后让其拥有者将它打出到其所属的基地，无视费用。
card("OGN-102", keywords={Keyword.ACTION})

# OGN-104 择日再战
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   让一名友方单位返回其所属的手牌，然后让其拥有者召出一枚休眠的符文。
card("OGN-104", keywords={Keyword.REACTION})

# OGN-108 聚合变异
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   选择一名友方单位。如果其战力低于另一名友方单位，则让其在本回合内变为后者的战力。
card("OGN-108", keywords={Keyword.REACTION})

# OGN-110 艾克
#   {{急速}}（你可以选择额外支付{{1}}和{{蓝色}}，让我以活跃状态进场。）
#   {{绝念}}—回收我，以此让你的所有符文变为活跃状态。（当我被摧毁后，发动此效果。）
card("OGN-110", keywords={Keyword.ACCELERATE, Keyword.DEATHKNELL})

# OGN-112 卡莎
#   {{游走}}（我可以向其他战场进行移动。）
#   当我征服一处战场时，你可以选择从废牌堆中打出一张法力费用低于你当前分数的法术牌，无需支付其法力费用，然后将其回收（仍需支付所有符能费用）。
card("OGN-112", keywords={Keyword.GANKING})

# OGN-112a 卡莎
#   {{游走}}（我可以向其他战场进行移动。）
#   当我征服一处战场时，你可以选择从废牌堆中打出一张法力费用低于你当前分数的法术牌，无需支付其法力费用，然后将其回收（仍需支付所有符能费用）。
card("OGN-112a", keywords={Keyword.GANKING})

# OGN-116 千尾监视者
#   {{急速}}（你可以选择额外支付{{1}}和{{蓝色}}，让我以活跃状态进场。）
#   当你打出我时，让所有敌方单位本回合内{{S}}-3，不得低于1{{S}}。
card("OGN-116", keywords={Keyword.ACCELERATE})

# OGN-120 洞察之印
#   {{横置}}：{{反应}}—{{获得}}{{蓝色}}，用以支付符能费用。（获得费用资源的技能无法成为其他法术的反应目标。）
card("OGN-120", abilities=(
    AbilityDef(ability_id="OGN-120:gear_gain_resource:0", kind="gain_resource", timing="reaction", cost_exhaust_self=True, rules_ref=("R-CR-377.1", "R-CR-357.1.a", "R-CR-429.3", "R-CR-444.2.c",), grant_power_domain="B"),
))

# OGN-121 提莫
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   当我防守一处战场、或从正面朝下的{{待命}}状态中打出时，展示你主牌堆顶部的五张牌，当中每有一张带有{{待命}}技能的卡牌，就对此处的一名敌方单位造成1点伤害，然后将展示的牌回收。
card("OGN-121", keywords={Keyword.HIDDEN})

# OGN-121a 提莫
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   当我防守一处战场、或从正面朝下的{{待命}}状态中打出时，展示你主牌堆顶部的五张牌，当中每有一张带有{{待命}}技能的卡牌，就对此处的一名敌方单位造成1点伤害，然后将展示的牌回收。
card("OGN-121a", keywords={Keyword.HIDDEN})

# OGN-127 加农炮幕
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   对战斗中的所有敌方单位各造成2点伤害。
card("OGN-127", keywords={Keyword.REACTION})

# OGN-128 决斗
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   选择任意一名友方和一名敌方单位，让这两名单位相互以自身战力给对方造成伤害。
card("OGN-128", keywords={Keyword.ACTION})

# OGN-129 迎敌号令
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   在本回合内，你打出的所有单位以活跃状态进场。抽一张牌。
card("OGN-129", keywords={Keyword.ACTION})

# OGN-133 剑刃飓风
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   对所有战场上的单位各造成1点伤害，不分敌我。
card("OGN-133", keywords={Keyword.REACTION})

# OGN-135 帕卡幼崽
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
card("OGN-135", reviewed=True, keywords={Keyword.HIDDEN})

# OGN-137 雷爪氏族熊人
#   {{壁垒}}（我在战斗中首先承担伤害。）
#   当你打出我时，召出一枚休眠的符文。
card("OGN-137", keywords={Keyword.TANK})

# OGN-144 以战养战
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   如果本回合内有一名敌方单位被摧毁，则此牌的费用减少{{2}}。
#   抽两张牌。
card("OGN-144", keywords={Keyword.REACTION})

# OGN-145 坚毅不倒
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   无效化本回合内所有法术或技能的伤害。
card("OGN-145", keywords={Keyword.REACTION})

# OGN-146 痛殴
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   当你打出此牌时，你可以选择消耗一个增益作为额外费用，以此无视此法术的费用。
#   让一名单位变为活跃状态。
card("OGN-146", keywords={Keyword.ACTION})

# OGN-150 海妖猎手
#   {{急速}}（你可以选择额外支付{{1}}和{{橙色}},让我以活跃状态进场。)
#   {{强攻}}(如果我是进攻方，则{{S}}+1。）
#   当你打出我时，可以选择消耗任意数量的增益作为额外费用。每消耗一个增益，就让我的费用减少{{橙色}}。
card("OGN-150", keywords={Keyword.ACCELERATE, Keyword.ASSAULT})

# OGN-151 李青
#   {{急速}}(你可以选择额外支付{{1}}和{{橙色}},让我以活跃状态进场。）
#   我所在战场上其他拥有增益的友方单位获得{{S}}+2。
card("OGN-151", keywords={Keyword.ACCELERATE})

# OGN-151a 李青
#   {{急速}}(你可以选择额外支付{{1}}和{{橙色}},让我以活跃状态进场。）
#   我所在战场上其他拥有增益的友方单位获得{{S}}+2。
card("OGN-151a", keywords={Keyword.ACCELERATE})

# OGN-153 公开行动
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   你可以选择任意数量拥有增益的友方单位，消耗他们身上的增益，以此让他们变为活跃状态。然后，给予所有友方单位增益。（每名未拥有增益的单位获得一个{{S}}+1增益。）
card("OGN-153", keywords={Keyword.ACTION})

# OGN-154 洪荒巨力
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   让一名单位在本回合内{{S}}+7。
# 手写（fx-4）：spell_pump=+7 @任一单位（474 加减层；317.2.c 回合结束失效）
card("OGN-154", keywords={Keyword.ACTION}, reviewed=True, abilities=(
    AbilityDef(ability_id="OGN-154:spell_pump:0", kind="spell_pump", timing="passive",
               immediate=False,
               rules_ref=("R-CR-157.1", "R-CR-355.6", "R-CR-317.2.c", "R-CR-474"),
               pump_value=7, target_scope="unit"),
))

# OGN-155 奇亚娜
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   当我征服一处战场时，抽一张牌或召出一枚休眠的符文。
card("OGN-155", keywords={Keyword.DEFLECT})

# OGN-158 沃利贝尔
#   {{坚守3}}（如果我是防守方，则{{S}}+3。）
#   {{壁垒}}（我在战斗中首先承担伤害。）
#   每当对手移动单位到我不在的其他战场时，你抽一张牌。（基地不算作战场。）
card("OGN-158", keywords={Keyword.SHIELD, Keyword.TANK}, keyword_values={"shield": 3})

# OGN-158a 沃利贝尔
#   {{坚守3}}（如果我是防守方，则{{S}}+3。）
#   {{壁垒}}（我在战斗中首先承担伤害。）
#   每当对手移动单位到我不在的其他战场时，你抽一张牌。（基地不算作战场。）
card("OGN-158a", keywords={Keyword.SHIELD, Keyword.TANK}, keyword_values={"shield": 3})

# OGN-159 沃里克
#   我以活跃状态进场。
#   当我进攻时，摧毁此处所有已受伤的敌方单位。
card("OGN-159", abilities=(
    AbilityDef(ability_id="OGN-159:enters_ready:0", kind="enters_ready", timing="passive", immediate=False, rules_ref=("R-CR-369.3", "R-CR-359.2.c",)),
))

# OGN-161 亡花掠食者
#   {{法盾}}（对手必须支付{{A}}才能将我作为法术或技能的目标。）
#   你可以选择将我打出到敌方控制的战场。
card("OGN-161", keywords={Keyword.DEFLECT})

# OGN-162 厄运小姐
#   {{急速}}（你可以选择额外支付{{1}}和{{橙色}}，让我以活跃状态进场。）
#   {{游走}}（我可以向其他战场进行移动。）
#   每回合首次：当我移动时，让一个其他休眠的物体变为活跃状态（包括传奇和符文）。
card("OGN-162", keywords={Keyword.ACCELERATE, Keyword.GANKING})

# OGN-162a 厄运小姐
#   {{急速}}（你可以选择额外支付{{1}}和{{橙色}}，让我以活跃状态进场。）
#   {{游走}}（我可以向其他战场进行移动。）
#   每回合首次：当我移动时，让一个其他休眠的物体变为活跃状态（包括传奇和符文）。
card("OGN-162a", keywords={Keyword.ACCELERATE, Keyword.GANKING})

# OGN-163 力量之印
#   {{横置}}：{{反应}}—{{获得}}{{橙色}}，用以支付符能费用。（获得费用资源的技能无法成为其他法术的反应目标。）
card("OGN-163", abilities=(
    AbilityDef(ability_id="OGN-163:gear_gain_resource:0", kind="gain_resource", timing="reaction", cost_exhaust_self=True, rules_ref=("R-CR-377.1", "R-CR-357.1.a", "R-CR-429.3", "R-CR-444.2.c",), grant_power_domain="O"),
))

# OGN-168 战或逃
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   将一名单位从战场上移动到其所属的基地。
card("OGN-168", keywords={Keyword.ACTION, Keyword.HIDDEN})

# OGN-169 罡风
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   让战场上一名不高于3{{S}}的单位返回其所属的手牌。
card("OGN-169", keywords={Keyword.REACTION})

# OGN-170 亡者复生
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   让你废牌堆里的一名单位返回手牌。
card("OGN-170", keywords={Keyword.ACTION})

# OGN-171 叨叨魄罗
#   {{预知}}（当你打出我时，查看主牌堆顶部的一张牌，你可以选择将其回收。）
card("OGN-171", reviewed=True, keywords={Keyword.VISION})

# OGN-172 责退
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   让一名战场上的单位返回其所属的手牌。
card("OGN-172", keywords={Keyword.ACTION})

# OGN-173 驭风而行
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   移动一名友方单位，然后让其变为活跃状态。
card("OGN-173", keywords={Keyword.ACTION})

# OGN-174 大塞斥候
#   {{预知}}（当你打出我时，查看主牌堆顶部的一张牌，你可以选择将其回收。）
#   你可以选择将我打出到一处开放的战场。
card("OGN-174", keywords={Keyword.VISION}, abilities=(
    AbilityDef(ability_id="OGN-174:location_open_battlefield:0", kind="location_open_battlefield", timing="passive", immediate=False, rules_ref=("R-CR-170.11", "R-CR-170.11.c",)),
))

# OGN-176 鬼祟的水手
#   你可以选择将我打出到一处开放的战场。
card("OGN-176", abilities=(
    AbilityDef(ability_id="OGN-176:location_open_battlefield:0", kind="location_open_battlefield", timing="passive", immediate=False, rules_ref=("R-CR-170.11", "R-CR-170.11.c",)),
))

# OGN-178 卧底特工
#   {{绝念}}—弃置两张手牌，然后抽两张牌。（当我被摧毁后，发动此效果。）
card("OGN-178", keywords={Keyword.DEATHKNELL})

# OGN-179 折戟再战
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   每名玩家摧毁自己的一件装备。
card("OGN-179", keywords={Keyword.ACTION})

# OGN-183 卡牌骗术
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   查看你主牌堆顶部的三张牌。选择其中一张加入手牌，并回收其余的卡牌。
card("OGN-183", keywords={Keyword.ACTION})

# OGN-189 凯隐
#   {{游走}}（我可以向其他战场进行移动。）
#   在本回合内，如果我移动了两次，则我免疫伤害。
card("OGN-189", keywords={Keyword.GANKING})

# OGN-190 克格莫
#   {{绝念}}-对我所处战场上的所有单位各造成4点伤害。（当我被摧毁后，发动此效果。）
card("OGN-190", keywords={Keyword.DEATHKNELL})

# OGN-191 疯狂海寇
#   {{壁垒}}（我在战斗中首先承担伤害。）
#   当你打出我时，将一名单位从战场上移动到其所属的基地。
card("OGN-191", keywords={Keyword.TANK})

# OGN-193 厄运小姐
#   你可以选择将我打出到一处开放的战场。
#   当我在场上时，你可以选择将友方单位打出到一处开放的战场。
card("OGN-193", abilities=(
    AbilityDef(ability_id="OGN-193:location_open_battlefield:0", kind="location_open_battlefield", timing="passive", immediate=False, rules_ref=("R-CR-170.11", "R-CR-170.11.c",)),
))

# OGN-193a 厄运小姐
#   你可以选择将我打出到一处开放的战场。
#   当我在场上时，你可以选择将友方单位打出到一处开放的战场。
card("OGN-193a", abilities=(
    AbilityDef(ability_id="OGN-193a:location_open_battlefield:0", kind="location_open_battlefield", timing="passive", immediate=False, rules_ref=("R-CR-170.11", "R-CR-170.11.c",)),
))

# OGN-193b 厄运小姐
#   你可以选择将我打出到一处开放的战场。
#   当我在场上时，你可以选择将友方单位打出到一处开放的战场。
card("OGN-193b", abilities=(
    AbilityDef(ability_id="OGN-193b:location_open_battlefield:0", kind="location_open_battlefield", timing="passive", immediate=False, rules_ref=("R-CR-170.11", "R-CR-170.11.c",)),
))

# OGN-194 魔腾
#   {{游走}}（我可以向其他战场进行移动。）
#   当你查看主牌堆顶部的卡牌（不是抽牌）并看到我时，可以选择支付{{A}}将我打出。
card("OGN-194", keywords={Keyword.GANKING})

# OGN-197 提莫
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   当你打出我时，让我本回合内{{S}}+3。
# 手写（fx-4）：on_play_pump=+3（383.1 进场触发；317.2.c 回合结束失效）
card("OGN-197", keywords={Keyword.HIDDEN}, reviewed=True, abilities=(
    AbilityDef(ability_id="OGN-197:on_play_pump:1", kind="on_play_pump", timing="passive",
               immediate=False, rules_ref=("R-CR-383.1", "R-CR-317.2.c", "R-CR-474"),
               pump_value=3),
))

# OGN-197a 提莫
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   当你打出我时，让我本回合内{{S}}+3。
card("OGN-197a", keywords={Keyword.HIDDEN}, reviewed=True, abilities=(
    AbilityDef(ability_id="OGN-197a:on_play_pump:1", kind="on_play_pump", timing="passive",
               immediate=False, rules_ref=("R-CR-383.1", "R-CR-317.2.c", "R-CR-474"),
               pump_value=3),
))

# OGN-197b 提莫
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   当你打出我时，让我本回合内{{S}}+3。
card("OGN-197b", keywords={Keyword.HIDDEN}, reviewed=True, abilities=(
    AbilityDef(ability_id="OGN-197b:on_play_pump:1", kind="on_play_pump", timing="passive",
               immediate=False, rules_ref=("R-CR-383.1", "R-CR-317.2.c", "R-CR-474"),
               pump_value=3),
))

# OGN-199 控潮者
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   当你打出我时，你可以选择受你控制的一名单位，然后把我移动到其所在位置，再将其移动到我原来的位置。
card("OGN-199", keywords={Keyword.HIDDEN})

# OGN-203 据为己有
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   选择战场上的一名敌方单位，获得它的控制权并将其召回。（将其送到你的基地。此动作不被视为移动。）
card("OGN-203", keywords={Keyword.ACTION})

# OGN-204 不和之印
#   {{横置}}：{{反应}}—{{获得}}{{紫色}}，用以支付符能费用。（获得费用资源的技能无法成为其他法术的反应目标。）
card("OGN-204", abilities=(
    AbilityDef(ability_id="OGN-204:gear_gain_resource:0", kind="gain_resource", timing="reaction", cost_exhaust_self=True, rules_ref=("R-CR-377.1", "R-CR-357.1.a", "R-CR-429.3", "R-CR-444.2.c",), grant_power_domain="P"),
))

# OGN-205 亚索
#   {{游走}}（我可以向其他战场进行移动。）
#   当我在一个回合内进行了第三次移动，你获得1分。
card("OGN-205", keywords={Keyword.GANKING})

# OGN-205a 亚索
#   {{游走}}（我可以向其他战场进行移动。）
#   当我在一个回合内进行了第三次移动，你获得1分。
card("OGN-205a", keywords={Keyword.GANKING})

# OGN-206 背靠背
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   让两名友方单位本回合内{{S}}+2。
card("OGN-206", keywords={Keyword.REACTION})

# OGN-207 荣耀召唤
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   打出此牌时，你可以选择消耗一个增益作为额外费用，以此无视本法术的费用。让一名单位本回合内{{S}}+3。
card("OGN-207", keywords={Keyword.REACTION})

# OGN-210 莽莽魄罗
#   {{强攻}}（如果我是进攻方，则{{S}}+1。）
card("OGN-210", reviewed=True, keywords={Keyword.ASSAULT})

# OGN-213 暗刃
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   摧毁战场中的一名单位，然后让其控制者抽两张牌。
card("OGN-213", keywords={Keyword.ACTION, Keyword.HIDDEN})

# OGN-215 躁烈的副官
#   {{强攻}}（如果我是进攻方，则{{S}}+1。）
card("OGN-215", reviewed=True, keywords={Keyword.ASSAULT})

# OGN-216 侦察飞鹰
#   {{绝念}}—召出一枚休眠的符文。（当我被摧毁后，发动此效果。）
card("OGN-216", keywords={Keyword.DEATHKNELL})

# OGN-217 崔法利求战者
#   {{鼓舞}}—当你打出我时，给予我增益。（如果我未拥有增益，则我获得一个{{S}}+1增益。如果你在本回合内已打出过其他卡牌，则发动此效果。）
card("OGN-217", keywords={Keyword.LEGION})

# OGN-218 先锋队长
#   {{鼓舞}}—当你打出我时，在此处额外打出两名1{{S}}的“随从”。（当你打出我时，如果你在本回合内已打出过其他卡牌，则发动此效果。）
card("OGN-218", keywords={Keyword.LEGION})

# OGN-220 强手裂颅
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   眩晕位于同一个战场上的一名友方单位和一名敌方单位。（使其在本回合内无法造成战斗伤害。）
card("OGN-220", keywords={Keyword.ACTION, Keyword.HIDDEN})

# OGN-221 帝国谕令
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   在本回合内，每当任意单位承受伤害时，直接将它摧毁。
card("OGN-221", keywords={Keyword.ACTION})

# OGN-224 废物利用
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   你可以选择摧毁一件装备，然后抽一张牌。
card("OGN-224", keywords={Keyword.ACTION})

# OGN-231 莱卓斯指挥官
#   当你打出我时，你可以选择摧毁任意数量的友方单位作为额外费用。每用这个方法摧毁一个友方单位，便让我的费用减少{{黄色}}。
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   {{游走}}（我可以向其他战场进行移动。）
card("OGN-231", keywords={Keyword.DEFLECT, Keyword.GANKING})

# OGN-233 宏伟战略
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   在本回合内，让所有友方单位{{S}}+5。
card("OGN-233", keywords={Keyword.ACTION})

# OGN-235 卡尔玛
#   {{预知}}（当你打出我时，查看主牌堆顶部的一张牌，你可以选择将其回收。）
#   每当你回收任意数量的卡牌时，给予一名友方单位增益。（如果该单位未拥有增益，则获得一个{{S}}+1增益。符文不被视为卡牌。）
card("OGN-235", keywords={Keyword.VISION})

# OGN-238 蕾欧娜
#   {{坚守}}（如果我是防守方，则{{S}}+1。）
#   当我进攻时，眩晕此处的一名敌方单位。（使其在本回合内无法造成战斗伤害。）
card("OGN-238", keywords={Keyword.SHIELD})

# OGN-238a 蕾欧娜
#   {{坚守}}（如果我是防守方，则{{S}}+1。）
#   当我进攻时，眩晕此处的一名敌方单位。（使其在本回合内无法造成战斗伤害。）
card("OGN-238a", keywords={Keyword.SHIELD})

# OGN-239 机械戏法师
#   {{绝念}}—打出三名1{{S}}的“随从”到你的基地。（当我被摧毁后，发动此效果。）
card("OGN-239", keywords={Keyword.DEATHKNELL})

# OGN-240 瑟提
#   {{壁垒}}（我在战斗中首先承担伤害。）
#   我所处的战场每有一名拥有增益的友方单位，我便获得{{S}}+1。
card("OGN-240", keywords={Keyword.TANK})

# OGN-240a 瑟提
#   {{壁垒}}（我在战斗中首先承担伤害。）
#   我所处的战场每有一名拥有增益的友方单位，我便获得{{S}}+1。
card("OGN-240a", keywords={Keyword.TANK})

# OGN-241 慎
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算，并能打出到你控制的战场。）
#   {{坚守2}}（如果我是防守方，则{{S}}+2。）
#   {{壁垒}}（我在战斗中首先承担伤害。）
card("OGN-241", reviewed=True, keywords={Keyword.REACTION, Keyword.SHIELD, Keyword.TANK}, keyword_values={"shield": 2})

# OGN-243 德莱厄斯
#   {{鼓舞}}—当你打出我时，让我变为活跃状态。（如果你在本回合内已打出过其他卡牌，则发动此效果。）
#   此处的其他友方单位获得{{S}}+1。
card("OGN-243", keywords={Keyword.LEGION})

# OGN-243a 德莱厄斯
#   {{鼓舞}}—当你打出我时，让我变为活跃状态。（如果你在本回合内已打出过其他卡牌，则发动此效果。）
#   此处的其他友方单位获得{{S}}+1。
card("OGN-243a", keywords={Keyword.LEGION})

# OGN-245 团结之印
#   {{横置}}：{{反应}}—{{获得}}{{黄色}}，用以支付符能费用。（获得费用资源的技能无法成为其他法术的反应目标。）
card("OGN-245", abilities=(
    AbilityDef(ability_id="OGN-245:gear_gain_resource:0", kind="gain_resource", timing="reaction", cost_exhaust_self=True, rules_ref=("R-CR-377.1", "R-CR-357.1.a", "R-CR-429.3", "R-CR-444.2.c",), grant_power_domain="Y"),
))

# OGN-256 妖异狐火
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   摧毁一处战场中任意数量的单位，这些单位总计战力不得高于4。
card("OGN-256", keywords={Keyword.ACTION, Keyword.HIDDEN})

# OGN-268 弹幕时间
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   支付任意数量的{{A}}，对一处战场上的所有敌方单位造成等同于该数量的伤害。
card("OGN-268", keywords={Keyword.ACTION})

# OGN-274 精灵
#   {{瞬息}}（在控制者的下个回合开始阶段，结算得分之前将我摧毁。）
card("OGN-274", reviewed=True, keywords={Keyword.TEMPORARY})

