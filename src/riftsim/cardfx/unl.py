# 自动生成草稿（scripts/cards/gen_cardfx_from_defs.py）；人工 review 后为事实源。
# CN 原文注释为权威面；rules_ref 锚点随 AbilityDef 携带。
from ..cards import AbilityDef
from ..enums import Keyword
from . import card


# UNL-001 竞技场理事
#   我以活跃状态进场。
#   {{横置}}：让一名单位在本回合内{{S}}+3。
card("UNL-001", abilities=(
    AbilityDef(ability_id="UNL-001:enters_ready:0", kind="enters_ready", timing="passive", immediate=False, rules_ref=("R-CR-369.3", "R-CR-359.2.c",)),
))

# UNL-002 伊焚娜
#   {{伏击}}（你可以选择将我作为{{反应}}牌，打出到有己方单位的战场。）
#   {{强攻2}}（如果我是进攻方，则{{S}}+2。）
card("UNL-002", reviewed=True, keywords={Keyword.AMBUSH, Keyword.ASSAULT}, keyword_values={"assault": 2})

# UNL-003 鲛人滋事者
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   当你将我打出到一处战场时，对此处的一名敌方单位造成2点伤害。
card("UNL-003", keywords={Keyword.HIDDEN})

# UNL-005 传承者雷芙纳
#   {{游走}}（我可以向其他战场进行移动。）
#   当你打出一个法术时，如果消耗了不低于{{4}}法力，则让我变为活跃状态。
card("UNL-005", keywords={Keyword.GANKING})

# UNL-006 小鲨鱼
#   {{急速}}（你可以选择额外支付{{1}}和{{红色}}，让我以活跃状态进场。）
#   {{强攻4}}（如果我是进攻方，则{{S}}+4。）
card("UNL-006", reviewed=True, keywords={Keyword.ACCELERATE, Keyword.ASSAULT}, keyword_values={"assault": 4})

# UNL-007 惩戒
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   对战场上的一名单位造成3点伤害。如果该单位在本回合内被摧毁，则改为将其放逐。
card("UNL-007", keywords={Keyword.ACTION})

# UNL-008 莽林巨象
#   {{强攻}}（如果我是进攻方，则{{S}}+1。）
#   如果本回合内有单位被摧毁，则我以活跃状态进场。
card("UNL-008", keywords={Keyword.ASSAULT})

# UNL-009 大幕渐起
#   {{回响}}{{2}}（你可以选择支付此额外费用，以重复此法术效果。）让一名单位变为活跃状态。
card("UNL-009", keywords={Keyword.REPEAT})

# UNL-010 强能冲拳
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   让一名单位本回合内获得{{强攻2}}和{{游走}}。（如果它是进攻方，则{{S}}+2。它可以向其它战场进行移动。）
card("UNL-010", keywords={Keyword.ACTION})

# UNL-012 布罗梅因领主
#   {{伏击}}（你可以选择将我作为{{反应}}牌，打出到有己方单位的战场。）
#   当你打出我时，让你此处的其他单位本回合内获得{{强攻}}。（如果他们是进攻方，则{{S}}+1。）
card("UNL-012", keywords={Keyword.AMBUSH})

# UNL-013 莲花陷阱
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   选择一名单位。本回合该单位受到的所有伤害翻倍。
card("UNL-013", keywords={Keyword.HIDDEN, Keyword.REACTION})

# UNL-014 渊海狩咒
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   对战场上的一名单位造成2点伤害。如果你控制着一张正面朝下的卡牌，则改为对该单位造成4点伤害。
card("UNL-014", keywords={Keyword.ACTION})

# UNL-016 焰爪
#   {{狩猎2}}（当我征服或据守一处战场时，获得2经验。）
#   {{等级3>}} 我获得{{S}}+1，并以活跃状态进场。（如果你拥有不少于3经验，则获得该效果。）
card("UNL-016", keywords={Keyword.HUNT})

# UNL-019 枯萎战斧
#   {{装配}}{{1}}{{红色}}（支付{{1}}和{{红色}}：将此牌贴附到你控制的一名单位上。）
#   [EN 补段] At the end of your turn, if I didn't conquer this turn, unattach this and deal 4 to me.
#   （在你的回合结束时，如果我未在本回合内征服，将此牌卸除，并对我造成 4 点伤害。）
#   口径：「我」=宿主顶部卡（719.1 贴附卡文本添加；OPEN-7 据此 derived 收敛——docs/unresolved_rules.md）
card("UNL-019", reviewed=True, keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="UNL-019:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('1', 'R'), target_scope="unit"),
        AbilityDef(ability_id="UNL-019:trigger:end:0", kind="trigger", trigger="end_of_turn_own",
                   payload="unattach_self_deal_host", value=4, condition="no_conquer_this_turn",
                   rules_ref=("R-CR-383.3", "R-CR-435.1", "R-CR-417.1", "R-CR-719.1")),
    )
)

# UNL-021 阴森药剂师
#   {{伏击}}（你可以选择将我作为{{反应}}牌，打出到有己方单位的战场。）
#   当你打出我时，你可以选择让一名战场上的友方单位返回其所属的手牌。
card("UNL-021", keywords={Keyword.AMBUSH})

