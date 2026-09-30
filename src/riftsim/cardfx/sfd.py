# 自动生成草稿（scripts/cards/gen_cardfx_from_defs.py）；人工 review 后为事实源。
# CN 原文注释为权威面；rules_ref 锚点随 AbilityDef 携带。
from ..cards import AbilityDef
from ..enums import Keyword
from . import card


# SFD-001 矢志不退
#   {{反应}} （可在任意时机打出，甚至先于其他法术和技能的结算。）
#   选择战场上的一名友方单位，此战场上每有一名敌方单位，就让该友方单位在本回合内{{S}}+2。
card("SFD-001", keywords={Keyword.REACTION})

# SFD-002 武装强袭者
#   {{急速}}（你可以选择额外支付{{1}}和{{红色}}，让我以活跃状态进场。）
#   {{百炼}}（当你打出我时，你可以选择为我{{装配}}你的一件武装，其装配费用减少{{A}}。可选择已贴附的武装。）
card("SFD-002", keywords={Keyword.ACCELERATE, Keyword.WEAPONMASTER})

# SFD-003 血性冲刺
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   {{回响1}}（你可以选择支付此额外费用，以重复此法术效果。）
#   让一名单位获得{{强攻2}}。（如果它是进攻方，则{{S}}+2。）
card("SFD-003", keywords={Keyword.ACTION, Keyword.REPEAT})

# SFD-004 丛林伏击
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   在本回合内，友方单位以活跃状态进场。打出一个休眠的“金币”装备指示物。
card("SFD-004", keywords={Keyword.HIDDEN})

# SFD-006 好斗的龙犬
#   我以活跃状态进场。
card("SFD-006", abilities=(
    AbilityDef(ability_id="SFD-006:enters_ready:0", kind="enters_ready", timing="passive", immediate=False, rules_ref=("R-CR-369.3", "R-CR-359.2.c",)),
))

# SFD-008 哨兵好手
#   {{百炼}}（当你打出我时，你可以选择为我{{装配}}你的一件武装，其装配费用减少{{A}}。可选择已贴附的武装。）
card("SFD-008", keywords={Keyword.WEAPONMASTER})

# SFD-009 锯齿短匕
#   {{装配红色}}（支付{{红色}}：将此牌贴附到你控制的一名单位上。）
card("SFD-009", reviewed=True, keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-009:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('R',), target_scope="unit"),
    )
)

# SFD-011 取放自如
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   选择一名单位和其控制者的一件武装。为该单位贴附或卸除该武装。抽一张牌。
card("SFD-011", keywords={Keyword.REACTION})

# SFD-013 爆破队学员
#   你可以选择支付{{1}}和{{红色}}，作为打出我的额外费用。
#   当你打出我时，如果你支付了该额外费用，则对战场上的一名单位造成2点伤害。
card("SFD-013", abilities=(
    AbilityDef(ability_id="SFD-013:extra_cost:0", kind="extra_cost", timing="passive", immediate=False, rules_ref=("R-CR-356.2",), cost_symbols=("1", "R",)),
))

# SFD-016 反曲之弓
#   {{装配红色}}（支付{{红色}}：将此牌贴附到你控制的一名单位上。）
#   [EN 补段] When I attack or defend, deal 2 to an enemy unit here.
#   （当我进攻或防守时，对此处的一名敌方单位造成 2 点伤害。me=宿主→719.1）
card("SFD-016", reviewed=True, keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-016:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('R',), target_scope="unit"),
        AbilityDef(ability_id="SFD-016:trigger:atkdef:0", kind="trigger", trigger="atk_defend",
                   payload="deal_enemy_here", value=2,
                   rules_ref=("R-CR-383.3", "R-CR-417.1", "R-CR-719.1")),
    )
)

# SFD-017 雷霆突降
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   对战场上的一名单位造成2点伤害。如果它是进攻方，则改为对其造成4点伤害。
card("SFD-017", keywords={Keyword.ACTION, Keyword.HIDDEN})

# SFD-021 铁甲先锋
#   {{绝念}}—打出两名3{{S}}的“机器人”到你的基地。（当我被摧毁后，发动此效果。）
card("SFD-021", keywords={Keyword.DEATHKNELL})

# SFD-022 长剑
#   {{灵便}}（此牌获得{{反应}}。当你打出此牌时,将它贴附到你控制的一名单位上。)
#   {{装配}}{{红色}}（支付{{红色}}：将此牌贴附到你控制的一名单位上。）
card("SFD-022", reviewed=True, keywords={Keyword.EQUIP, Keyword.QUICKDRAW},
    abilities=(
        AbilityDef(ability_id="SFD-022:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('R',), target_scope="unit"),
    )
)

# SFD-023 透体圣光
#   {{回响2红色}}（你可以选择支付此额外费用，以重复此法术效果。）
#   对战场上的一名单位造成2点伤害，然后对最多另一名单位造成2点伤害。
card("SFD-023", keywords={Keyword.REPEAT})

# SFD-024 芮尔
#   {{壁垒}}（我在战斗中首先承担伤害。）
#   当我进攻时，你可以选择打出一件法力费用不高于{{2}}的武装，无视其费用，然后将其贴附到我身上。
card("SFD-024", keywords={Keyword.TANK})

# SFD-025 雷恩加尔
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算，并能打出到你控制的战场。）
#   {{强攻2}}（如果我是进攻方，则{{S}}+2。）
#   我可以被打出到你正在进攻的战场。
card("SFD-025", keywords={Keyword.ASSAULT, Keyword.REACTION}, keyword_values={"assault": 2})

# SFD-025a 雷恩加尔
#   {{反应}}
#   {{强攻2}}
#   我可以被打出到你正在进攻的战场。
card("SFD-025a", keywords={Keyword.ASSAULT, Keyword.REACTION}, keyword_values={"assault": 2})

# SFD-028 卢锡安
#   {{强攻}}（如果我是进攻方，则{{S}}+1。）
#   当我进攻时，对此处的一名敌方单位造成等同于我{{强攻}}数值的伤害。
card("SFD-028", keywords={Keyword.ASSAULT})

# SFD-028a 卢锡安
#   {{强攻}}（如果我是进攻方，则{{S}}+1。）
#   当我进攻时，对此处的一名敌方单位造成等同于我{{强攻}}数值的伤害。
card("SFD-028a", keywords={Keyword.ASSAULT})

# SFD-029 雷克塞
#   {{急速}}（你可以选择额外支付{{1}}和{{红色}}，让我以活跃状态进场。）
#   {{强攻}}（如果我是进攻方，则{{S}}+1。）
#   从手牌以外位置被打出的友方单位获得{{急速}}。
card("SFD-029", keywords={Keyword.ACCELERATE, Keyword.ASSAULT})

# SFD-029a 雷克塞
#   {{急速}}（你可以选择额外支付{{1}}和{{红色}}，让我以活跃状态进场。）
#   {{强攻}}（如果我是进攻方，则{{S}}+1。）
#   从手牌以外位置被打出的友方单位获得{{急速}}。
card("SFD-029a", keywords={Keyword.ACCELERATE, Keyword.ASSAULT})

# SFD-030 阿瑞昂的陨落
#   {{装配1红色}}（支付{{1}}和{{红色}}：将此牌贴附到你控制的一名单位上。）
# 数据缺陷修复（bilingual 丢 effect_plain）暴露：卡体效果段未接线 → 降级回评
#   段（来自 EN）：据守效果与征服效果互换（效果改写，未接）
card("SFD-030", keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-030:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('1', 'R'), target_scope="unit"),
    )
)

