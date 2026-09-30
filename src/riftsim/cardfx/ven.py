# 自动生成草稿（scripts/cards/gen_cardfx_from_defs.py）；人工 review 后为事实源。
# CN 原文注释为权威面；rules_ref 锚点随 AbilityDef 携带。
from ..cards import AbilityDef
from ..enums import Keyword
from . import card


# VEN-003 极寒脆化
#   摧毁一件装备。
#   {{流转4红色}}（你可以选择支付此牌的流转费用，将其从你的废牌堆中打出。然后将其放逐。）
card("VEN-003", keywords={Keyword.FLOW})

# VEN-007 拳拳魄罗
#   {{强化}} — 弃置一张手牌（支付此费用：强化我。仅在未强化时可用。）
#   {{已强化>}} 我获得{{S}}+1。
card("VEN-007", keywords={Keyword.EMPOWER})

# VEN-008 无情打击
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   你可以选择弃置一张手牌，作为打出此牌的额外费用。
#   对战场上的一名单位造成3点伤害。如果你支付了该额外费用，则改为对其造成5点伤害。
card("VEN-008", keywords={Keyword.ACTION})

# VEN-010 蚀骨诅咒
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   对战场上的一名单位造成2点伤害。你的废牌堆中每有一张此牌的同名卡牌，此牌便造成1点额外伤害。
card("VEN-010", keywords={Keyword.ACTION})

# VEN-011 悬摆之刃
#   {{装配红色}}（支付{{红色}}：将此牌贴附到你控制的一名单位上。）
#   When I move to a battlefield, give me +2 [M] this turn.（当我移动到一处战场时，给我 +2 战力本回合。）
#   口径：「我」=宿主顶部卡（719.1 文本添加）→宿主 might_temp，317.2.c/d 回合结束失效
card("VEN-011", reviewed=True, keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="VEN-011:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('R',), target_scope="unit"),
        AbilityDef(ability_id="VEN-011:trigger:move:0", kind="trigger", trigger="move",
                   payload="pump_turn", value=2,
                   rules_ref=("R-CR-383.3", "R-CR-719.1", "R-CR-317.2.c")),
    )
)

# VEN-012 表里杀缭乱
#   让一名单位变为活跃状态，并给予其在本回合内{{强攻3}}。（如果其为进攻方，则{{S}}+3。）
#   {{流转3红色}}（你可以选择支付此牌的流转费用，以此将其从你的废牌堆中打出。然后将其放逐。）
card("VEN-012", keywords={Keyword.FLOW})

# VEN-014 暗影之魔
#   {{强化2红色}}（支付{{2}}和{{红色}}：强化我。仅在未强化时可用。）
#   {{已强化>}} 我获得{{强攻3}}。（如果我是进攻方，则{{S}}+3。）
card("VEN-014", keywords={Keyword.EMPOWER})

# VEN-015 暴怒箴言
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   此牌无法被无效化。
#   对一名具有翠意（{{绿色}}）特性的敌方单位造成4点伤害。
card("VEN-015", keywords={Keyword.ACTION})

# VEN-016 蚀影巨龙
#   {{急速}}（你可以选择额外支付{{1}}和{{红色}}，让我以活跃状态进场。）
#   当我移动时，如果你控制的符文数量不超过四枚，则抽一张牌。
card("VEN-016", keywords={Keyword.ACCELERATE})

# VEN-017 莫甘娜
#   {{伏击}}（你可以选择将我作为{{反应}}牌，打出到有己方单位的战场。）
#   当你打出我时，对一名单位造成伤害，其数量等同于该单位上已标记的伤害数值。
card("VEN-017", keywords={Keyword.AMBUSH})

# VEN-018 怒火放大器
#   {{强化6红色}}（支付{{6}}和{{红色}}：强化此牌。仅在未强化时可用。）
#   你的单位获得{{S}}+1。如果我{{已强化}}，则改为让其获得{{S}}+2。
card("VEN-018", keywords={Keyword.EMPOWER})

# VEN-019 雷克顿
#   {{急速}}（你可以选择额外支付{{1}}和{{红色}}，让我以活跃状态进场。）
#   当我进攻时，如果你控制的符文数量不超过四枚，则对此处的所有敌方单位各造成2点伤害。
card("VEN-019", keywords={Keyword.ACCELERATE})

# VEN-019a 雷克顿
#   {{急速}}
#   当我进攻时，如果你控制的符文数量不超过四枚，则对此处的所有敌方单位各造成2点伤害。
card("VEN-019a", keywords={Keyword.ACCELERATE})