# UNL-022 烬
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   {{游走}}（我可以向其他战场进行移动。）
#   当我移动时，{{获得}}{{1}}和{{A}}。（获得费用资源的技能无法成为其他法术的反应目标。）
card("UNL-022", keywords={Keyword.DEFLECT, Keyword.GANKING})

# UNL-022a 烬
#   {{法盾}}
#   {{游走}}
#   当我移动时，{{获得}}{{1}}和{{A}}。
card("UNL-022a", keywords={Keyword.DEFLECT, Keyword.GANKING})

# UNL-024 雷恩加尔
#   {{急速}}（你可以选择额外支付{{1}}和{{红色}}，让我以活跃状态进场。）
#   {{强攻2}}（如果我是进攻方，则{{S}}+2。）
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   {{游走}}（我可以向其他战场进行移动。）
card("UNL-024", reviewed=True, keywords={Keyword.ACCELERATE, Keyword.ASSAULT, Keyword.DEFLECT, Keyword.GANKING}, keyword_values={"assault": 2})

# UNL-024a 雷恩加尔
#   {{急速}}
#   {{强攻2}}
#   {{法盾}}
#   {{游走}}
card("UNL-024a", reviewed=True, keywords={Keyword.ACCELERATE, Keyword.ASSAULT, Keyword.DEFLECT, Keyword.GANKING}, keyword_values={"assault": 2})

# UNL-025 不死军团
#   {{鼓舞>}} 你可以选择支付{{3}}和{{红色}}，将我从废牌堆中打出。（如果你在本回合内已打出过其他卡牌，则发动此效果。）
card("UNL-025", keywords={Keyword.LEGION})

# UNL-028 派克
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{游走}}（我可以向其他战场进行移动。）
#   你可以选择支付{{红色}}，作为打出我的额外费用。
#   当你打出我时，如果你支付了该额外费用，则让我变为活跃状态，并让我本回合内{{S}}+2。
card("UNL-028", keywords={Keyword.GANKING, Keyword.HIDDEN}, abilities=(
    AbilityDef(ability_id="UNL-028:extra_cost:0", kind="extra_cost", timing="passive", immediate=False, rules_ref=("R-CR-356.2",), cost_symbols=("R",)),
))

# UNL-028a 派克
#   {{待命}}
#   {{游走}}
#   你可以选择支付{{红色}}，作为打出我的额外费用。
#   当你打出我时，如果你支付了该额外费用，则让我变为活跃状态，并让我本回合内{{S}}+2。
card("UNL-028a", keywords={Keyword.GANKING, Keyword.HIDDEN}, abilities=(
    AbilityDef(ability_id="UNL-028a:extra_cost:0", kind="extra_cost", timing="passive", immediate=False, rules_ref=("R-CR-356.2",), cost_symbols=("R",)),
))

# UNL-029 绯红印记树怪
#   {{急速}}（你可以选择额外支付{{1}}和{{红色}}，让我以活跃状态进场。）
#   你征服此处时的征服效果额外触发一次。
#   当我征服一处战场时，给予一名友方单位{{增益}}。（如果其未拥有增益，则获得一个{{S}}+1增益。）
card("UNL-029", keywords={Keyword.ACCELERATE})

# UNL-029a 绯红印记树怪
#   {{急速}}
#   你征服此处时的征服效果额外触发一次。
#   当我征服一处战场时，给予一名友方单位{{增益}}。
card("UNL-029a", keywords={Keyword.ACCELERATE})

# UNL-030 蔚
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   支付{{2}}和{{红色}}：让我本回合内战力翻倍。
card("UNL-030", keywords={Keyword.DEFLECT})

# UNL-030a 蔚
#   {{法盾}}
#   支付{{2}}和{{红色}}：让我本回合内战力翻倍。
card("UNL-030a", keywords={Keyword.DEFLECT})

# UNL-031 实战经验
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   让一名单位在本回合内{{S}}+1。
#   {{等级6>}} 改为让其本回合内{{S}}+3。（如果你拥有不少于6经验，则获得该效果。）
card("UNL-031", keywords={Keyword.REACTION})

# UNL-032 龙虎双雄
#   {{回响}}{{2}}（你可以选择支付此额外费用，以重复此法术效果。）
#   查看你主牌堆顶部的三张牌。你可以选择从中展示一名单位，并抽取该卡牌。回收其余的卡牌。
card("UNL-032", keywords={Keyword.REPEAT})

# UNL-034 暖春之使
#   {{狩猎}}（当我征服或据守一处战场时，获得1经验。）
#   当你打出我时，获得2经验。
card("UNL-034", keywords={Keyword.HUNT})

# UNL-036 变异猫咪
#   {{坚守2}}（如果我是防守方，则{{S}}+2。）
#   {{壁垒}}（我在战斗中首先承担伤害。）
card("UNL-036", reviewed=True, keywords={Keyword.SHIELD, Keyword.TANK}, keyword_values={"shield": 2})

