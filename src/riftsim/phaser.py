# 回合阶段推进（314..317；MECH-START-OF-TURN/MAIN-PHASE/ENDING-PHASE）
from __future__ import annotations

from .enums import EventType, Phase
from .events import emit
from .resources import channel, clear_all_pools, draw, heal
from .state import GameState


def start_turn(state: GameState) -> None:
    """回合开始（315）：唤醒→开始阶段（触发挂点+据守计分）→召出→抽牌→主阶段入口。"""
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

    # 315.2 开始阶段：开始时触发（骨架池无触发——collect_begin_triggers 挂点）→计分步骤
    state.phase = Phase.BEGIN
    emit(state, EventType.PHASE_ENTER, rule_ids=["R-CR-315.2"], public={"turn_player": seat, "phase": "begin"})
    score_hold(state, seat)

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
    """据守（315.2+469.2）：控制的每个战场 +1 分（每战场每回合限 1 分 470）。"""
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


def end_turn(state: GameState) -> None:
    """回合结束阶段（317）：结束时触发（挂点）→特殊清理（3c 治疗/3d 失效/3e 清池）→移交。"""
    seat = state.turn_player
    state.phase = Phase.ENDING
    state.priority = None
    emit(state, EventType.PHASE_ENTER, rule_ids=["R-CR-317.2"], public={"turn_player": seat, "phase": "ending"})
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
    # 移交（306）
    state.turn_player = 1 - state.turn_player
    state.turn_number += 1
    state.phase = Phase.AWAKEN


def start_next_turn(state: GameState) -> None:
    start_turn(state)