# VEN-021 阿卡丽
#   {{强化2红色}}（支付{{2}}和{{红色}}：强化我。仅在未强化时可用。）
#   当我移动时，你可以选择对我移动起点或终点的战场上的一名单位造成1点伤害。如果我{{已强化}}，则改为造成2点伤害。
#   {{已强化>}} 我获得{{S}}+1。
card("VEN-021", keywords={Keyword.EMPOWER})

# VEN-021a 阿卡丽
#   {{强化2红色}}
#   当我移动时，你可以选择对我移动起点或终点的战场上的一名单位造成1点伤害。如果我{{已强化}}，则改为造成2点伤害。
#   {{已强化>}} 我获得{{S}}+1。
card("VEN-021a", keywords={Keyword.EMPOWER})

# VEN-027 杠锤
#   {{装配绿色}}（支付{{绿色}}：将此牌贴附到你控制的一名单位上。）
#   
# 数据缺陷修复（bilingual 丢 effect_plain）暴露：卡体效果段未接线 → 降级回评
#   段（来自 EN）：战场恰有另一友方单位时+2（条件持续，未接）
card("VEN-027", keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="VEN-027:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('G',), target_scope="unit"),
    )
)

# VEN-030 无情苦修者
#   {{强化3}}（支付{{3}}：强化我。仅在未强化时可用。）
#   {{已强化>}} 我获得{{法盾}}和{{坚守3}}。（对手必须支付{{A}}才能将我选作法术或技能的目标。如果我是防守方，则{{S}}+3。）
card("VEN-030", keywords={Keyword.EMPOWER})

# VEN-031 我流奥义！霞阵
#   给予一名友方单位在本回合内{{S}}+1。其在本回合内无法被敌方法术和技能选作目标。
#   {{流转2}}（你可以选择支付此牌的流转费用，以此将其从你的废牌堆中打出。然后将其放逐。）
card("VEN-031", keywords={Keyword.FLOW})

# VEN-034 回音击
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   {{反应}}（可在你的回合或法术对决中打出。）
#   选择一处受你控制的战场，和一名位于其他位置且受你控制的单位。将该单位移动到该战场，并给予其在本回合内{{S}}+2。
card("VEN-034", keywords={Keyword.HIDDEN, Keyword.REACTION})

# VEN-035 念化盈虚
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   选择一个效果 —
#   - 强化一名单位。回合结束时，解除其强化。
#   - 解除一名{{已强化}}单位的强化。在回合结束时，强化该单位。
card("VEN-035", keywords={Keyword.REACTION})

# VEN-039 崩解之沙
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   如果对手在本回合内打出过其他法术，则无效化一个法术。
card("VEN-039", keywords={Keyword.REACTION})

# VEN-040 专注箴言
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   选择一名正在与具有炽烈（{{红色}}）特性的敌方单位进行战斗、或被敌方具有炽烈特性的法术选为目标的友方单位。给予其在本回合内{{S}}+4。
card("VEN-040", keywords={Keyword.REACTION})

# VEN-041 锐雯
#   {{百炼}}（当你打出我时，你可以选择为我{{装配}}你的一件武装，其装配费用减少{{A}}。可选择已贴附的武装。）
#   当我进攻时，选择此处的一名敌方单位。我身上每贴附一件武装，便对其造成2点伤害。
card("VEN-041", keywords={Keyword.WEAPONMASTER})

# VEN-043 钢爪
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
#   {{强化7}}（支付{{7}}：强化我。仅在未强化时可用。）
#   {{已强化>}} 我获得{{S}}+7。
card("VEN-043", keywords={Keyword.DEFLECT, Keyword.EMPOWER})

# VEN-045 抑制之盔
#   {{强化4绿色}}（支付{{4}}和{{绿色}}：强化此牌。仅在未强化时可用。）
#   对手的法术费用增加{{1}}。如果此牌{{已强化}}，则改为对手的法术费用增加{{1}}和{{A}}。
card("VEN-045", keywords={Keyword.EMPOWER})

# VEN-046 内瑟斯
#   {{法盾2}}（对手必须支付{{A}}{{A}}才能将我选作法术或技能的目标。）
#   {{强化8}}（支付{{8}}：强化我。仅在未强化时可用。）
#   {{已强化>}} 当我征服一处战场时，你获得1分。
card("VEN-046", keywords={Keyword.DEFLECT, Keyword.EMPOWER}, keyword_values={"deflect": 2})

# VEN-046a 内瑟斯
#   {{法盾2}}
#   {{强化8}}
#   {{已强化>}} 当我征服一处战场时，你获得1分。
card("VEN-046a", keywords={Keyword.DEFLECT, Keyword.EMPOWER}, keyword_values={"deflect": 2})