# UNL-039 灵魂之剑
#   {{装配}}{{绿色}}（支付{{绿色}}：将此牌贴附到你控制的一名单位上。）
# 数据缺陷修复（bilingual 丢 effect_plain）暴露：卡体效果段未接线 → 降级回评
#   段（来自 EN）：[Level 3][>] 额外+1（等级关键词820，未接）
card("UNL-039", keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="UNL-039:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('G',), target_scope="unit"),
    )
)

# UNL-040 无极学徒
#   {{狩猎}}（当我征服或据守一处战场时，获得1经验。）
#   {{等级6>}} 当你打出我时，抽一张牌。（如果你拥有不少于6经验，则获得该效果。）
card("UNL-040", keywords={Keyword.HUNT})

# UNL-041 艾蕾，头号拥趸
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   如果我位于战场上，则你此处的其他单位获得{{法盾}}。
card("UNL-041", keywords={Keyword.DEFLECT})

# UNL-042 走开
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   {{眩晕}}一名单位。（使其在本回合内无法造成战斗伤害。）
#   如果你从手牌中打出此牌，则抽一张牌。
card("UNL-042", keywords={Keyword.ACTION, Keyword.HIDDEN})

# UNL-043 热情的播报员
#   {{后排}}（我在战斗中最后承担伤害。）
#   当我据守一处战场时，给予此处的所有单位{{增益}}。（未拥有增益的单位获得一个{{S}}+1增益。）
card("UNL-043", keywords={Keyword.BACKLINE})

# UNL-044 羽毛旋风
#   {{反应}}
#   从下列中选择一个 —
#   - 无效化一个法术。
#   - 打出四名1{{S}}的“战鹰”，它们拥有{{法盾}}。（对手必须支付{{A}}才能将其选作法术或技能的目标。）
card("UNL-044", keywords={Keyword.REACTION})

# UNL-046 动物之友
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   选择一名单位。你的单位中每有一种以下属性标签，则所选择的单位便在本回合内获得{{S}}+1 — “鸟类”、“猫科”、“犬形”、“魄罗”。
card("UNL-046", keywords={Keyword.REACTION})

# UNL-047 踏苔蜥
#   {{狩猎2}}（当我征服或据守一处战场时，获得2经验。）
#   {{等级3>}} 我获得{{S}}+1和{{法盾}}。（如果你拥有不少于3经验，则获得该效果。对手必须支付{{A}}才能将拥有{{法盾}}的目标选作法术或技能的目标。）
card("UNL-047", keywords={Keyword.HUNT})

# UNL-048 特雷弗·达顿尔
#   {{坚守}}（如果我是防守方，则{{S}}+1。）
#   当我据守一处战场时，在此处打出一名处于活跃状态的3{{S}}“精灵”，它拥有{{瞬息}}。（在其控制者的下个开始阶段开始时，结算得分之前将其摧毁。）
card("UNL-048", keywords={Keyword.SHIELD})

# UNL-049 蜜糖果实
#   此牌以休眠状态进场。
#   {{反应>}} {{横置}}：{{获得}}{{A}}。（获得费用资源的技能无法成为其他法术的反应目标。）
#   {{等级6>}} {{>>}}{{反应>}} {{横置}}：{{获得}} {{1}}和{{A}}。（你仅可在拥有不少于6经验时才能使用此技能。）
card("UNL-049", abilities=(
    AbilityDef(ability_id="UNL-049:enters_exhausted:0", kind="enters_exhausted", timing="passive", immediate=False, rules_ref=("R-CR-369.3", "R-CR-143.4", "R-CR-359.2.c",)),
))

# UNL-052 娜美
#   你可以选择支付{{绿色}}，作为打出我的额外费用。
#   当你打出我时，如果你支付了该额外费用，则{{眩晕}}一名敌方单位。（使其在本回合内无法造成战斗伤害。）
#   当我据守一处战场时，则你本回合下一次打出一名单位时，让其变为活跃状态，并给予其{{增益}}。
card("UNL-052", abilities=(
    AbilityDef(ability_id="UNL-052:extra_cost:0", kind="extra_cost", timing="passive", immediate=False, rules_ref=("R-CR-356.2",), cost_symbols=("G",)),
))

# UNL-053 迅捷蟹
#   （0{{S}}的单位可以进行征服和据守。）
#   当你打出我时，抽一张牌。
#   {{绝念>}} 选择一名对手。让其展示手牌。本回合内，你可以查看该对手正面朝下的卡牌。获得1经验。（当我被摧毁后，发动此效果。）
card("UNL-053", keywords={Keyword.DEATHKNELL}, abilities=(
    AbilityDef(ability_id="UNL-053:on_play_draw:0", kind="on_play_draw", timing="trigger", immediate=False, rules_ref=("R-CR-383.1", "R-CR-413.1",), draw_count=1),
))

# UNL-055 薇古丝
#   {{坚守}}（如果我是防守方，则{{S}}+1。）
#   {{壁垒}}（我在战斗中首先承担伤害。）
#   当你{{眩晕}}战场上的一名敌方单位时，你可以选择将我移动到该战场。
card("UNL-055", keywords={Keyword.SHIELD, Keyword.TANK})