# SFD-031 点沙成兵
#   {{回响2}}（你可以选择支付此额外费用，以重复此法术效果。）
#   打出一名2{{S}}的“黄沙士兵”。
card("SFD-031", keywords={Keyword.REPEAT})

# SFD-033 多兰之盾
#   {{装配绿色}}（支付{{绿色}}：将此牌贴附到你控制的一名单位上。）
card("SFD-033", reviewed=True, keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-033:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('G',), target_scope="unit"),
    )
)

# SFD-034 蛮荒之力
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   {{回响2}}（你可以选择支付此额外费用，以重复此法术效果。）
#   让一名单位在本回合内{{S}}+2。
# 手写（rq-2a）：spell_pump=+2；[回响2] 未接线（820）→ 暂不标 reviewed
card("SFD-034", keywords={Keyword.REACTION, Keyword.REPEAT}, abilities=(
    AbilityDef(ability_id="SFD-034:spell_pump:2", kind="spell_pump", timing="passive",
               immediate=False,
               rules_ref=("R-CR-157.1", "R-CR-355.6", "R-CR-317.2.c", "R-CR-474"),
               pump_value=2, target_scope="unit"),
))

# SFD-036 哀哀魄罗
#   {{绝念}} — 当我被摧毁时，如果此处没有其他友方单位，则抽一张牌。（当我被摧毁后，发动此效果。）
card("SFD-036", keywords={Keyword.DEATHKNELL})

# SFD-037 纳沃利侦察兵
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
card("SFD-037", reviewed=True, keywords={Keyword.DEFLECT})

# SFD-040 扑咚！
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   {{回响2}}（你可以选择支付此额外费用，以重复此法术效果。）
#   眩晕一名进攻方单位。（使其在本回合内无法造成战斗伤害。）
card("SFD-040", keywords={Keyword.ACTION, Keyword.REPEAT})

# SFD-042 残暴之力
#   {{装配绿色}}（支付{{绿色}}：将此牌贴附到你控制的一名单位上。）
# 数据缺陷修复（bilingual 丢 effect_plain）暴露：卡体效果段未接线 → 降级回评
#   段（来自 EN）：本回合贴附期间额外+2（条件持续效果，未接）
card("SFD-042", keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-042:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('G',), target_scope="unit"),
    )
)

# SFD-043 禁军之墙
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   将一处战场上任意数量的友方单位移动到其所属的基地。
card("SFD-043", keywords={Keyword.ACTION, Keyword.HIDDEN})

# SFD-045 极速反制
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   无效化一个将友方单位或友方装备选为目标的敌方法术或技能。
card("SFD-045", keywords={Keyword.REACTION})

# SFD-051 守护天使
#   {{装配绿色}}（支付{{绿色}}：将此牌贴附到你控制的一名单位上。）
# 数据缺陷修复（bilingual 丢 effect_plain）暴露：卡体效果段未接线 → 降级回评
#   段（来自 EN）：免死改杀守护天使+治疗+休眠+召回（替换效果，未接）
card("SFD-051", keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-051:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('G',), target_scope="unit"),
    )
)

# SFD-053 迦娜
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算，并能打出到你控制的战场。）
#   当你打出我时，为你此处的所有单位移除伤害，然后将一名敌方单位从此处移动到其所属的基地。
card("SFD-053", keywords={Keyword.REACTION})

# SFD-054 贾克斯
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   你手牌中的每一件武装都获得{{灵便}}。（此牌获得{{反应}}。当你打出此牌时，将它贴附到你控制的一名单位上。）
card("SFD-054", keywords={Keyword.DEFLECT})

# SFD-054a 贾克斯
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   你手牌中的每一件武装都获得{{灵便}}。（此牌获得{{反应}}。当你打出此牌时，将它贴附到你控制的一名单位上。）
card("SFD-054a", keywords={Keyword.DEFLECT})

# SFD-055 超大型约德尔人
#   {{坚守5}}（如果我是防守方，则{{S}}+5。）
#   {{壁垒}}（我在战斗中首先承担伤害。）
#   在本回合内，你每通过据守获得1分，我的费用就减少{{2}}和{{绿色}}。
card("SFD-055", keywords={Keyword.SHIELD, Keyword.TANK}, keyword_values={"shield": 5})