# VEN-047 见习法师
#   {{强化2}}（支付{{2}}：强化我。仅在未强化时可用。）
#   当我变为{{已强化}}时，进行{{洞察2}}。（查看你主牌堆顶部的两张牌。你可以将其中任意卡牌回收，并将其余的卡牌按任意顺序放回原处。）
#   {{已强化>}} 我获得{{S}}+1。
card("VEN-047", keywords={Keyword.EMPOWER})

# VEN-048 云端亚龙
#   当你打出我时，抽一张牌。
card("VEN-048", reviewed=True, abilities=(
    AbilityDef(ability_id="VEN-048:on_play_draw:0", kind="on_play_draw", timing="trigger", immediate=False, rules_ref=("R-CR-383.1", "R-CR-413.1",), draw_count=1),
))

# VEN-049 深水打捞
#   抽一张牌。
#   {{流转2}}（你可以选择支付此牌的流转费用，以此将其从你的废牌堆中打出。然后将其放逐。）
card("VEN-049", keywords={Keyword.FLOW}, abilities=(
    AbilityDef(ability_id="VEN-049:spell_draw:0", kind="spell_draw", timing="passive", immediate=False, rules_ref=("R-CR-413.1",), draw_count=1),
))

# VEN-051 迭代式设计
#   打出一名3{{S}}的“机器人”。
#   {{流转2蓝色}}（你可以选择支付此牌的流转费用，以此将其从你的废牌堆中打出。然后将其放逐。）
card("VEN-051", keywords={Keyword.FLOW})

# VEN-052 惑心转意
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   选择一个效果 —
#   - 让一名友方单位返回其所属的手牌。
#   - 给予一名敌方单位在本回合内{{S}}-2。
card("VEN-052", keywords={Keyword.REACTION})

# VEN-054 可疑之书
#   {{强化}} — {{横置}}（支付此费用：强化我。仅在未强化时可用。）
#   解除此牌的强化，支付{{1}}，{{横置}}：抽一张牌。
card("VEN-054", keywords={Keyword.EMPOWER})

# VEN-055 实干研究员
#   {{强化3}}（支付{{3}}：强化我。仅在未强化时可用。）
#   {{已强化>}} 你的法术费用减少{{1}}和{{A}}，不得低于{{1}}。
card("VEN-055", keywords={Keyword.EMPOWER})

# VEN-056 千里眼
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   {{洞察5}}。（查看你主牌堆顶部的五张牌。你可以将其中任意卡牌回收，并将其余的卡牌按任意顺序放回原处。）
#   抽两张牌。
card("VEN-056", keywords={Keyword.REACTION})

# VEN-057 秘密线人
#   {{强化3}}（支付{{3}}：强化我。仅在未强化时可用。）
#   {{已强化>}} 当我移动时，抽一张牌。
card("VEN-057", keywords={Keyword.EMPOWER})

# VEN-059 电能震荡
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   如果你控制着{{已强化}}的物体，则此牌的费用减少{{2}}。
#   对战场上的一名单位造成4点伤害，
card("VEN-059", keywords={Keyword.ACTION}, abilities=(
    AbilityDef(ability_id="VEN-059:spell_damage:0", kind="spell_damage", timing="passive", immediate=False, rules_ref=("R-CR-157.1", "R-CR-417.1",), damage=4, target_scope="unit_at_battlefield"),
))

# VEN-061 洞察箴言
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   支付此法术的费用时，无视{{法盾}}。
#   给予一名具有摧破（{{橙色}}）特性的敌方单位在本回合内{{S}}-5。
card("VEN-061", keywords={Keyword.REACTION})

# VEN-062 海克斯方程式
#   此牌以休眠状态进场。
#   {{横置}}：强化另一件装备。（如果其未被强化，则变为已强化状态。）
card("VEN-062", abilities=(
    AbilityDef(ability_id="VEN-062:enters_exhausted:0", kind="enters_exhausted", timing="passive", immediate=False, rules_ref=("R-CR-369.3", "R-CR-143.4", "R-CR-359.2.c",)),
))

# VEN-064 广场守卫
#   你每控制一件装备，我的费用便减少{{1}}。
#   {{法盾}}（对手必须支付{{A}}才能将我选作法术或技能的目标。）
card("VEN-064", keywords={Keyword.DEFLECT})

# VEN-065 斯维因
#   {{预知}}（当你打出我时，查看主牌堆顶部的一张牌。你可以选择将其回收。）
#   当我征服一处战场时，如果你在本回合内打出了一名非指示物单位、一件非指示物装备和一个法术，则你获得1分。
card("VEN-065", keywords={Keyword.VISION})