# UNL-055a 薇古丝
#   {{坚守}}
#   {{壁垒}}
#   当你{{眩晕}}战场上的一名敌方单位时，你可以选择将我移动到该战场。
card("UNL-055a", keywords={Keyword.SHIELD, Keyword.TANK})

# UNL-057 野爪兽王
#   {{壁垒}}（我在战斗中首先承担伤害。）
#   你此处战力低于我的单位无法被敌方法术或技能选作目标。
card("UNL-057", keywords={Keyword.TANK})

# UNL-060 卑鄙之喉
#   {{伏击}}（你可以选择将我作为{{反应}}牌，打出到有己方单位的战场。）
#   此处战力低于我的敌方单位无法造成战斗伤害。
#   当我据守一处战场时，抽一张牌。
card("UNL-060", keywords={Keyword.AMBUSH})

# UNL-060a 卑鄙之喉
#   {{伏击}}
#   此处战力低于我的敌方单位无法在战斗中造成伤害。
#   当我据守一处战场时，抽一张牌。
card("UNL-060a", keywords={Keyword.AMBUSH})

# UNL-061 台前作秀
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   {{回响}}{{2}}（你可以选择支付此额外费用，以重复此法术效果。）
#   抽一张牌。
card("UNL-061", keywords={Keyword.REACTION, Keyword.REPEAT}, abilities=(
    AbilityDef(ability_id="UNL-061:spell_draw:0", kind="spell_draw", timing="passive", immediate=False, rules_ref=("R-CR-413.1",), draw_count=1),
))

# UNL-062 戏精远见家
#   {{绝念>}} {{洞察2}}。（当我被摧毁时，查看主牌堆顶部的两张牌。你可以将其中任意卡牌回收，并将其余的卡牌按任意顺序放回原处。）
card("UNL-062", keywords={Keyword.DEATHKNELL})

# UNL-063 月蚀
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   让一名单位在本回合内{{S}}-4。
#   进行{{洞察}}。（查看你主牌堆顶部的一张牌。你可以选择将其回收。）
card("UNL-063", keywords={Keyword.REACTION})

# UNL-066 月光之殇
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   让一名单位在本回合内{{S}}-10。
# 手写（rq-2a）：spell_pump=-10（负向修正照加，无下限语不 clamp）
card("UNL-066", keywords={Keyword.REACTION}, reviewed=True, abilities=(
    AbilityDef(ability_id="UNL-066:spell_pump:1", kind="spell_pump", timing="passive",
               immediate=False,
               rules_ref=("R-CR-157.1", "R-CR-355.6", "R-CR-317.2.c", "R-CR-474"),
               pump_value=-10, target_scope="unit"),
))

# UNL-067 破败大鲨炮
#   {{绝念>}} 对一名敌方单位造成4点伤害。（当我被摧毁后，发动此效果。）
card("UNL-067", keywords={Keyword.DEATHKNELL})

# UNL-071 环刃舞者
#   {{伏击}}（你可以选择将我作为{{反应}}牌，打出到有己方单位的战场。）
#   当你打出我时，让你此处的其他单位本回合内获得{{坚守}}。（如果他们是防守方，则{{S}}+1。）
card("UNL-071", keywords={Keyword.AMBUSH})

# UNL-072 新月打击
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   选择一处战场，以及该处的一名敌方单位。对该单位造成4点伤害，并对该处的其他敌方单位各造成1点伤害。
card("UNL-072", keywords={Keyword.ACTION})

# UNL-075 风行狐
#   {{狩猎2}}（当我征服或据守一处战场时，获得2经验。）
#   {{等级3>}} 我获得{{S}}+1和{{游走}}。（如果你拥有不少于3经验，则获得该效果。拥有{{游走}}的单位可以向其他战场进行移动。）
card("UNL-075", keywords={Keyword.HUNT})

# UNL-078 精灵提灯
#   {{瞬息}}（在其控制者的开始阶段开始时，结算得分之前将其摧毁。）
#   当你打出此牌时，打出一名活跃状态的3{{S}}“精灵”到你的基地，它拥有{{瞬息}}。
#   {{绝念>}} 重复此装备的打出效果。（当此牌被摧毁后，发动此效果。）
card("UNL-078", keywords={Keyword.DEATHKNELL, Keyword.TEMPORARY})

# UNL-081 赐面守侍
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{瞬息}}（在我控制者的开始阶段开始时，结算得分之前将我摧毁。）
#   当你打出我时，在此处打出两名“映像”。它们变为我的复制体。
card("UNL-081", keywords={Keyword.HIDDEN, Keyword.TEMPORARY})

# UNL-082 莉莉娅
#   {{急速}}（你可以选择额外支付{{1}}和{{蓝色}}，让我以活跃状态进场。）
#   当我移动时，在我移动的起点位置打出一名3{{S}}的“精灵”，它拥有{{瞬息}}。（在其控制者的开始阶段开始时，结算得分之前将其摧毁。）
card("UNL-082", keywords={Keyword.ACCELERATE})