# SFD-056 斯特拉克的挑战护手
#   {{灵便}}（此牌获得{{反应}}。当你打出此牌时，将它贴附到你控制的一名单位上。)
#   {{装配绿色}}（支付{{绿色}}：将此牌贴附到你控制的一名单位上。）
card("SFD-056", reviewed=True, keywords={Keyword.EQUIP, Keyword.QUICKDRAW},
    abilities=(
        AbilityDef(ability_id="SFD-056:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('G',), target_scope="unit"),
    )
)

# SFD-057 艾瑞莉娅
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   当你选择我为目标或让我变为活跃状态时，让我本回合内{{S}}+1。
card("SFD-057", keywords={Keyword.DEFLECT})

# SFD-057a 艾瑞莉娅
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   当你选择我为目标或让我变为活跃状态时，让我本回合内{{S}}+1。
card("SFD-057a", keywords={Keyword.DEFLECT})

# SFD-059 斯弗尔尚歌
#   {{装配}}{{1}}{{绿色}}（支付{{1}}和{{绿色}}：将此牌贴附到你控制的一名单位上。）
#   在此牌贴附于单位期间，复制该单位的技能描述到此武装的效果文字，在贴附期间持续生效。
# rq-1a 误标 reviewed 降级：卡面有未接线效果行（复制单位技能描述——文本拷贝机制，待 367 类基建）
card("SFD-059", keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-059:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('1', 'G'), target_scope="unit"),
    )
)

# SFD-060 缇亚娜·冕卫
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   如果我位于战场上，则对手无法得分。
card("SFD-060", keywords={Keyword.DEFLECT})

# SFD-064 布甲
#   {{灵便}}（此牌获得{{反应}}。当你打出此牌时，将它贴附到你控制的一名单位上。）
#   {{装配蓝色}}（支付{{蓝色}}：将此牌贴附到你控制的一名单位上。）
card("SFD-064", reviewed=True, keywords={Keyword.EQUIP, Keyword.QUICKDRAW},
    abilities=(
        AbilityDef(ability_id="SFD-064:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('B',), target_scope="unit"),
    )
)

# SFD-066 封冻
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   {{回响2}}（你可以选择支付此额外费用，以重复此法术效果。）
#   让一名单位在本回合内{{S}}-2。
# 手写（rq-2a）：spell_pump=-2（负向修正照加，无下限语不 clamp）；[回响2] 未接线 → 暂不标 reviewed
card("SFD-066", keywords={Keyword.REACTION, Keyword.REPEAT}, abilities=(
    AbilityDef(ability_id="SFD-066:spell_pump:2", kind="spell_pump", timing="passive",
               immediate=False,
               rules_ref=("R-CR-157.1", "R-CR-355.6", "R-CR-317.2.c", "R-CR-474"),
               pump_value=-2, target_scope="unit"),
))

# SFD-067 霜衣幼崽
#   你可以选择支付{{蓝色}}，作为打出我的额外费用。
#   当你打出我时，如果你支付了该额外费用，则让一名单位本回合内{{S}}-2。
card("SFD-067", abilities=(
    AbilityDef(ability_id="SFD-067:extra_cost:0", kind="extra_cost", timing="passive", immediate=False, rules_ref=("R-CR-356.2",), cost_symbols=("B",)),
))

# SFD-068 机械迷
#   {{急速}}（你可以选择额外支付{{1}}和{{蓝色}}，让我以活跃状态进场。）
#   贴附在我身上的每件武装提供双倍基础战力加成。
card("SFD-068", keywords={Keyword.ACCELERATE})

# SFD-070 痛苦之酬
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   对战场上的一名单位造成3点伤害。打出一个休眠的“金币”装备指示物。
card("SFD-070", keywords={Keyword.ACTION, Keyword.HIDDEN})

# SFD-073 海克斯注力刚壁
#   {{装配蓝色}}（支付{{蓝色}}：将此牌贴附到你控制的一名单位上。）
card("SFD-073", reviewed=True, keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-073:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('B',), target_scope="unit"),
    )
)

# SFD-076 产量激增
#   如果你控制着“机械”属性单位，则此牌的费用减少{{2}}。
#   打出一名3{{S}}的“机器人”到你的基地。
#   抽一张牌。
card("SFD-076", abilities=(
    AbilityDef(ability_id="SFD-076:spell_draw:0", kind="spell_draw", timing="passive", immediate=False, rules_ref=("R-CR-413.1",), draw_count=1),
))

# SFD-077 火箭轰击
#   {{回响4蓝色}}（你可以选择支付此额外费用，以重复此法术效果，并做出不同的选择。）
#   选择一个效果 — 
#   -对基地中的一名单位造成4点伤害。
#   -摧毁一件装备。
card("SFD-077", keywords={Keyword.REPEAT})

# SFD-080 风箱炎息
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   {{回响1蓝色}}（你可以选择支付此额外费用，以重复此法术效果。）
#   对同一位置的最多三名单位各造成1点伤害。
card("SFD-080", keywords={Keyword.ACTION, Keyword.REPEAT})

# SFD-082 伊泽瑞尔
#   当我进攻或防守时，对此处的一名敌方单位造成等同于我战力的伤害。
#   我无法造成战斗伤害。
#   支付{{蓝色}}：{{迅捷}} — 将我移动到你的基地。
card("SFD-082", abilities=(
    AbilityDef(ability_id="SFD-082:no_combat_damage:0", kind="no_combat_damage", timing="passive", immediate=False, rules_ref=("R-CR-465.2",)),
))

# SFD-082a 伊泽瑞尔
#   当我进攻或防守时，对此处的一名敌方单位造成等同于我战力的伤害。
#   我无法造成战斗伤害。
#   支付{{蓝色}}：{{迅捷}} — 将我移动到你的基地。
card("SFD-082a", abilities=(
    AbilityDef(ability_id="SFD-082a:no_combat_damage:0", kind="no_combat_damage", timing="passive", immediate=False, rules_ref=("R-CR-465.2",)),
))

# SFD-082b 伊泽瑞尔
#   当我进攻或防守时，对此处的一名敌方单位造成等同于我战力的伤害。
#   我无法造成战斗伤害。
#   支付{{蓝色}}：{{迅捷}} — 将我移动到你的基地。
card("SFD-082b", abilities=(
    AbilityDef(ability_id="SFD-082b:no_combat_damage:0", kind="no_combat_damage", timing="passive", immediate=False, rules_ref=("R-CR-465.2",)),
))

# SFD-085 奥恩
#   {{法盾2}}（对手必须支付{{A}}{{A}}才能将我选作法术或技能的目标。）
#   {{百炼}}（当你打出我时，你可以选择为我{{装配}}你的一件武装，其装配费用减少{{A}}。可选择已贴附的武装。）
#   每有一件友方装备，我便获得{{S}}+1。
card("SFD-085", keywords={Keyword.DEFLECT, Keyword.WEAPONMASTER}, keyword_values={"deflect": 2})

