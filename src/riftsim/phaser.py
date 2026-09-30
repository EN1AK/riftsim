# 回合阶段推进（314..317；MECH-START-OF-TURN/MAIN-PHASE/ENDING-PHASE）
from __future__ import annotations

from .enums import EventType, Keyword, Phase
from .events import emit
from .resources import channel, clear_all_pools, draw, heal
from .state import ChainItem, GameState


def start_turn(state: GameState) -> None:
    """回合开始（315）：唤醒→开始阶段（816 瞬息触发入链+据守计分）→召出→抽牌→主阶段入口。"""
    seat = state.turn_player
    emit(state, EventType.PHASE_ENTER, rule_ids=["R-CR-315.1"],
         public={"turn_player": seat, "turn": state.turn_number, "phase": "awaken"})
    # 315.1.b 唤醒：其控制的所有能活跃的物体
    p = state.players[seat]
    readied = []
    for uid in state.player_objects(seat, board_only=True):
        o = state.obj(uid)
        if o.exhausted:
            o.exhausted = False
            readied.append(uid)
    state.phase = Phase.AWAKEN
    if readied:
        emit(state, EventType.READY, rule_ids=["R-CR-315.1.b"], public={"player": seat, "uids": readied})

    # 315.2 开始阶段：开始触发（816 瞬息：控制者开始阶段开始 816.1.c，计分前摧毁 816.1.b）
    state.phase = Phase.BEGIN
    emit(state, EventType.PHASE_ENTER, rule_ids=["R-CR-315.2"], public={"turn_player": seat, "phase": "begin"})
    from .playing import keywords_of

    temporaries = [
        uid for uid in state.player_objects(seat, board_only=True)
        if Keyword.TEMPORARY in keywords_of(state, uid) and state.obj(uid).attached_to is None
        # 贴附卡规则文本未激活不触发（722.2 语义）
    ]
    if temporaries:
        from . import chain_sys

        for uid in temporaries:  # 多触发排序（383.3.d）按 uid 确定序入链（挂点：玩家自选序）
            chain_sys.push(state, ChainItem(
                item_id=state.new_uid(), kind="trigger", source_uid=uid, controller=seat,
                ability={"kind": "temporary_destroy", "origin": "trigger",
                         "rules_ref": ["R-CR-816.1.b", "R-CR-816.1.c"]},
                origin=state.obj(uid).zone,
            ))
        state.sub_step = "begin_after_triggers"  # 链结算干净后由 engine.advance 续段
        return
    begin_after_triggers(state)


def begin_after_triggers(state: GameState) -> None:
    """开始阶段续段（315.2 计分→据守触发链→315.3 召出→315.4 抽牌→316 主阶段入口）。"""

    seat = state.turn_player
    score_hold(state, seat)
    if state.chain_live():
        # 据守计分触发（383.3）入链 → 链结算干净后由 engine.advance 续段
        state.sub_step = "begin_after_hold_triggers"
        return
    begin_after_hold_triggers(state)


def begin_after_hold_triggers(state: GameState) -> None:
    """315.3 召出→315.4 抽牌→316 主阶段入口（据守触发链后或无触发直进）。"""
    seat = state.turn_player
    p = state.players[seat]

    # 315.3 召出：2 + 后手首回合补偿（485）
    state.phase = Phase.CHANNEL
    n = 2 + p.first_channel_extra
    p.first_channel_extra = 0
    emit(state, EventType.PHASE_ENTER, rule_ids=["R-CR-315.3"], public={"turn_player": seat, "phase": "channel", "count": n})
    channel(state, seat, n)

    # 315.4 抽牌（空堆→燃尽 315.4.b.1/431）
    state.phase = Phase.DRAW
    emit(state, EventType.PHASE_ENTER, rule_ids=["R-CR-315.4"], public={"turn_player": seat, "phase": "draw"})
    draw(state, seat, 1, rule="R-CR-315.4")

    # 316 主阶段：清空所有玩家符文池（316.3）→开始时触发（挂点）→行动窗口
    state.phase = Phase.MAIN
    state.sub_step = ""
    emit(state, EventType.PHASE_ENTER, rule_ids=["R-CR-316.1"], public={"turn_player": seat, "phase": "main"})
    clear_all_pools(state, rule="R-CR-316.3")
    state.priority = seat
    from .actions import DecisionRequest
    from .enums import DecisionKind

    state.current_request = DecisionRequest(DecisionKind.MAIN_ACTION, seat).to_dict()