# UNL-082a 莉莉娅
#   {{急速}}
#   当我移动时，在我移动的起点位置打出一名3{{S}}的“精灵”，它拥有{{瞬息}}。
card("UNL-082a", keywords={Keyword.ACCELERATE})

# UNL-083 镜中幻影
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   选择一名受你控制的单位和另一名与之位置不同的受你控制的单位。如果其中至少一个拥有{{瞬息}}，则将两名单位分别移动到对方的位置。抽一张牌。
card("UNL-083", keywords={Keyword.ACTION, Keyword.HIDDEN})

# UNL-085 地沟区地图
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   {{瞬息}}（在其控制者的开始阶段开始时，结算得分之前将其摧毁。）
#   当一名对手得分时，抽一张牌。
card("UNL-085", keywords={Keyword.REACTION, Keyword.TEMPORARY})

# UNL-087 苍蓝雕纹魔像
#   {{坚守2}}（如果我是防守方，则{{S}}+2。）
#   你据守此处时的据守效果额外触发一次。
#   当我据守一处战场时，你在下一个主阶段开始时{{获得}}{{A}}。（获得费用资源的技能无法成为其他法术的反应目标。）
card("UNL-087", keywords={Keyword.SHIELD}, keyword_values={"shield": 2})

# UNL-087a 苍蓝雕纹魔像
#   {{坚守2}}
#   你据守此处时的据守效果额外触发一次。
#   当我据守一处战场时，你在下一个主阶段开始时{{获得}}{{A}}。
card("UNL-087a", keywords={Keyword.SHIELD}, keyword_values={"shield": 2})

# UNL-089 烬
#   {{预知}}（当你打出我时，查看主牌堆顶部的一张牌，你可以选择将其回收。）
#   如果你在本回合消耗了不低于{{4}}的费用来打出一个法术，则你可以选择支付{{蓝色}}来将我打出。
card("UNL-089", keywords={Keyword.VISION})

# UNL-089a 烬
#   {{预知}}
#   如果你在本回合消耗了不低于{{4}}的费用来打出一个法术，则你可以选择支付{{蓝色}}来将我打出。
card("UNL-089a", keywords={Keyword.VISION})

# UNL-090 乐芙兰
#   {{后排}}（我在战斗中最后承担伤害。）
#   你在我所处战场的{{瞬息}}效果不会触发。
card("UNL-090", keywords={Keyword.BACKLINE})

# UNL-090a 乐芙兰
#   {{后排}}
#   你在我所处战场的{{瞬息}}效果不会触发。
card("UNL-090a", keywords={Keyword.BACKLINE})

# UNL-094 晶手猎人
#   {{狩猎}}（当我征服或据守一处战场时，获得1经验。）
#   {{等级6>}} 我获得{{S}}+1。（如果你拥有不少于6经验，则获得该效果。）
card("UNL-094", keywords={Keyword.HUNT})

# UNL-095 视死如归
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   让一名友方单位本回合内{{S}}+3。当该单位在本回合赢得一场战斗时，获得2经验。
card("UNL-095", keywords={Keyword.ACTION})

# UNL-096 猎人的宽刃刀
#   {{装配}}{{橙色}}（支付{{橙色}}：将此牌贴附到你控制的一名单位上。）
# 数据缺陷修复（bilingual 丢 effect_plain）暴露：卡体效果段未接线 → 降级回评
#   段（来自 EN）：狩猎（宿主）——狩猎812未接（关键词未接但 fx 未声明，属隐式漏标）
card("UNL-096", keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="UNL-096:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('O',), target_scope="unit"),
    )
)

# UNL-099 魁梧斗士
#   {{坚守2}}（如果我是防守方，则{{S}}+2。）
#   {{壁垒}}（我在战斗中首先承担伤害。）
card("UNL-099", reviewed=True, keywords={Keyword.SHIELD, Keyword.TANK}, keyword_values={"shield": 2})

# UNL-100 贪食魔沼蛙
#   {{狩猎3}}（当我征服或据守一处战场时，获得3经验。）
card("UNL-100", keywords={Keyword.HUNT})

# UNL-102 竞技场人气王
#   {{狩猎}}（当我征服或据守一处战场时，获得1点经验值。）
#   消耗2经验：给予我{{增益}}。（如果我未拥有增益，则获得一个{{S}}+1增益。）
card("UNL-102", keywords={Keyword.HUNT})

# UNL-103 处置命令
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   从下列中选择一个 —
#   — 从对手的废牌堆里总共选择最多三张牌。让其拥有者将其回收。
#   — 抽一张牌。
card("UNL-103", keywords={Keyword.REACTION})

# UNL-106 击退
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   选择战场上的一名友方单位。无效化一个以该单位为目标且不以其他友方单位为目标的敌方法术或技能。
card("UNL-106", keywords={Keyword.REACTION})

# UNL-113 易
#   {{狩猎2}}（当我征服或据守一处战场时，获得2经验。）
#   {{等级6>}} 我获得{{法盾}}和{{游走}}。（如果你拥有不少于6经验，对手必须支付{{A}}才能将我选作法术或技能的目标，且我可以向其他战场进行移动。）
card("UNL-113", keywords={Keyword.HUNT})