# SFD-085a 奥恩
#   {{法盾2}}（对手必须支付{{A}}{{A}}才能将我选作法术或技能的目标。）
#   {{百炼}}（当你打出我时，你可以选择为我{{装配}}你的一件武装，其装配费用减少{{A}}。可选择已贴附的武装。）
#   每有一件友方装备，我便获得{{S}}+1。
card("SFD-085a", keywords={Keyword.DEFLECT, Keyword.WEAPONMASTER}, keyword_values={"deflect": 2})

# SFD-086 云游图鉴
#   {{装配蓝色}}（支付{{蓝色}}：将此牌贴附到你控制的一名单位上。）
# 数据缺陷修复（bilingual 丢 effect_plain）暴露：卡体效果段未接线 → 降级回评
#   段（来自 EN）：据守时打出2个金币装备token（触发+token，未接）
card("SFD-086", keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-086:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('B',), target_scope="unit"),
    )
)

# SFD-087 先知之兆
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   抽三张牌。
# 手写（rq-2a）：spell_draw=3（中文数字「三」）
card("SFD-087", keywords={Keyword.REACTION}, reviewed=True, abilities=(
    AbilityDef(ability_id="SFD-087:spell_draw:1", kind="spell_draw", timing="passive",
               immediate=False, rules_ref=("R-CR-157.1", "R-CR-413.1"), draw_count=3),
))

# SFD-090 Z型驱动
#   {{装配1蓝色}}（支付{{1}}和{{蓝色}}：将此牌贴附到你控制的一名单位上。）
#   支付{{3}}和{{蓝色}}，放逐此牌：打出所有因此牌效果被放逐的单位，无视费用。（只有在未贴附时才能使用。）
# rq-1a 误标 reviewed 降级：放逐联动效果行未接线（放逐-撤回复合机制，待远征/放逐效果基建）
card("SFD-090", keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-090:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('1', 'B'), target_scope="unit"),
    )
)

# SFD-092 战斗厨神
#   {{百炼}}（当你打出我时，你可以选择为我{{装配}}你的一件武装，其装配费用减少{{A}}。可选择已贴附的武装。）
card("SFD-092", keywords={Keyword.WEAPONMASTER})

# SFD-095 多兰之刃
#   {{装配橙色}}（支付{{橙色}}：将此牌贴附到你控制的一名单位上。）
card("SFD-095", reviewed=True, keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-095:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('O',), target_scope="unit"),
    )
)

# SFD-096 劳伦特护刃者
#   {{游走}} （我可以向其他战场进行移动。）
card("SFD-096", reviewed=True, keywords={Keyword.GANKING})

# SFD-097 先打再问
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   让一名单位在本回合内{{S}}+5。
# 手写（fx-4）：spell_pump=+5 @任一单位（474 加减层；317.2.c 回合结束失效）
card("SFD-097", keywords={Keyword.ACTION}, reviewed=True, abilities=(
    AbilityDef(ability_id="SFD-097:spell_pump:0", kind="spell_pump", timing="passive",
               immediate=False,
               rules_ref=("R-CR-157.1", "R-CR-355.6", "R-CR-317.2.c", "R-CR-474"),
               pump_value=5, target_scope="unit"),
))

# SFD-098 船猿
#   你可以选择支付{{1}}，作为打出我的额外费用。
#   当你打出我时，如果你支付了该额外费用，则给予我增益。（如果我未拥有增益，则获得一个{{S}}+1增益。）
card("SFD-098", abilities=(
    AbilityDef(ability_id="SFD-098:extra_cost:0", kind="extra_cost", timing="passive", immediate=False, rules_ref=("R-CR-356.2",), cost_symbols=("1",)),
))

# SFD-099 壮壮魄罗
#   {{百炼}}（当你打出我时，你可以选择为我{{装配}}你的一件武装，其装配费用减少{{A}}。可选择已贴附的武装。）
card("SFD-099", keywords={Keyword.WEAPONMASTER})

# SFD-102 海克斯饮魔刀
#   {{装配橙色}}（支付{{橙色}}：将此牌贴附到你控制的一名单位上。）
card("SFD-102", reviewed=True, keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-102:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('O',), target_scope="unit"),
    )
)

# SFD-103 琢珥鱼
#   {{急速}}（你可以选择额外支付{{1}}和{{橙色}}，让我以活跃状态进场。）
#   你每控制一名{{强力}}单位，我的费用便减少{{2}}。（战力达到5或以上时，即为强力单位。）
card("SFD-103", keywords={Keyword.ACCELERATE})

# SFD-104 禁魔石丰碑
#   {{瞬息}}（在其控制者的下个回合开始阶段，结算得分之前将其摧毁。）
#   友方单位获得{{法盾}}（对手必须支付{{A}}才能将其选作法术或技能的目标。）
card("SFD-104", keywords={Keyword.TEMPORARY})

# SFD-106 实力至上
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   你每控制一名{{强力}}单位，就抽一张牌。（战力达到5或以上时，即为强力单位。）
card("SFD-106", keywords={Keyword.REACTION})

# SFD-108 狂徒铠甲
#   {{装配橙色}}（支付{{橙色}}：将此牌贴附到你控制的一名单位上。）
# 数据缺陷修复（bilingual 丢 effect_plain）暴露：卡体效果段未接线 → 降级回评
#   段（来自 EN）：征服时buff me（触发+增益700，未接）
card("SFD-108", keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-108:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('O',), target_scope="unit"),
    )
)

# SFD-109 阿克尚
#   {{百炼}}
#   你可以选择支付{{橙色}}{{橙色}}，作为打出我的额外费用。
#   当你打出我时，如果你支付了该额外费用，则可以将一件敌方装备移动到你的基地。你控制这件装备，直到我离场为止。如果它是一件武装，则将其贴附到我身上。
card("SFD-109", keywords={Keyword.WEAPONMASTER}, abilities=(
    AbilityDef(ability_id="SFD-109:extra_cost:0", kind="extra_cost", timing="passive", immediate=False, rules_ref=("R-CR-356.2",), cost_symbols=("O", "O",)),
))

