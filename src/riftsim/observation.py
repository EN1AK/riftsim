# Observation 构造与私有过滤（docs/api_contract.md §3；T-0130：对手私有内容零泄漏）
from __future__ import annotations

from typing import Any

from .enums import CardType, DecisionKind, LinkState, Phase, TurnMode, Zone
from .version import OBS_SCHEMA_VERSION
from .state import GameState


def turn_state(state: GameState) -> dict:
    """四态派生（R-CR-307..310）：闭环=链非空（331）；对决态=对决/战斗进行中（343）。"""
    link = LinkState.CLOSED if state.chain_live() else LinkState.OPEN
    mode = TurnMode.SHOWDOWN if state.showdown_live() else TurnMode.NORMAL
    return {"mode": mode.value, "link": link.value}


def _pub_obj(state: GameState, uid: int, viewer: int) -> dict:
    """公开对象视图。非公开内容绝不进入（CardType/def 详情仅公开对象与本玩家私有对象）。"""
    o = state.obj(uid)
    d = state.card_registry[o.def_id]
    return {
        "uid": uid,
        "def_id": o.def_id,
        "name": d.name,
        "types": sorted(t.value for t in d.card_types),
        "owner": o.owner,
        "controller": o.controller,
        "might": _might_view(state, uid),
        "damage": o.damage,
        "exhausted": o.exhausted,
        "stunned": o.stunned,
        "buffs": o.buffs,
        "keywords": sorted({k.value for k in d.keywords} | set(o.keywords_extra.keys())),
        "attached_to": o.attached_to,
        "attachments": list(o.attachments),
        "might_temp": o.might_temp,
    }


def _might_view(state: GameState, uid: int) -> int | None:
    from .resources import effective_might

    d = state.card_registry[state.obj(uid).def_id]
    if d.might is None:
        return None
    return effective_might(state, uid)


def observe(state: GameState, player: int) -> dict[str, Any]:
    me, opp = state.players[player], state.players[1 - player]
    ts = turn_state(state)

    board = []
    for bf in state.battlefields:
        bf_view = {
            "index": bf.index,
            "battlefield_uid": bf.uid,
            "battlefield_def": state.obj(bf.uid).def_id,
            "controller": bf.controller,
            "contested": bf.contested,
            "showdown_active": bf.showdown_active,
            "combat_active": bf.combat is not None,
            "occupants": [_pub_obj(state, u, player) for u in bf.occupants],
            # 待命位：存在性与归属公开（107.3.f）；内容仅控制者可见（811.6.a）
            "hidden_slot": [
                {"controller": state.obj(u).controller, "owner": state.obj(u).owner,
                 "content": _pub_obj(state, u, player) if state.obj(u).controller == player else None}
                for u in bf.hidden_slot
            ],
        }
        board.append(bf_view)

    bases = []
    for seat in (0, 1):
        bases.append([
            _pub_obj(state, u, player) for u in state.base_occupants[seat]
            if not state.obj(u).face_down or state.obj(u).controller == player
        ])
        # 基地公开信息（107.1.d）；face_down 理论上不出现于此（仅待命）——防御式过滤

    hand_view = [
        {
            "uid": u,
            "def_id": state.obj(u).def_id,
            "name": state.card_registry[state.obj(u).def_id].name,
            "cost_energy": state.card_registry[state.obj(u).def_id].cost_energy,
            "cost_power": [x.value for x in state.card_registry[state.obj(u).def_id].cost_power],
            "types": sorted(t.value for t in state.card_registry[state.obj(u).def_id].card_types),
            "might": state.card_registry[state.obj(u).def_id].might,
            "keywords": sorted(k.value for k in state.card_registry[state.obj(u).def_id].keywords),
        }
        for u in me.hand
    ]
    hidden_self = [
        _pub_obj(state, u, player)
        for bf in state.battlefields for u in bf.hidden_slot
        if state.obj(u).controller == player
    ]

    # 合法动作 id 列表由 engine.legal_actions 在 runner/adapter 层填充；观察内嵌请求描述
    req_view = None
    if state.current_request:
        req_view = dict(state.current_request)
        # 请求参数过滤：非请求方不得看到洞察牌顶 uid（436.1 私密查看；隐藏信息隔离）
        from .enums import DecisionKind

        opts = dict(req_view.get("options") or {})
        if req_view.get("kind") == DecisionKind.SCOUT_KEEP.value and req_view.get("player") != player:
            opts.pop("uids", None)
            req_view["options"] = opts
        if (req_view.get("kind") == DecisionKind.CHOOSE_MODE.value
                and opts.get("reason") == "trigger_discard"
                and req_view.get("player") != player):
            opts.pop("choices", None)  # 383 弃抽续段：手牌 uid 选择面仅请求方可见（128）
            req_view["options"] = opts

    return {
        "schema": OBS_SCHEMA_VERSION,
        "viewer": player,
        "match_id": state.meta.match_id,
        "step_id": state.step_id,
        "turn": {
            "turn_player": state.turn_player,
            "turn_number": state.turn_number,
            "phase": state.phase.value,
            "sub_step": state.sub_step,
        },
        "turn_state": ts,
        "ended": state.ended,
        "winner": state.winner,
        "termination": state.termination.value if state.termination else None,
        "priority": state.priority,
        "focus": state.focus,
        "showdown_bf": state.showdown_bf,
        "board": board,
        "bases": bases,
        "self": {
            "seat": player,
            "hand": hand_view,
            "hand_count": len(me.hand),
            "main_deck_count": len(me.main_deck),
            "rune_deck_count": len(me.rune_deck),
            "trash": [_brief(state, u) for u in me.trash],        # 公开监督（zones 见 108 公开）
            "banish": [_brief(state, u) for u in me.banish],
            "hidden": hidden_self,
            "rune_energy": me.rune_energy,          # OPEN-5：暂定公开
            "rune_power": dict(me.rune_power),
            "score": me.score,
            "score_marks": {str(k): sorted(v) for k, v in me.score_marks.items()},
            "hero_zone": [_brief(state, u) for u in me.hero_zone],
            "legend_zone": [_brief(state, u) for u in me.legend_zone],
        },
        "opponent": {
            "seat": 1 - player,
            "hand_count": len(opp.hand),           # 仅数量（128）
            "main_deck_count": len(opp.main_deck),
            "rune_deck_count": len(opp.rune_deck),
            "trash": [_brief(state, u) for u in opp.trash],
            "banish": [_brief(state, u) for u in opp.banish],
            "rune_energy": opp.rune_energy,
            "rune_power": dict(opp.rune_power),
            "score": opp.score,
            "hero_zone": [_brief(state, u) for u in opp.hero_zone],
            "legend_zone": [_brief(state, u) for u in opp.legend_zone],
        },
        "chain": [
            {  # 链上项目公开信息（108 子条款）
                "item_id": it.item_id, "kind": it.kind, "controller": it.controller,
                "def_id": state.obj(it.source_uid).def_id if it.source_uid in state.objects else None,
                "status": it.status, "targets": list(it.targets),
            }
            for it in state.chain
        ],
        "request": req_view,
    }


def _brief(state: GameState, uid: int) -> dict:
    o = state.obj(uid)
    d = state.card_registry[o.def_id]
    return {"uid": uid, "def_id": o.def_id, "name": d.name,
            "types": sorted(t.value for t in d.card_types)}