# UNL-113a 易
#   {{狩猎2}}
#   {{等级6>}} 我获得{{法盾}}和{{游走}}。
card("UNL-113a", keywords={Keyword.HUNT})

# UNL-114 奈德丽
#   {{伏击}}（你可以选择将我作为{{反应}}牌，打出到有己方单位的战场。）
#   当我赢得一场战斗时，抽一张牌。（如果我在战斗后仍然存活，则我赢得胜利。）
card("UNL-114", keywords={Keyword.AMBUSH})

# UNL-115 尼菈
#   {{急速}}（你可以选择额外支付{{1}}和{{橙色}}，让我以活跃状态进场。）
#   {{游走}}（我可以向其他战场进行移动。）
#   当我移动时，获得1经验。
card("UNL-115", keywords={Keyword.ACCELERATE, Keyword.GANKING})

# UNL-116 波比
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   当你打出我时，如果对手得分距离胜利得分不超过3分，则让我变为活跃状态，并获得3经验。
card("UNL-116", keywords={Keyword.DEFLECT})

# UNL-116a 波比
#   {{法盾}}
#   当你打出我时，如果对手得分距离胜利得分不超过3分，则让我变为活跃状态，并获得3经验。
card("UNL-116a", keywords={Keyword.DEFLECT})

# UNL-117 恐怖蛛怪
#   {{狩猎2}}（当我征服或据守一处战场时，获得2经验。）
#   如果一处战场上的敌方单位落单，则可以将我打出至该战场。
#   如果一处战场上的敌方单位落单，则可以将友方单位打出至该战场。
card("UNL-117", keywords={Keyword.HUNT})

# UNL-119 卡兹克
#   {{狩猎}}（当我征服或据守一处战场时，获得1经验。）
#   当我进攻时，你可以选择消耗3经验，以此对此处的一名敌方单位造成等同于我战力的伤害。
card("UNL-119", keywords={Keyword.HUNT})

# UNL-119a 卡兹克
#   {{狩猎}}
#   当我进攻时，你可以选择消耗3经验，以此对此处的一名敌方单位造成等同于我战力的伤害。
card("UNL-119a", keywords={Keyword.HUNT})

# UNL-120 雷恩加尔
#   {{伏击}}（你可以选择将我作为{{反应}}牌，打出到有己方单位的战场。）
#   我可以被打出至有敌方单位的战场（即使你在该处没有单位）。
card("UNL-120", keywords={Keyword.AMBUSH})

# UNL-120a 雷恩加尔
#   {{伏击}}
#   我可以被打出至有敌方单位的战场。
card("UNL-120a", keywords={Keyword.AMBUSH})

# UNL-125 月神恩赐
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   弃置一张手牌，然后抽两张牌。
card("UNL-125", keywords={Keyword.REACTION})

# UNL-127 树根先生
#   {{急速}}（你可以选择额外支付{{1}}和{{紫色}}，让我以活跃状态进场。）
#   当我移动至战场时，获得2经验。
card("UNL-127", keywords={Keyword.ACCELERATE})

# UNL-128 造化弄人
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   让一名友方单位和一名敌方单位返回其所属的手牌。
card("UNL-128", keywords={Keyword.REACTION})

# UNL-130 移动栖木
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   当你打出我时，选择一名对手。该玩家打出一名1{{S}}的“战鹰”，它拥有{{法盾}}。
card("UNL-130", keywords={Keyword.DEFLECT})

# UNL-131 遗弃
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   无效化一个法术。让其返回所属的手牌，而不是将其放入废牌堆。
#   进行{{洞察}}。（查看你主牌堆顶部的一张牌。你可以选择将其回收。）
card("UNL-131", keywords={Keyword.REACTION})

# UNL-134 存在焦虑
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   {{回响}}{{2}}（你可以选择支付此额外费用，以重复此法术效果。）
#   {{眩晕}}一名正在进攻的敌方单位。如果它已经被眩晕，则改为让该单位返回其所属的手牌。（被眩晕的单位在本回合内无法造成战斗伤害。）
card("UNL-134", keywords={Keyword.ACTION, Keyword.REPEAT})

# UNL-136 占卜花朵
#   此牌以休眠状态进场。
#   摧毁此牌，支付{{1}}，{{横置}}：{{洞察2}}，然后抽一张牌。获得1经验。（执行洞察2，即查看你主牌堆顶部的两张牌。你可以将其中任意卡牌回收，并将其余的卡牌按任意顺序放回原处。）
card("UNL-136", abilities=(
    AbilityDef(ability_id="UNL-136:enters_exhausted:0", kind="enters_exhausted", timing="passive", immediate=False, rules_ref=("R-CR-369.3", "R-CR-143.4", "R-CR-359.2.c",)),
))

# UNL-139 透骨尖钉
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   选择一处战场。让一名对手展示自己的手牌。你可以从中选择一名单位。让该对手将该单位打出到该战场，无视一切费用。当对手如此做时，{{眩晕}}该单位。（使其在本回合内无法造成战斗伤害。）
card("UNL-139", keywords={Keyword.HIDDEN})