# SFD-111 前来相助
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   你可以选择将一名单位从手牌打出到你控制的一处战场，其费用减少{{3}}。
card("SFD-111", keywords={Keyword.ACTION, Keyword.HIDDEN})

# SFD-112 巨腕加藤
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   当我移动到一处战场时，让一名友方单位在本回合内获得我的关键词和等同于我战力的+{{S}}加成。
card("SFD-112", keywords={Keyword.DEFLECT})

# SFD-113 卢锡安
#   {{百炼}}（当你打出我时，你可以选择为我{{装配}}你的一件武装，其装配费用减少{{A}}。可选择已贴附的武装。）
#   每回合首次，当我征服一处战场时，让我变为活跃状态。
card("SFD-113", keywords={Keyword.WEAPONMASTER})

# SFD-113a 卢锡安
#   {{百炼}}（当你打出我时，你可以选择为我{{装配}}你的一件武装，其装配费用减少{{A}}。可选择已贴附的武装。）
#   每回合首次，当我征服一处战场时，让我变为活跃状态。
card("SFD-113a", keywords={Keyword.WEAPONMASTER})

# SFD-114 行军号令
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   {{回响3}}（你可以选择支付此额外费用，以重复此法术效果。）
#   选择任意一名友方单位，和战场上的一名敌方单位。让这两名单位相互以自身战力给对方造成伤害。
card("SFD-114", keywords={Keyword.ACTION, Keyword.REPEAT})

# SFD-115 三相之力
#   {{装配橙色}}（支付{{橙色}}：将此牌贴附到你控制的一名单位上。）
#   [EN 补段] When I hold, score 1 point.（当我据守时，你获得 1 分。）
card("SFD-115", reviewed=True, keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-115:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('O',), target_scope="unit"),
        AbilityDef(ability_id="SFD-115:trigger:hold:0", kind="trigger", trigger="hold",
                   payload="score", value=1,
                   rules_ref=("R-CR-383.3", "R-CR-469.2")),
    )
)

# SFD-116 永恩
#   {{百炼}}（当你打出我时，你可以选择为我{{装配}}你的一件武装，其装配费用减少{{A}}。可选择已贴附的武装。）
#   当我征服一处开放的战场时，对基地中的一名敌方单位造成等同于我战力的伤害。
card("SFD-116", keywords={Keyword.WEAPONMASTER})

# SFD-118 碎骨棒
#   {{装配1橙色}}（支付{{1}}和{{橙色}}：将此牌贴附到你控制的一名单位上。）
#   [EN 补段] When I conquer, channel 1 rune exhausted.（当我征服时，召出 1 枚休眠的符文。）
card("SFD-118", reviewed=True, keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-118:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('1', 'O'), target_scope="unit"),
        AbilityDef(ability_id="SFD-118:trigger:conquer:0", kind="trigger", trigger="conquer",
                   payload="channel", value=1,
                   rules_ref=("R-CR-383.3", "R-CR-430.2", "R-CR-430.5")),
    )
)

# SFD-118a 碎骨棒
#   {{装配1橙色}}（支付{{1}}和{{橙色}}：将此牌贴附到你控制的一名单位上。）
card("SFD-118a", reviewed=True, keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-118a:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('1', 'O'), target_scope="unit"),
    )
)

# SFD-119 贾克斯
#   {{百炼}}（当你打出我时，你可以选择为我{{装配}}你的一件武装，其装配费用减少{{A}}。可选择已贴附的武装。）
#   当你为我贴附武装时，可以选择支付{{1}}，以此抽一张牌。
card("SFD-119", keywords={Keyword.WEAPONMASTER})

# SFD-119a 贾克斯
#   {{百炼}}（当你打出我时，你可以选择为我{{装配}}你的一件武装，其装配费用减少{{A}}。可选择已贴附的武装。）
#   当你为我贴附武装时，可以选择支付{{1}}，以此抽一张牌。
card("SFD-119a", keywords={Keyword.WEAPONMASTER})

# SFD-120 希维尔
#   {{法盾2}}（对手必须支付{{A}}{{A}}才能将我选作法术或技能的目标。）
#   当我通过进攻征服一处战场时，如果你给敌方单位造成了不低于5点的过量伤害，则你可以选择对一名敌方单位造成等同于该过量伤害的伤害。
card("SFD-120", keywords={Keyword.DEFLECT}, keyword_values={"deflect": 2})

# SFD-120a 希维尔
#   {{法盾2}}（对手必须支付{{A}}{{A}}才能将我选作法术或技能的目标。）
#   当我通过进攻征服一处战场时，如果你给敌方单位造成了不低于5点的过量伤害，则你可以选择对一名敌方单位造成等同于该过量伤害的伤害。
card("SFD-120a", keywords={Keyword.DEFLECT}, keyword_values={"deflect": 2})

# SFD-122 预判攻势
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   {{回响紫色}}（你可以选择支付此额外费用，以重复此法术效果。）
#   查看你主牌堆顶部的两张牌。抽取其中一张，然后回收另一张卡牌。
card("SFD-122", keywords={Keyword.ACTION, Keyword.REPEAT})

# SFD-124 多兰之戒
#   {{装配紫色}}（支付{{紫色}}：将此牌贴附到你控制的一名单位上。）
#   [EN 补段] When I conquer, discard 1, then draw 1.（当我征服时，弃置 1 张手牌，然后抽 1 张。）
card("SFD-124", reviewed=True, keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-124:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('P',), target_scope="unit"),
        AbilityDef(ability_id="SFD-124:trigger:conquer:0", kind="trigger", trigger="conquer",
                   payload="discard_draw", value=1,
                   rules_ref=("R-CR-383.3", "R-CR-422.1", "R-CR-413.1")),
    )
)

# SFD-127 炳文大师
#   {{百炼}}（当你打出我时，你可以选择为我{{装配}}你的一件武装，其装配费用减少{{A}}。可选择已贴附的武装。）
card("SFD-127", keywords={Keyword.WEAPONMASTER})

