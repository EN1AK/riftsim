# 得分（467..472；MECH-SCORING）与终局（193..196）
from __future__ import annotations

from .enums import EventType
from .events import emit
from .state import BattlefieldState, GameState


def score_conquer(state: GameState, player: int, bf: BattlefieldState) -> None:
    """征服（466.5.d/467.1/469.1）：确立控制时、本回合尚未从该战场得分→+1 分（470 限）；
    终分限制（471.1.b）：仅以征服手段且当前分≥胜利分-1 时，
    须本回合已在每个战场得分，否则改为抽 1 张牌。
    征服时刻（确立控制）后触发「当我征服」式触发式技能登记入链（383.3；470/471.1.b 拦分不拦触发）。"""
    state.players[player].conquered_this_turn = True  # 383 条件面（UNL-019 类「本回合未征服」）
    _score_conquer_points(state, player, bf)
    from . import triggers

    triggers.fire(state, "conquer", player=player, battlefield_index=bf.index)


def _score_conquer_points(state: GameState, player: int, bf: BattlefieldState) -> None:
    p = state.players[player]
    marks = p.score_marks.setdefault(bf.uid, [])
    if state.turn_number in marks:
        emit(state, EventType.SCORE, rule_ids=["R-CR-470.1"],
             public={"player": player, "battlefield": bf.index, "kind": "conquer_blocked", "score": p.score})
        return
    if p.score >= state.meta.win_score - 1:
        every = all(state.turn_number in p.score_marks.get(b.uid, []) for b in state.battlefields)
        if not every:
            from .resources import draw

            emit(state, EventType.SCORE, rule_ids=["R-CR-471.1.b"],
                 public={"player": player, "kind": "final_point_forbidden", "score": p.score})
            draw(state, player, 1, rule="R-CR-471.1.b")
            return
    p.score += 1
    marks.append(state.turn_number)
    emit(state, EventType.SCORE, rule_ids=["R-CR-469.1", "R-CR-467.1", "R-CR-466.5.d"],
         public={"player": player, "battlefield": bf.index, "kind": "conquer", "score": p.score})