# UNL-141 伊芙琳
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{后排}}（我在战斗中最后承担伤害。）
#   当你在你的回合中将我从正面朝下的状态打出时，你可以选择移动任意一名位于不同位置的敌方单位到我所在的战场。
card("UNL-141", keywords={Keyword.BACKLINE, Keyword.HIDDEN})

# UNL-142 残酷复活
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   你必须摧毁一名友方单位，作为打出此牌的额外费用。
#   从你的废牌堆中打出一名法力和符能费用不高于被摧毁单位的单位，无视其费用。
card("UNL-142", keywords={Keyword.REACTION})

# UNL-143 卡兹克
#   {{伏击}}（你可以选择将我作为{{反应}}牌，打出到有己方单位的战场。）
#   当我进攻或防守时，如果此处有一名落单的敌方单位，则让我本回合内{{S}}+2并获得2经验。
card("UNL-143", keywords={Keyword.AMBUSH})

# UNL-143a 卡兹克
#   {{伏击}}
#   当我进攻或防守时，如果此处有一名落单的敌方单位，则让我本回合内{{S}}+2并获得2经验。
card("UNL-143a", keywords={Keyword.AMBUSH})

# UNL-145 派克
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{后排}}（我在战斗中最后承担伤害。）
#   每回合限一次，如果我位于战场上，当一名敌方单位被摧毁时，打出一个休眠的“金币”装备指示物。（其具有“{{反应>}} 摧毁此牌，{{横置}}：{{获得}}{{A}}。”）
card("UNL-145", keywords={Keyword.BACKLINE, Keyword.HIDDEN})

# UNL-145a 派克
#   {{待命}}
#   {{后排}}
#   每回合限一次，如果我位于战场上，当一名敌方单位被摧毁时，打出一个休眠的“金币”装备指示物。
card("UNL-145a", keywords={Keyword.BACKLINE, Keyword.HIDDEN})

# UNL-149 黛安娜
#   {{伏击}}（你可以选择将我作为{{反应}}牌，打出到有己方单位的战场。）
#   每当你打出一个法术时，让我本回合内{{S}}+2。
card("UNL-149", keywords={Keyword.AMBUSH})

# UNL-149a 黛安娜
#   {{伏击}}
#   每当你打出一个法术时，让我本回合内{{S}}+2。
card("UNL-149a", keywords={Keyword.AMBUSH})

# UNL-150 薇古丝
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   当对手打出一名单位时，如果我位于战场上，则{{眩晕}}该单位。该对手在本回合内无法移动该单位。（使其在本回合内无法造成战斗伤害。）
card("UNL-150", keywords={Keyword.DEFLECT})

# UNL-150a 薇古丝
#   {{法盾}}
#   当对手打出一名单位时，如果我位于战场上，则{{眩晕}}该单位。该对手在本回合内无法移动该单位。
card("UNL-150a", keywords={Keyword.DEFLECT})

# UNL-152 黑色玫瑰要员
#   {{强攻}}（如果我是进攻方，则{{S}}+1。）
#   {{绝念>}} 召出一枚休眠的符文。（当我被摧毁后，发动此效果。）
card("UNL-152", keywords={Keyword.ASSAULT, Keyword.DEATHKNELL})

# UNL-153 腐泥疏浚工
#   {{绝念>}} 打出一名1{{S}}的“战鹰”到你的基地，它拥有{{法盾}}。（当我被摧毁后，发动此效果。对手必须支付{{A}}才能将拥有{{法盾}}的目标选作法术或技能的目标。）
card("UNL-153", keywords={Keyword.DEATHKNELL})

# UNL-155 英勇冲锋
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   让一名友方单位本回合内{{S}}+1，并{{眩晕}}其所在位置的一名敌方单位。（被眩晕的单位在本回合内无法造成战斗伤害。）
card("UNL-155", keywords={Keyword.ACTION})

# UNL-156 忠忠魄罗
#   {{绝念>}} 如果我被摧毁时未处于落单状态，则抽一张牌。（当我被摧毁后，发动此效果。所在位置没有其他友方单位时，即视为“落单”。）
card("UNL-156", keywords={Keyword.DEATHKNELL})

# UNL-161 占卜贝壳
#   {{预知}}（当你打出此牌时，查看主牌堆顶部的一张牌。你可以选择将其回收。）
#   {{迅捷>}} 摧毁此牌，{{横置}}：让一名单位在本回合内{{S}}+2。
card("UNL-161", keywords={Keyword.VISION})

# UNL-162 惊艳守护者
#   {{狩猎}}（当我征服或据守一处战场时，获得1经验。）
#   消耗2经验：给予我{{增益}}。（如果我未拥有增益，则获得一个{{S}}+1增益。）
card("UNL-162", keywords={Keyword.HUNT})