# SFD-129 诱饵
#   {{回响2}}（你可以选择支付此额外费用，以重复此法术效果。）
#   将一名敌方单位移动到其控制者的其他单位所在的一处位置。
card("SFD-129", keywords={Keyword.REPEAT})

# SFD-131 远古战狂
#   {{急速}}（你可以选择额外支付{{1}}和{{紫色}}，让我以活跃状态进场。）
#   我拥有等同于此处敌方单位数量的{{强攻}}数值。（如果我是进攻方，则每点强攻提供{{S}}+1。）
card("SFD-131", keywords={Keyword.ACCELERATE})

# SFD-133 轻灵之靴
#   {{装配紫色}}（支付{{紫色}}：将此牌贴附到你控制的一名单位上。）
card("SFD-133", reviewed=True, keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-133:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('P',), target_scope="unit"),
    )
)

# SFD-134 萃取
#   {{装配紫色}}（支付{{紫色}}：将此牌贴附到你控制的一名单位上。）
# 数据缺陷修复（bilingual 丢 effect_plain）暴露：卡体效果段未接线 → 降级回评
#   段（来自 EN）：征服时打金币token（触发+token，未接）
card("SFD-134", keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-134:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('P',), target_scope="unit"),
    )
)

# SFD-135 紧急召回
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   让一件装备返回其所属的手牌。
card("SFD-135", keywords={Keyword.ACTION})

# SFD-136 强买强卖
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   {{回响2}}（你可以选择支付此额外费用，以重复此法术效果。）
#   选择一个法术，除非其控制者选择支付{{2}}，否则无效化该法术。
card("SFD-136", keywords={Keyword.REACTION, Keyword.REPEAT})

# SFD-138 吟风翼
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   当你打出我时，你可以选择让战场上另一名不高于3{{S}}的单位返回其所属的手牌。
card("SFD-138", keywords={Keyword.HIDDEN})

# SFD-139 夜之锋刃
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   当你从正面朝下状态中打出此牌时，将此牌贴附到此处你控制的一名单位上。
#   {{装配紫色}}（支付{{紫色}}：将此牌贴附到你控制的一名单位上。）
# rq-1a 误标 reviewed 降级：「从正面朝下打出时触发贴附」未接线（待命打出触发时点，待 383 触发基建）
card("SFD-139", keywords={Keyword.EQUIP, Keyword.HIDDEN},
    abilities=(
        AbilityDef(ability_id="SFD-139:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('P',), target_scope="unit"),
    )
)

# SFD-143 希维尔
#   {{急速}}（你可以选择额外支付{{1}}和{{紫色}}，让我以活跃状态进场。）
#   在本回合内，如果你至少支付了{{A}}{{A}}，则我获得{{S}}+2和{{游走}}。（我可以向其他战场进行移动。）
card("SFD-143", keywords={Keyword.ACCELERATE})

# SFD-143a 希维尔
#   {{急速}}（你可以选择额外支付{{1}}和{{紫色}}，让我以活跃状态进场。）
#   在本回合内，如果你至少支付了{{A}}{{A}}，则我获得{{S}}+2和{{游走}}。（我可以向其他战场进行移动。）
card("SFD-143a", keywords={Keyword.ACCELERATE})

# SFD-145 换换乐
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   让同一处战场上的两名单位在本回合内战力互换。
card("SFD-145", keywords={Keyword.ACTION, Keyword.HIDDEN})

# SFD-148 德莱文
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   每回合首次，当我赢得战斗时，你获得1分。
#   当我在战斗中被摧毁时，选择一名对手，让其获得1分。"
card("SFD-148", keywords={Keyword.DEFLECT})

# SFD-148a 德莱文
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   每回合首次，当我赢得战斗时，你获得1分。
#   当我在战斗中被摧毁时，选择一名对手，让其获得1分。"
card("SFD-148a", keywords={Keyword.DEFLECT})

# SFD-151 力量之缚
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   {{回响2}}（你可以选择支付此额外费用，以重复此法术效果。）
#   让两名友方单位在本回合内{{S}}+1。
card("SFD-151", keywords={Keyword.REACTION, Keyword.REPEAT})

# SFD-153 先锋之眼
#   {{装配黄色}}（支付{{黄色}}：将此牌贴附到你控制的一名单位上。）
# 数据缺陷修复（bilingual 丢 effect_plain）暴露：卡体效果段未接线 → 降级回评
#   段（来自 EN）：移动时打 1might 招募兵token（触发+token，未接）
card("SFD-153", keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-153:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('Y',), target_scope="unit"),
    )
)

# SFD-154 护驾！
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   打出一名2{{S}}的“黄沙士兵”。你可以选择支付{{黄色}}，以此让其变为活跃状态。
card("SFD-154", keywords={Keyword.HIDDEN})

# SFD-155 诚实掮客
#   {{绝念}} — 打出一个休眠的“金币”装备指示物。（当我被摧毁后，发动此效果。）
card("SFD-155", keywords={Keyword.DEATHKNELL})

# SFD-156 劳伦特剑使
#   {{强攻2}}（如果我是进攻方，则{{S}}+2。）
card("SFD-156", reviewed=True, keywords={Keyword.ASSAULT}, keyword_values={"assault": 2})

# SFD-161 暴风大剑
#   {{装配黄色}}（支付{{黄色}}：将此牌贴附到你控制的一名单位上。）
card("SFD-161", reviewed=True, keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-161:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('Y',), target_scope="unit"),
    )
)

# SFD-162 血钱
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   摧毁战场上一名不高于2{{S}}的单位。如果是敌方单位，则打出一个休眠的“金币”装备指示物。如果是友方单位，则打出两个休眠的“金币”装备指示物。
card("SFD-162", keywords={Keyword.ACTION})

# SFD-163 断魂一扼
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   摧毁一名友方单位，让另一名友方单位在本回合内获得等同于被摧毁单位战力的+{{S}}加成。抽一张牌。
card("SFD-163", keywords={Keyword.REACTION})

# SFD-164 流沙陷坑
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   如果你将我从手牌以外的位置打出，则我的费用减少{{2}}。
#   摧毁战场上的一名单位。
card("SFD-164", keywords={Keyword.ACTION})