# VEN-066 时空裂隙
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   放逐一名单位，然后让其拥有者将其打出到同一位置，无视其费用。
card("VEN-066", keywords={Keyword.HIDDEN})

# VEN-069 梅尔
#   当你打出我时，抽一张牌。
#   {{强化3}}（支付{{3}}：强化我。仅在未强化时可用。）
#   {{已强化>}} 你的法术和技能无法被无效化。如果你控制的法术或技能将给予其选作目标的一名单位-{{S}}，则其额外给予{{S}}-1。
card("VEN-069", keywords={Keyword.EMPOWER}, abilities=(
    AbilityDef(ability_id="VEN-069:on_play_draw:0", kind="on_play_draw", timing="trigger", immediate=False, rules_ref=("R-CR-383.1", "R-CR-413.1",), draw_count=1),
))

# VEN-069a 梅尔
#   当你打出我时，抽一张牌。
#   {{强化3}}
#   {{已强化>}} 你的法术和技能无法被无效化。如果你控制的法术或技能将给予其选作目标的一名单位-{{S}}，则其额外给予{{S}}-1。
card("VEN-069a", keywords={Keyword.EMPOWER}, abilities=(
    AbilityDef(ability_id="VEN-069a:on_play_draw:0", kind="on_play_draw", timing="trigger", immediate=False, rules_ref=("R-CR-383.1", "R-CR-413.1",), draw_count=1),
))

# VEN-070 残暴猎手
#   {{强化3}}（支付{{3}}：强化我。仅在未强化时可用。）
#   {{已强化>}} 我获得{{S}}+2和{{游走}}。（我可以向其他战场进行移动。）
card("VEN-070", keywords={Keyword.EMPOWER})

# VEN-072 深沉咆哮
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   给予一名单位在本回合内{{S}}+2。如果该单位{{已强化}}，则改为给予其在本回合内{{S}}+4。
card("VEN-072", keywords={Keyword.ACTION})

# VEN-074 军团掠阵兵
#   {{强化}} — 支付{{1}}或{{橙色}}（支付其中一种费用：强化我。仅在未强化时可用。）
#   {{已强化>}} 我获得{{S}}+1。
card("VEN-074", keywords={Keyword.EMPOWER})

# VEN-075 剑头蛟的卵
#   此牌以休眠状态进场。
#   {{强化}} — 支付{{1}}，{{横置}}（支付此费用：强化此牌。仅在未强化时可用。）
#   {{反应>}} {{横置}}：{{获得}}{{1}}。如果此牌{{已强化}}，则改为{{获得}}{{2}}。
card("VEN-075", keywords={Keyword.EMPOWER}, abilities=(
    AbilityDef(ability_id="VEN-075:enters_exhausted:0", kind="enters_exhausted", timing="passive", immediate=False, rules_ref=("R-CR-369.3", "R-CR-143.4", "R-CR-359.2.c",)),
))

# VEN-077 帝国工具
#   {{强化2}}（支付{{2}}：强化此牌。仅在未强化时可用。）
#   {{横置}}：给予一名单位在本回合内{{S}}+2。如果此牌{{已强化}}，则改为给予该单位在本回合内{{S}}+4。
card("VEN-077", keywords={Keyword.EMPOWER})

# VEN-078 枯爪巴凯
#   {{强化1AA}}（支付{{1}}和{{A}}{{A}}：强化我。仅在未强化时可用。）
#   {{已强化>}} 我获得{{S}}+2。
#   {{已强化>}}{{>绝念>}} 召出两枚休眠的符文。（当我在已强化状态下被摧毁时，发动此效果。）
card("VEN-078", keywords={Keyword.EMPOWER})

# VEN-079 夺魂钩 妲姆
#   {{强化5橙色}}（支付{{5}}和{{橙色}}：强化我。仅在未强化时可用。）
#   {{已强化>}} 当我进攻或防守时，选择此处一名战力大于我的单位。在本回合内将我的战力提升至与其战力相同，然后给予我在本回合内{{S}}+1。
card("VEN-079", keywords={Keyword.EMPOWER})

# VEN-081 狂袭
#   给予一名单位在本回合内{{S}}+6。
#   {{流转4}}（你可以选择支付此牌的流转费用，以此将其从你的废牌堆中打出。然后将其放逐。）
card("VEN-081", keywords={Keyword.FLOW})

