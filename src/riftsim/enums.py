# 枚举与符号常量；每项注释锚定规则（R-CR-xxx）。
from __future__ import annotations

from enum import Enum


class CardType(str, Enum):
    """卡牌/物体类型（R-CR-133 类别=超类型+类型+标签）。"""

    UNIT = "unit"            # R-CR-140
    GEAR = "gear"            # R-CR-147
    SPELL = "spell"          # R-CR-153
    RUNE = "rune"            # R-CR-160
    LEGEND = "legend"        # R-CR-173
    BATTLEFIELD = "battlefield"  # R-CR-169
    TOKEN = "token"          # R-CR-179（P1 用）


class Domain(str, Enum):
    """特性（R-CR-134）。[A]=任意、[C]=自身——作为费用匹配语义在 cost 计算中处理。"""

    R = "R"  # 炽烈
    G = "G"  # 冷静
    B = "B"  # 毁灭？（名称以规则为准，引擎仅用符号）
    O = "O"
    P = "P"
    Y = "Y"


class Privacy(str, Enum):
    """隐私三级（R-CR-128）。"""

    PUBLIC = "public"
    PRIVATE = "private"   # 仅持有者
    SECRET = "secret"     # 无人可知（牌堆顺序、对手手牌内容）


class Zone(str, Enum):
    """区域（R-CR-105..108）。场上位置由 Battlefield/Base 结构再说，zone 取枚举便于序列化。"""

    HAND = "hand"
    MAIN_DECK = "main_deck"
    RUNE_DECK = "rune_deck"
    TRASH = "trash"
    BANISH = "banish"
    LEGEND_ZONE = "legend_zone"
    HERO_ZONE = "hero_zone"
    CHAIN = "chain"
    HIDDEN_SLOT = "hidden_slot"   # 待命区（R-CR-108/811：容量 1 牌面朝下私密）
    BASE = "base"
    BATTLEFIELD = "battlefield"
    ASIDE = "aside"               # 搁置（Setup 战场 113、调度 117）


class Phase(str, Enum):
    """回合阶段（R-CR-314..317）。SETUP/GAME_OVER 为引擎边界态。"""

    SETUP = "setup"
    AWAKEN = "awaken"        # R-CR-315.1
    BEGIN = "begin"          # R-CR-315.2（开始时触发 + 得分步骤）
    CHANNEL = "channel"      # R-CR-315.3
    DRAW = "draw"            # R-CR-315.4
    MAIN = "main"            # R-CR-316
    ENDING = "ending"        # R-CR-317
    GAME_OVER = "game_over"


class TurnMode(str, Enum):
    """普通/法术对决（R-CR-308）。"""

    NORMAL = "normal"
    SHOWDOWN = "showdown"


class LinkState(str, Enum):
    """开环/闭环（R-CR-309/331）。"""

    OPEN = "open"
    CLOSED = "closed"


class Keyword(str, Enum):
    """关键词（R-CR-800..829）。MVP 骨架仅枚举；无文本骨架卡默认不带。"""

    ACCELERATE = "accelerate"   # 805 急速
    ACTION = "action"           # 806 迅捷
    ASSAULT = "assault"         # 807 强攻
    DEATHKNELL = "deathknell"   # 808 绝念
    DEFLECT = "deflect"         # 809 法盾
    GANKING = "ganking"         # 810 游走
    HIDDEN = "hidden"           # 811 待命
    LEGION = "legion"           # 812 鼓舞
    REACTION = "reaction"       # 813 反应
    SHIELD = "shield"           # 814 坚守
    TANK = "tank"               # 815 壁垒
    TEMPORARY = "temporary"     # 816 瞬息
    VISION = "vision"           # 817 预知
    AMBUSH = "ambush"           # 822 伏击
    BACKLINE = "backline"       # 826 后排


class DecisionKind(str, Enum):
    """决策点类型（docs/architecture.md §3）。"""

    MAIN_ACTION = "main_action"          # 自决行动（主阶段）
    REACTION_EXECUTE = "reaction_execute"  # FEPR 执行窗口（R-CR-338/339）
    SHOWDOWN_FOCUS = "showdown_focus"    # 对决焦点（R-CR-347）
    CHOOSE_TARGETS = "choose_targets"
    CHOOSE_LOCATION = "choose_location"
    CHOOSE_MODE = "choose_mode"
    ASSIGN_DAMAGE = "assign_damage"      # R-CR-465.2
    CHOOSE_BATTLEFIELD_NEXT = "choose_battlefield_next"  # 323.12/13 多场次选择
    MULLIGAN = "mulligan"                # R-CR-117
    ORDER_TRIGGERS = "order_triggers"    # R-CR-383.3.d（同玩家多触发排序）
    ORDER_REPLACEMENTS = "order_replacements"  # R-CR-372/373
    SCOUT_KEEP = "scout_keep"            # 洞察去留（R-CR-436；P1）