# SFD-165 戈拉斯克调酒师
#   {{绝念}} — 你可以选择从你的废牌堆中打出一名费用不高于{{3}}且不高于{{A}}的单位，无视其费用。（当我被摧毁后，发动此效果。）
card("SFD-165", keywords={Keyword.DEATHKNELL})

# SFD-166 集结部队
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   在本回合内，每当一名友方单位被打出时，给予其增益。（如果该单位未拥有增益，则获得一个{{S}}+1增益。）
#   抽一张牌。
card("SFD-166", keywords={Keyword.ACTION}, abilities=(
    AbilityDef(ability_id="SFD-166:spell_draw:0", kind="spell_draw", timing="passive", immediate=False, rules_ref=("R-CR-413.1",), draw_count=1),
))

# SFD-167 无名英雄
#   {{绝念}} — 如果我为{{强力}}单位，则抽两张牌。（当我被摧毁后，发动此效果。战力达到5或以上时，即为强力单位。）
card("SFD-167", keywords={Keyword.DEATHKNELL})

# SFD-172 神圣剪刀
#   {{装配黄色}}（支付{{黄色}}：将此牌贴附到你控制的一名单位上。）
# 数据缺陷修复（bilingual 丢 effect_plain）暴露：卡体效果段未接线 → 降级回评
#   段（来自 EN）：绝念（Deathknell）——绝念触发类，未接
card("SFD-172", keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="SFD-172:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('Y',), target_scope="unit"),
    )
)

# SFD-173 索拉卡
#   我在战斗中最后承担伤害。
#   如果你在此处控制的另一名单位被摧毁，且该单位的战力低于我，则改为移除其所受伤害，让其变为休眠状态，并将其召回。（把该单位送回基地，此行动不算作移动。）
card("SFD-173", abilities=(
    AbilityDef(ability_id="SFD-173:last_damage:0", kind="last_damage", timing="passive", immediate=False, rules_ref=("R-CR-465.2.c.2",)),
))

# SFD-176 赵信
#   {{壁垒}}（我在战斗中首先承担伤害。）
#   如果你的基地中有不少于两名其他单位，则我以活跃状态进场。
card("SFD-176", keywords={Keyword.TANK})

# SFD-177 阿兹尔
#   {{急速}}（你可以选择额外支付{{1}}和{{黄色}}，让我以活跃状态进场。）
#   当我进攻时，你可以选择将自己任意数量的指示物单位移动到此战场。
card("SFD-177", keywords={Keyword.ACCELERATE})

# SFD-177a 阿兹尔
#   {{急速}}（你可以选择额外支付{{1}}和{{黄色}}，让我以活跃状态进场。）
#   当我进攻时，你可以选择将自己任意数量的指示物单位移动到此战场。
card("SFD-177a", keywords={Keyword.ACCELERATE})

# SFD-179 卡银娜·薇蕊泽
#   {{急速}}（你可以选择额外支付{{1}}和{{黄色}}，让我以活跃状态进场。）
#   当我移动到一处战场时，在此处打出三名1{{S}}的“随从”。
card("SFD-179", keywords={Keyword.ACCELERATE})