# VEN-084 安蓓萨
#   {{强化3橙色}}（支付{{3}}和{{橙色}}：强化我。仅在未强化时可用。）
#   {{已强化>}} 我获得{{S}}+3，且除非我处于战斗中，否则我无法受到伤害。
card("VEN-084", keywords={Keyword.EMPOWER})

# VEN-084a 安蓓萨
#   {{强化3橙色}}
#   {{已强化>}} 我获得{{S}}+3，且除非我处于战斗中，否则我无法受到伤害。
card("VEN-084a", keywords={Keyword.EMPOWER})

# VEN-086 普朗克
#   {{强化橙色橙色}}（支付{{橙色}}{{橙色}}：强化我。仅在未强化时可用。）
#   {{已强化>}} 如果一个将我选作目标的法术或技能将眩晕我、或给予我-{{S}}、或把我送回手牌，则改为给予我在本回合内{{S}}+3。
card("VEN-086", keywords={Keyword.EMPOWER})

# VEN-087 海克斯圆盘
#   {{强化}} — {{横置}}（支付此费用：强化此牌。仅在未强化时可用。）
#   解除此牌的强化，支付{{1}}，{{横置}}：打出一名3{{S}}的“机器人”到你的基地。
card("VEN-087", keywords={Keyword.EMPOWER})

# VEN-093 均衡渡命人
#   {{强化2}}（支付{{2}}：强化我。仅在未强化时可用。）
#   {{已强化>}} 我获得{{S}}+1和{{游走}}。（我可以向其他战场进行移动。）
card("VEN-093", keywords={Keyword.EMPOWER})

# VEN-097 小蜘蛛
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   你在此处每控制一名和我同名的其他单位，我便获得{{S}}+1。
#   你的卡组中可以包含任意数量名为“小蜘蛛”的卡牌。
card("VEN-097", keywords={Keyword.HIDDEN})

# VEN-099 旋风武者
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   当你将我从正面朝下的状态打出时，你可以选择强化此处的一个物体。在回合结束时，解除其强化。
card("VEN-099", keywords={Keyword.HIDDEN})

# VEN-100 深渊之触
#   打出两名具有“比尔吉沃特”属性的1{{S}}“触手”。
#   {{流转3}}（你可以选择支付此牌的流转费用，以此将其从你的废牌堆中打出。然后将其放逐。）
card("VEN-100", keywords={Keyword.FLOW})

# VEN-101 劲风修士
#   你可以选择支付{{1}}，作为打出我的额外费用。
#   当你打出我时，如果你支付了该额外费用，则从任意废牌堆中放逐一张牌，以此给予一名单位在本回合内{{强攻2}}。（如果它是进攻方，则{{S}}+2。）
card("VEN-101", abilities=(
    AbilityDef(ability_id="VEN-101:extra_cost:0", kind="extra_cost", timing="passive", immediate=False, rules_ref=("R-CR-356.2",), cost_symbols=("1",)),
))

# VEN-104 披尾女族长
#   {{强化2紫色}}（支付{{2}}和{{紫色}}：强化我。仅在未强化时可用。）
#   当我变为{{已强化}}时，你可以选择从你的废牌堆中选择一名法力费用不高于{{3}}且符能费用不高于{{A}}的单位。将其打出到你的基地，无视其费用。
card("VEN-104", keywords={Keyword.EMPOWER})

# VEN-105 奥义！幽步
#   移动一名不高于3{{S}}的单位。
#   {{流转4紫色}}（你可以选择支付此牌的流转费用，以此将其从你的废牌堆中打出。然后将其放逐。）
card("VEN-105", keywords={Keyword.FLOW})

# VEN-106 风灵瞬转
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   选择战场上的一名单位。如果其战力不高于3{{S}}，则将其放逐。否则让其返回其所属的手牌。
card("VEN-106", keywords={Keyword.ACTION})

# VEN-110 梅尔
#   {{强化}} — 弃置一张法术牌（支付此费用：强化我。仅在未强化时可用。）
#   当我变为{{已强化}}时，放逐战场上一名不高于3{{S}}的敌方单位。
card("VEN-110", keywords={Keyword.EMPOWER})

# VEN-110a 梅尔
#   {{强化}} — 弃置一张法术牌
#   当我变为{{已强化}}时，放逐战场上一名不高于3{{S}}的敌方单位。
card("VEN-110a", keywords={Keyword.EMPOWER})

# VEN-114 卡洛克斯
#   {{强化6紫色紫色}}（支付{{6}}和{{紫色}}{{紫色}}：强化我。仅在未强化时可用。）
#   当我变为{{已强化}}时，选择一名对手。该玩家{{燃烧3}}。然后你可以选择进行一次：从其废牌堆中选择一名单位，并当作自己的牌打出，无视其费用。（将其主牌堆顶部的三张牌放入废牌堆，即为燃烧3。）
card("VEN-114", keywords={Keyword.EMPOWER})