def score_hold(state: GameState, seat: int) -> None:
    """据守（315.2+469.2）：控制的每个战场 +1 分（每战场每回合限 1 分 470）；
    每次据守得分后触发「当我据守」式触发式技能登记入链（383.3）。"""
    from . import triggers

    for bf in state.battlefields:
        if bf.controller != seat:
            continue
        p = state.players[seat]
        marks = p.score_marks.setdefault(bf.uid, [])
        if state.turn_number in marks:
            continue  # 470：本回合已从该战场得分
        p.score += 1
        marks.append(state.turn_number)
        emit(state, EventType.SCORE, rule_ids=["R-CR-315.2", "R-CR-469.2", "R-CR-470"],
             public={"player": seat, "battlefield": bf.index, "kind": "hold", "score": p.score})
        triggers.fire(state, "hold", player=seat, battlefield_index=bf.index)


def end_turn(state: GameState) -> None:
    """回合结束阶段（317）：结束时触发入链（383.3+317.2 触发窗）→链结算→特殊清理→移交。
    时序自洽点：触发链结算后 state-based 清理（advance 首步）先于 3c 治疗——
    UNL-019 类「自伤 4」对 might≤4 宿主会先经 323.5 摧毁，存活者再由 3c 移除伤害。"""
    seat = state.turn_player
    state.phase = Phase.ENDING
    state.priority = None
    emit(state, EventType.PHASE_ENTER, rule_ids=["R-CR-317.2"], public={"turn_player": seat, "phase": "ending"})
    from . import triggers

    triggers.fire(state, "end_of_turn_own", player=seat)  # 全场宿主扫描（装备贴附在场即可）
    if state.chain_live():
        state.sub_step = "end_after_triggers"  # 结束触发链结算干净后由 engine.advance 续段
        return
    end_after_triggers(state)


def end_after_triggers(state: GameState) -> None:
    """317 结束阶段续段：特殊清理（3c 治疗/3d 失效/3e 清池）→移交（306）；conquered 条件面清除。"""
    seat = state.turn_player
    # 特殊清理 3c：移除所有单位伤害（317.2.d → 324 细则）
    for uid in list(state.objects.keys()):
        o = state.objects.get(uid)
        if o and o.damage > 0:
            heal(state, uid, o.damage, rule="R-CR-317.2.d")
    # 特殊清理 3d：回合内效果失效（317.2.d：临时战力/回合关键词/眩晕 423）
    for uid in list(state.objects.keys()):
        o = state.objects.get(uid)
        if o is None:
            continue
        o.might_temp = 0
        o.stunned = False
        for kw in [k for k, dur in o.keywords_extra.items() if dur == "turn"]:
            del o.keywords_extra[kw]
    state.effects.continuous = [m for m in state.effects.continuous if m.duration != "turn"]
    # 特殊清理 3e：清空符文池（317.2.d）
    clear_all_pools(state, rule="R-CR-317.2.d")
    emit(state, EventType.END_TURN, rule_ids=["R-CR-306"], public={"turn_player": seat, "turn": state.turn_number})
    # 移交（306）；本回合征服条件面随回合结束清除；下回合启动驱动点（advance 续 pending_start）
    state.players[seat].conquered_this_turn = False
    state.turn_player = 1 - state.turn_player
    state.turn_number += 1
    state.phase = Phase.AWAKEN
    state.sub_step = "pending_start"


def start_next_turn(state: GameState) -> None:
    start_turn(state)