# SFD-190 炉火斗篷
#   {{唯我}}（你的卡组中只能拥有一张同名的此牌。）
#   {{装配A}}（支付{{A}}：将此牌贴附到你控制的一名单位上。）
#   [EN 补段] When I attack or defend, deal 2 to all enemy units here.
#   （当我进攻或防守时，对此处的所有敌方单位造成 2 点伤害。me=宿主→719.1）
card("SFD-190", reviewed=True, keywords={Keyword.EQUIP, Keyword.UNIQUE},
    abilities=(
        AbilityDef(ability_id="SFD-190:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('A',), target_scope="unit"),
        AbilityDef(ability_id="SFD-190:trigger:atkdef:0", kind="trigger", trigger="atk_defend",
                   payload="deal_all_enemy_here", value=2,
                   rules_ref=("R-CR-383.3", "R-CR-417.1", "R-CR-719.1")),
    )
)

# SFD-222 暴怒之印
#   {{横置}}：{{反应}}—{{获得}}{{红色}}，用以支付符能费用。（获得费用资源的技能无法成为其他法术的反应目标。）
card("SFD-222", abilities=(
    AbilityDef(ability_id="SFD-222:gear_gain_resource:0", kind="gain_resource", timing="reaction", cost_exhaust_self=True, rules_ref=("R-CR-377.1", "R-CR-357.1.a", "R-CR-429.3", "R-CR-444.2.c",), grant_power_domain="R"),
))

# SFD-223 薇恩
#   {{强攻3}}（如果我是进攻方，则{{S}}+3。）
#   如果对手已控制任意战场，则我以活跃状态进场。每当我征服一处战场时，你可以选择支付{{1}}来让我返回所属的手牌。
card("SFD-223", keywords={Keyword.ASSAULT}, keyword_values={"assault": 3})

# SFD-223* 薇恩
#   {{强攻3}}（如果我是进攻方，则{{S}}+3。）
#   如果对手已控制任意战场，则我以活跃状态进场。每当我征服一处战场时，你可以选择支付{{1}}来让我返回所属的手牌。
card("SFD-223*", keywords={Keyword.ASSAULT}, keyword_values={"assault": 3})

# SFD-225 艾瑞莉娅
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   当你选择我为目标或让我变为活跃状态时，让我本回合内{{S}}+1。
card("SFD-225", keywords={Keyword.DEFLECT})

# SFD-225* 艾瑞莉娅
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   当你选择我为目标或让我变为活跃状态时，让我本回合内{{S}}+1。
card("SFD-225*", keywords={Keyword.DEFLECT})

# SFD-226 专注之印
#   {{横置}}：{{反应}}—{{获得}}{{绿色}}，用以支付符能费用。（获得费用资源的技能无法成为其他法术的反应目标。）
card("SFD-226", abilities=(
    AbilityDef(ability_id="SFD-226:gear_gain_resource:0", kind="gain_resource", timing="reaction", cost_exhaust_self=True, rules_ref=("R-CR-377.1", "R-CR-357.1.a", "R-CR-429.3", "R-CR-444.2.c",), grant_power_domain="G"),
))

# SFD-229 洞察之印
#   {{横置}}：{{反应}}—{{获得}}{{蓝色}}，用以支付符能费用。（获得费用资源的技能无法成为其他法术的反应目标。）
card("SFD-229", abilities=(
    AbilityDef(ability_id="SFD-229:gear_gain_resource:0", kind="gain_resource", timing="reaction", cost_exhaust_self=True, rules_ref=("R-CR-377.1", "R-CR-357.1.a", "R-CR-429.3", "R-CR-444.2.c",), grant_power_domain="B"),
))

# SFD-230 提莫
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   当我防守一处战场、或从正面朝下的{{待命}}状态中打出时，展示你主牌堆顶部的五张牌，当中每有一张带有{{待命}}技能的卡牌，就对此处的一名敌方单位造成1点伤害，然后将展示的牌回收。
card("SFD-230", keywords={Keyword.HIDDEN})

# SFD-230* 提莫
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   当我防守一处战场、或从正面朝下的{{待命}}状态中打出时，展示你主牌堆顶部的五张牌，当中每有一张带有{{待命}}技能的卡牌，就对此处的一名敌方单位造成1点伤害，然后将展示的牌回收。
card("SFD-230*", keywords={Keyword.HIDDEN})

# SFD-231 力量之印
#   {{横置}}：{{反应}}—{{获得}}{{橙色}}，用以支付符能费用。（获得费用资源的技能无法成为其他法术的反应目标。）
card("SFD-231", abilities=(
    AbilityDef(ability_id="SFD-231:gear_gain_resource:0", kind="gain_resource", timing="reaction", cost_exhaust_self=True, rules_ref=("R-CR-377.1", "R-CR-357.1.a", "R-CR-429.3", "R-CR-444.2.c",), grant_power_domain="O"),
))

# SFD-233 永恩
#   {{百炼}}（当你打出我时，你可以选择为我{{装配}}你的一件武装，其装配费用减少{{A}}。可选择已贴附的武装。）
#   当我征服一处开放的战场时，对基地中的一名敌方单位造成等同于我战力的伤害。
card("SFD-233", keywords={Keyword.WEAPONMASTER})

# SFD-233* 永恩
#   {{百炼}}（当你打出我时，你可以选择为我{{装配}}你的一件武装，其装配费用减少{{A}}。可选择已贴附的武装。）
#   当我征服一处开放的战场时，对基地中的一名敌方单位造成等同于我战力的伤害。
card("SFD-233*", keywords={Keyword.WEAPONMASTER})

# SFD-234 不和之印
#   {{横置}}：{{反应}}—{{获得}}{{紫色}}，用以支付符能费用。（获得费用资源的技能无法成为其他法术的反应目标。）
card("SFD-234", abilities=(
    AbilityDef(ability_id="SFD-234:gear_gain_resource:0", kind="gain_resource", timing="reaction", cost_exhaust_self=True, rules_ref=("R-CR-377.1", "R-CR-357.1.a", "R-CR-429.3", "R-CR-444.2.c",), grant_power_domain="P"),
))

# SFD-235 亚索
#   {{游走}}（我可以向其他战场进行移动。）
#   当我在一个回合内进行了第三次移动，你获得1分。
card("SFD-235", keywords={Keyword.GANKING})

# SFD-235* 亚索
#   {{游走}}（我可以向其他战场进行移动。）
#   当我在一个回合内进行了第三次移动，你获得1分。
card("SFD-235*", keywords={Keyword.GANKING})

# SFD-236 德莱厄斯
#   {{鼓舞}}—当你打出我时，让我变为活跃状态。（如果你在本回合内已打出过其他卡牌，则发动此效果。）
#   此处的其他友方单位获得{{S}}+1。
card("SFD-236", keywords={Keyword.LEGION})

# SFD-236* 德莱厄斯
#   {{鼓舞}}—当你打出我时，让我变为活跃状态。（如果你在本回合内已打出过其他卡牌，则发动此效果。）
#   此处的其他友方单位获得{{S}}+1。
card("SFD-236*", keywords={Keyword.LEGION})

# SFD-237 卡尔玛
#   {{预知}}（当你打出我时，查看主牌堆顶部的一张牌，你可以选择将其回收。）
#   每当你回收任意数量的卡牌时，给予一名友方单位增益。（如果该单位未拥有增益，则获得一个{{S}}+1增益。符文不被视为卡牌。）
card("SFD-237", keywords={Keyword.VISION})

# SFD-237* 卡尔玛
#   {{预知}}（当你打出我时，查看主牌堆顶部的一张牌，你可以选择将其回收。）
#   每当你回收任意数量的卡牌时，给予一名友方单位增益。（如果该单位未拥有增益，则获得一个{{S}}+1增益。符文不被视为卡牌。）
card("SFD-237*", keywords={Keyword.VISION})

# SFD-238 团结之印
#   {{横置}}：{{反应}}—{{获得}}{{黄色}}，用以支付符能费用。（获得费用资源的技能无法成为其他法术的反应目标。）
card("SFD-238", abilities=(
    AbilityDef(ability_id="SFD-238:gear_gain_resource:0", kind="gain_resource", timing="reaction", cost_exhaust_self=True, rules_ref=("R-CR-377.1", "R-CR-357.1.a", "R-CR-429.3", "R-CR-444.2.c",), grant_power_domain="Y"),
))

# SFD-239 索拉卡
#   我在战斗中最后承担伤害。
#   如果你在此处控制的另一名单位被摧毁，且该单位的战力低于我，则改为移除其所受伤害，让其变为休眠状态，并将其召回。（把该单位送回基地，此行动不算作移动。）
card("SFD-239", abilities=(
    AbilityDef(ability_id="SFD-239:last_damage:0", kind="last_damage", timing="passive", immediate=False, rules_ref=("R-CR-465.2.c.2",)),
))

# SFD-239* 索拉卡
#   我在战斗中最后承担伤害。
#   如果你在此处控制的另一名单位被摧毁，且该单位的战力低于我，则改为移除其所受伤害，让其变为休眠状态，并将其召回。（把该单位送回基地，此行动不算作移动。）
card("SFD-239*", abilities=(
    AbilityDef(ability_id="SFD-239*:last_damage:0", kind="last_damage", timing="passive", immediate=False, rules_ref=("R-CR-465.2.c.2",)),
))