# VEN-115 海洋亚龙
#   你可以选择将我打出到一处开放的战场。
#   当你打出我时，你可以选择让一名非“龙”属性的单位返回其所属的手牌。
card("VEN-115", abilities=(
    AbilityDef(ability_id="VEN-115:location_open_battlefield:0", kind="location_open_battlefield", timing="passive", immediate=False, rules_ref=("R-CR-170.11", "R-CR-170.11.c",)),
))

# VEN-116 龙之形
#   选择一名单位。其基础战力在本回合内变为5。
#   {{流转3}}（你可以选择支付此牌的流转费用，以此将其从你的废牌堆中打出。然后将其放逐。）
card("VEN-116", keywords={Keyword.FLOW})

# VEN-117 慎的弟子
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   如果我所在的战场上受你控制的其他单位有且仅有一个，则我获得{{坚守3}}。（如果我是防守方，则{{S}}+3。）
card("VEN-117", keywords={Keyword.HIDDEN})

# VEN-118 龙角勇士
#   {{壁垒}}（我在战斗中首先承担伤害。）
card("VEN-118", reviewed=True, keywords={Keyword.TANK})

# VEN-120 雷霆之怒 玛萨
#   你可以选择支付{{黄色}}，作为打出我的额外费用。 
#   当你打出我时，如果你支付了该额外费用，则{{眩晕}}战场上的一名敌方单位。（使其在本回合内无法造成战斗伤害。）
card("VEN-120", abilities=(
    AbilityDef(ability_id="VEN-120:extra_cost:0", kind="extra_cost", timing="passive", immediate=False, rules_ref=("R-CR-356.2",), cost_symbols=("Y",)),
))

# VEN-122 烈阳之鹰
#   {{强化2}}（支付{{2}}：强化我。仅在未强化时可用。）
#   {{已强化>}} 我获得{{S}}+1和{{法盾2}}。（对手必须支付{{A}}{{A}}才能将我选作法术或技能的目标。）
card("VEN-122", keywords={Keyword.EMPOWER})

# VEN-123 织魂者
#   {{伏击}}（你可以选择将我作为{{反应}}牌，打出到有己方单位的战场。）
card("VEN-123", reviewed=True, keywords={Keyword.AMBUSH})

# VEN-124 脱逃的灰背
#   {{强化}} — 摧毁一名友方单位（支付此费用：强化我。仅在未强化时可用。）
#   {{已强化>}} 我获得{{S}}+2。
card("VEN-124", keywords={Keyword.EMPOWER})

# VEN-126 忍法！气合盾
#   {{反应}}（可在任意时机打出，甚至先于其他法术和技能的结算。）
#   选择一名单位。抵挡该单位在本回合内将受到的7点伤害。（对手可以分配额外战斗伤害来摧毁该单位。）
card("VEN-126", keywords={Keyword.REACTION})

# VEN-127 血戮
#   选择一名单位。如果该单位{{已强化}}，则解除其强化。然后如果其战力不高于3{{S}}，则将其摧毁。
#    {{流转4黄色黄色}}（你可以选择支付此牌的流转费用，以此将其从你的废牌堆中打出。然后将其放逐。）
card("VEN-127", keywords={Keyword.FLOW})

# VEN-128 诺克萨斯使节
#   {{强化1黄色}}（支付{{1}}和{{黄色}}：强化我。仅在未强化时可用。）
#   {{已强化>}}{{>绝念>}} 打出两名1{{S}}的“随从”到你的基地。（当我在已强化状态下被摧毁时，发动此效果。）
card("VEN-128", keywords={Keyword.EMPOWER})

# VEN-130 奥洛克将军
#   {{强化3黄色}}（支付{{3}}和{{黄色}}：强化我。仅在未强化时可用。）
#   {{已强化>}} 你的{{已强化}}单位获得{{S}}+2（包括我在内）。
card("VEN-130", keywords={Keyword.EMPOWER})

# VEN-133 发光石
#   {{强化AA}}（支付{{A}}{{A}}：强化我。仅在未强化时可用。）
#   解除此牌的强化，{{横置}}：选择一名玩家。该玩家获得此牌的控制权，并将其召回。（将其送到该玩家的基地。）
#   在你回合结束时，摧毁此牌，并对你控制的所有单位各造成5点伤害。
card("VEN-133", keywords={Keyword.EMPOWER})