# UNL-166 追猎雪狼
#   {{伏击}}（你可以选择将我作为{{反应}}牌，打出到有己方单位的战场。）
#   你必须摧毁一名自己控制的“鸟类”、“猫科”、“犬形”或“魄罗”属性单位，作为打出我的额外费用。你可以选择将我打出至该单位所在的战场（即使你在该处没有其他单位）。
card("UNL-166", keywords={Keyword.AMBUSH})

# UNL-170 厄塔汗
#   你可以选择摧毁一名友方单位，作为打出我的额外费用。若如此做，则该单位每有1点法力费用，我的法力费用便减少{{1}}，该单位每有1点符能费用，我的符能费用便减少{{黄色}}。
#   {{游走}}（我可以向其他战场进行移动。）
#   当我进攻时，防守方必须摧毁其在此处的一名单位。
card("UNL-170", keywords={Keyword.GANKING})

# UNL-171 加里奥
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   {{壁垒}}（我在战斗中首先承担伤害。）
#   我无法造成战斗伤害。
card("UNL-171", keywords={Keyword.DEFLECT, Keyword.TANK}, abilities=(
    AbilityDef(ability_id="UNL-171:no_combat_damage:0", kind="no_combat_damage", timing="passive", immediate=False, rules_ref=("R-CR-465.2",)),
))

# UNL-172 乐芙兰
#   {{强攻}}（如果我是进攻方，则{{S}}+1。）
#   {{绝念>}} 抽一张牌。若此时是你的开始阶段，则改为抽两张牌。（当我被摧毁后，发动此效果。）
card("UNL-172", keywords={Keyword.ASSAULT, Keyword.DEATHKNELL})

# UNL-172a 乐芙兰
#   {{强攻}}
#   {{绝念>}} 抽一张牌。若此时是你的开始阶段，则改为抽两张牌。
card("UNL-172a", keywords={Keyword.ASSAULT, Keyword.DEATHKNELL})

# UNL-173 牺牲
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   你必须摧毁一名友方{{强力}}单位，作为打出此牌的额外费用。（战力达到5或以上时，即为强力单位。）
#   抽两张牌并召出一枚休眠的符文。
card("UNL-173", keywords={Keyword.REACTION})

# UNL-175 战术撤退
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   选择一名友方单位。本回合内，在该单位下次被摧毁时，改为移除其所受伤害、将其变为休眠状态、并将其召回。（把该单位送回基地，此行动不算作移动。）
card("UNL-175", keywords={Keyword.REACTION})

# UNL-176 蔚
#   {{伏击}}（你可以选择将我作为{{反应}}牌，打出到有己方单位的战场。）
#   当我进攻时，{{眩晕}}此处的一名敌方单位。（使其在本回合内无法造成战斗伤害。）
card("UNL-176", keywords={Keyword.AMBUSH})

# UNL-176a 蔚
#   {{伏击}}
#   当我进攻时，{{眩晕}}此处的一名敌方单位。
card("UNL-176a", keywords={Keyword.AMBUSH})

# UNL-178 波比
#   你可以选择消耗3经验，作为打出我的额外费用，以此让我的费用减少{{3}}。
#   {{伏击}}（你可以选择将我作为{{反应}}牌，打出到有己方单位的战场。）
#   {{壁垒}}（我在战斗中首先承担伤害。）
card("UNL-178", keywords={Keyword.AMBUSH, Keyword.TANK})

# UNL-178a 波比
#   你可以选择消耗3经验，作为打出我的额外费用，以此让我的费用减少{{3}}。
#   {{伏击}}
#   {{壁垒}}
card("UNL-178a", keywords={Keyword.AMBUSH, Keyword.TANK})

# UNL-179 峡谷先锋
#   当我移动至一处战场时，查看你主牌堆顶部的三张牌。你可以选择从中展示一名单位，并抽取该卡牌。回收其余的卡牌。
#   {{绝念>}} 从你的手牌中打出一名单位到你的基地，无视其法力费用。（当我被摧毁后，发动此效果。仍需支付所有符能费用。）
card("UNL-179", keywords={Keyword.DEATHKNELL})

# UNL-179a 峡谷先锋
#   当我移动至一处战场时，查看你主牌堆顶部的三张牌。你可以选择从中展示一名单位，并抽取该卡牌。回收其余的卡牌。
#   {{绝念>}} 从你的手牌中打出一名单位到你的基地，无视其法力费用。
card("UNL-179a", keywords={Keyword.DEATHKNELL})

# UNL-220 呸呸魄罗
#   {{法盾}}
card("UNL-220", reviewed=True, keywords={Keyword.DEFLECT})

# UNL-221 哀哀魄罗
#   {{绝念}} — 当我被摧毁时，如果此处没有其他友方单位，则抽一张牌。
card("UNL-221", keywords={Keyword.DEATHKNELL})

# UNL-223 壮壮魄罗
#   {{百炼}}
card("UNL-223", keywords={Keyword.WEAPONMASTER})

# UNL-224 叨叨魄罗
#   {{预知}}
card("UNL-224", reviewed=True, keywords={Keyword.VISION})

# UNL-225 莽莽魄罗
#   {{强攻}}
card("UNL-225", reviewed=True, keywords={Keyword.ASSAULT})