class ActionKind(str, Enum):
    """动作类型（docs/api_contract.md §6）。"""

    PLAY_CARD = "play_card"                  # R-CR-349
    ACTIVATE_ABILITY = "activate_ability"    # R-CR-401/377
    STD_MOVE = "std_move"                    # R-CR-144/447
    HIDE = "hide"                            # R-CR-421/811.1.b
    END_MAIN = "end_main"                    # R-CR-305/335
    EXECUTE_REACTION = "execute_reaction"    # R-CR-338（嵌套 play/activate 或 nothing）
    PASS = "pass"                            # R-CR-339/347
    RESOLVE_CHOICE = "resolve_choice"        # CHOOSE_* 统一回答
    ASSIGN_DAMAGE = "assign_damage"          # R-CR-465.2
    CONCEDE = "concede"                      # R-CR-650


class Termination(str, Enum):
    """终局原因（1v1 无平局；TRUNCATED 非规则终局，R-CR-196 之外）。"""

    SCORE = "score"          # R-CR-472/323.1
    EFFECT_WIN = "effect_win"  # R-CR-195
    CONCEDE = "concede"      # R-CR-649..652
    BURNOUT = "burnout"      # R-CR-431.3.c.1
    TRUNCATED = "truncated"
    ERROR = "error"


class EventType(str, Enum):
    """事件类型（docs/api_contract.md §7；字符串承载向后兼容新增）。"""

    SETUP = "SETUP"
    MULLIGAN = "MULLIGAN"
    PHASE_ENTER = "PHASE_ENTER"
    READY = "READY"
    CHANNEL = "CHANNEL"
    DRAW = "DRAW"
    BURNOUT = "BURNOUT"
    POOL_CLEAR = "POOL_CLEAR"
    PLAY_STEP = "PLAY_STEP"
    PAID = "PAID"
    FINALIZE = "FINALIZE"
    EXECUTE = "EXECUTE"
    PASS = "PASS"
    RESOLVE = "RESOLVE"
    TRIGGER_QUEUED = "TRIGGER_QUEUED"
    COUNTERED = "COUNTERED"
    MOVE = "MOVE"
    RECALL = "RECALL"
    CONTEST = "CONTEST"
    SHOWDOWN_START = "SHOWDOWN_START"
    SHOWDOWN_END = "SHOWDOWN_END"
    COMBAT_START = "COMBAT_START"
    COMBAT_DAMAGE_ASSIGNED = "COMBAT_DAMAGE_ASSIGNED"
    COMBAT_DAMAGE = "COMBAT_DAMAGE"
    COMBAT_END = "COMBAT_END"
    SCORE = "SCORE"
    WIN = "WIN"
    CLEANUP_START = "CLEANUP_START"
    CLEANUP_ITEM = "CLEANUP_ITEM"
    KILL = "KILL"
    DAMAGE = "DAMAGE"
    HEAL = "HEAL"
    BUFF = "BUFF"
    ATTACH = "ATTACH"
    DETACH = "DETACH"
    RETURN_TO_HAND = "RETURN_TO_HAND"
    DISCARD = "DISCARD"
    RECYCLE = "RECYCLE"
    BANISH = "BANISH"
    CONCEDE = "CONCEDE"
    END_TURN = "END_TURN"
    STUN = "STUN"
    EXHAUST = "EXHAUST"
    ERROR = "ERROR"


# ---- 卡面符号字面量（R-CR-135/163/164）。引擎内部用结构化表示，符号仅用于展示 ----
SYM_EXHAUST = "[E]"   # 休眠费用 377.2.a.1
SYM_MIGHT = "[M]"     # 战力 140.2
SYM_LINK = "[>]"      # 关键词-技能链接 800.4
SYM_ANY = "[A]"       # 任意特性 163.2.a
SYM_COLOR_ID = "[C]"  # 牌自身特性 163.2.b
SYM_ENERGY = "[1]"    # 1 点法力（示例）