# VEN-134 凯尔
#   {{强化3}}（支付{{3}}：强化我。）
#   我最多可以拥有3个{{已强化}}。
#   我每拥有1个{{已强化}}，便获得{{S}}+2。
#   如果我拥有3个{{已强化}}，则我获得{{法盾3}}和{{游走}}。
card("VEN-134", keywords={Keyword.EMPOWER})

# VEN-135 凯南
#   {{待命}}（支付{{A}}正面朝下放置此牌，之后可支付{{0}}将其当作反应牌打出。）
#   当你打出我时，或当我进攻时，你可以选择支付{{2}}，以此{{眩晕}}一名单位。（使其在本回合内无法造成战斗伤害。）
#   如果此处有一名被眩晕的敌方单位，则我获得{{S}}+2。
card("VEN-135", keywords={Keyword.HIDDEN})

# VEN-135a 凯南
#   {{待命}}
#   当你打出我时，或当我进攻时，你可以选择支付{{2}}，以此{{眩晕}}一名单位。
#   如果此处有一名被眩晕的敌方单位，则我获得{{S}}+2。
card("VEN-135a", keywords={Keyword.HIDDEN})

# VEN-136 安蓓萨
#   {{强化1黄色黄色}}（支付{{1}}和{{黄色}}{{黄色}}：强化我。仅在未强化时可用。）
#    {{已强化>}} 我获得{{强攻2}}。（如果我是进攻方，则{{S}}+2。）
#    {{已强化>}} 当我进攻时，摧毁此处一名战力低于我的敌方单位。
card("VEN-136", keywords={Keyword.EMPOWER})

# VEN-136a 安蓓萨
#   {{强化1黄色黄色}}
#   {{已强化>}} 我获得{{强攻2}}。
#   {{已强化>}} 当我进攻时，摧毁此处一名战力低于我的敌方单位。
card("VEN-136a", keywords={Keyword.EMPOWER})

# VEN-137 可疑的眼镜
#   {{装配1黄色}}（支付{{1}}和{{黄色}}：将此牌贴附到你控制的一名单位上。）
#   此牌贴附到单位上时，选择另一名友方单位。装配此牌的单位在此牌贴附期间变为所选单位的复制体。
card("VEN-137", keywords={Keyword.EQUIP},
    abilities=(
        AbilityDef(ability_id="VEN-137:equip:0", kind="equip", timing="action",
                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),
                   cost_symbols=('1', 'Y'), target_scope="unit"),
    )
)

# VEN-138 慎
#   {{坚守}}（如果我是防守方，则{{S}}+1。）
#   当我据守一处战场时，如果此处受你控制的其他单位有且仅有一个，则你获得1分。
card("VEN-138", keywords={Keyword.SHIELD})

# VEN-138a 慎
#   {{坚守}}
#   当我据守一处战场时，如果此处受你控制的其他单位有且仅有一个，则你获得1分。
card("VEN-138a", keywords={Keyword.SHIELD})

# VEN-139 离群之刺
#   {{强化3A}}（支付{{3}}和{{A}}：强化此牌。仅在未强化时可用。）
#   {{迅捷>}}{{横置}}：如果这是你的回合，则将一名处于法术对决中的友方单位移动到基地，且如果我{{已强化}}，则让该单位变为活跃状态。
card("VEN-139", keywords={Keyword.EMPOWER})

# VEN-142 终极统治
#   {{迅捷}}（可在你的回合或法术对决中打出。）
#   在本回合内，让一名单位的战力翻倍，并给予其“{{A}}{{A}}：让我变为活跃状态。”
card("VEN-142", keywords={Keyword.ACTION})

# VEN-149 未来守护者
#   {{强化2AA}}（支付{{2}}和{{A}}{{A}}：强化我。仅在未强化时可用。）
#   支付{{1}}，{{横置}}：让一件装备变为活跃状态。 
#   {{已强化>}} 支付{{1}}，{{横置}}：让两件装备变为活跃状态。
card("VEN-149", keywords={Keyword.EMPOWER})

# VEN-156 奥义！雷铠
#   查看你主牌堆顶部的三张牌。你可以选择指定其中一张，并抽取该卡牌。将其余卡牌放进你的废牌堆。
#   {{流转2A}}（你可以选择支付此牌的流转费用，以此将其从你的废牌堆中打出。然后将其放逐。）
card("VEN-156", keywords={Keyword.FLOW})

# VEN-167 蔚
#   {{游走}}
#   从废牌堆回收一张卡牌：让我在本回合内{{S}}+1（可重复执行）。
card("VEN-167", keywords={Keyword.GANKING})

# VEN-168 金克丝
#   {{急速}}
#   {{强攻2}}
#   当你打出我时，弃置两张手牌。
card("VEN-168", keywords={Keyword.ACCELERATE, Keyword.ASSAULT}, keyword_values={"assault": 2})

# VEN-171 锐雯
#   {{百炼}}
#   当我进攻时，选择此处的一名敌方单位。我身上每贴附一件武装，便对其造成2点伤害。
card("VEN-171", keywords={Keyword.WEAPONMASTER})

# VEN-173 斯维因
#   {{预知}}
#   当我征服一处战场时，如果你在本回合内打出了一名非指示物单位、一件非指示物装备和一个法术，则你获得1分。
card("VEN-173", keywords={Keyword.VISION})

# VEN-174 艾瑞莉娅
#   {{法盾}}
#   当你选择我为目标、或让我变为活跃状态时，给予我在本回合内{{S}}+1。
card("VEN-174", keywords={Keyword.DEFLECT})

# VEN-179 雷恩加尔
#   {{伏击}}
#   我可以{{伏击}}到有敌方单位的战场，即使你在该处没有单位。
card("VEN-179", keywords={Keyword.AMBUSH})

# VEN-180 卡兹克
#   {{狩猎}}
#   当我进攻时，你可以选择消耗3经验，以此对此处的一名敌方单位造成等同于我战力的伤害。
card("VEN-180", keywords={Keyword.HUNT})

# VEN-181 普朗克
#   {{强化橙色橙色}}
#   {{已强化>}} 如果一个将我选作目标的法术或技能将眩晕我、或给予我-{{S}}、或把我送回手牌，则改为给予我在本回合内{{S}}+3。
card("VEN-181", keywords={Keyword.EMPOWER})

# VEN-183 黛安娜
#   {{伏击}}
#   当你打出一个法术时，给予我在本回合内{{S}}+2。
card("VEN-183", keywords={Keyword.AMBUSH})

# VEN-184 蕾欧娜
#   {{坚守}}
#   当我进攻时，眩晕此处的一名敌方单位。
card("VEN-184", keywords={Keyword.SHIELD})

# VEN-185 凯尔
#   {{强化3}}（支付{{3}}：强化我。）
#   我最多可以拥有3个{{已强化}}。
#   我每拥有1个{{已强化}}，便获得{{S}}+2。
#   如果我拥有3个{{已强化}}，则我获得{{法盾3}}和{{游走}}。
card("VEN-185", keywords={Keyword.EMPOWER})

# VEN-186 莫甘娜
#   {{伏击}}
#   当你打出我时，对一名单位造成等同于其伤害标记数值的伤害。
card("VEN-186", keywords={Keyword.AMBUSH})

# VEN-187 安蓓萨
#   {{强化1黄色黄色}}
#   {{已强化>}} 我获得{{强攻2}}。
#   {{已强化>}} 当我进攻时，摧毁此处一名战力低于我的敌方单位。
card("VEN-187", keywords={Keyword.EMPOWER})

# VEN-188 梅尔
#   {{强化}} — 弃置一个法术
#   当我变为{{已强化}}时，放逐战场上一名不高于3{{S}}的敌方单位。
card("VEN-188", keywords={Keyword.EMPOWER})

# VEN-189 离群之刺
#   {{强化3A}}
#   {{迅捷>}}{{横置}}：如果这是你的回合，则将一名处于法术对决中的友方单位移动到基地，且如果我{{已强化}}，则让该单位变为活跃状态。
card("VEN-189", keywords={Keyword.EMPOWER})

# VEN-189* 离群之刺
#   {{强化3A}}
#   {{迅捷>}}{{横置}}：如果这是你的回合，则将一名处于法术对决中的友方单位移动到基地，且如果我{{已强化}}，则让该单位变为活跃状态。
card("VEN-189*", keywords={Keyword.EMPOWER})

# VEN-194 未来守护者
#   {{强化2AA}}
#   支付{{1}}，{{横置}}：让一件装备变为活跃状态。 
#   {{已强化>}} 支付{{1}}，{{横置}}：让两件装备变为活跃状态。
card("VEN-194", keywords={Keyword.EMPOWER})

# VEN-194* 未来守护者
#   {{强化2AA}}
#   支付{{1}}，{{横置}}：让一件装备变为活跃状态。 
#   {{已强化>}} 支付{{1}}，{{横置}}：让两件装备变为活跃状态。
card("VEN-194*", keywords={Keyword.EMPOWER})

# VEN-SP1 卡莎
#   {{急速}}
#   当我征服一处战场时，抽一张牌。
card("VEN-SP1", keywords={Keyword.ACCELERATE})

