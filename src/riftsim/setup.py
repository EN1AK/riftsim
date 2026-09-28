# reset() 实现（R-CR-110..118 Setup 全流程；T-0007/0008/0010/0011/0013）
from __future__ import annotations

import hashlib
import itertools
from pathlib import Path

from .actions import DecisionRequest
from .cards import DeckList, make_skeleton_deck
from .config import GameConfig
from .decks import assert_deck
from .enums import DecisionKind, EventType, Phase, Zone
from .events import emit
from .objects import GameObject
from .rng import RngStreams, STREAM_BATTLEFIELD_PICK, STREAM_EFFECT, STREAM_SHUFFLE_MAIN, STREAM_SHUFFLE_RUNE
from .state import BattlefieldState, GameMeta, GameState
from .version import CARD_POOL_VERSION, ENGINE_VERSION, RULESET_VERSION


def spec_hash() -> str:
    p = Path("spec/rules_spec.yaml")
    if p.exists():
        return hashlib.sha256(p.read_bytes()).hexdigest()[:12]
    return "unspec"


def _new_match_id(seed: int, decks: tuple[DeckList, DeckList]) -> str:
    """match_id 确定性派生（T-0013/T-0132：同 seed 完全同构；runner 可覆盖为运行 id）。"""
    raw = f"{seed}|{'/'.join(d.deck_id or '?' for d in decks)}"
    return "m-" + hashlib.sha256(raw.encode()).hexdigest()[:12]


def reset(seed: int, config: GameConfig | None = None) -> GameState:
    if config is None:
        config = GameConfig(decks=(make_skeleton_deck("A", "hero-a"), make_skeleton_deck("B", "hero-b")))
    decks = config.decks
    for d in decks:
        assert_deck(d, mode=config.mode)

    # def 注册表（def_id→CardDefinition；含双方卡组全部 def）
    registry: dict = {}
    for d in decks:
        for c in itertools.chain([d.legend, d.chosen_hero], d.main_deck, d.rune_deck, d.battlefields):
            registry[c.def_id] = c

    state = GameState(
        meta=GameMeta(
            match_id=config.match_id or _new_match_id(seed, decks),
            seed=seed,
            engine_version=ENGINE_VERSION,
            ruleset_version=RULESET_VERSION,
            spec_hash=spec_hash(),
            card_pool_version=CARD_POOL_VERSION,
            win_score=config.win_score,
            config={"mode": config.mode, "decks": [d.deck_id or f"deck{i}" for i, d in enumerate(decks)],
                    "max_steps": config.max_steps},
            trace_level=config.trace_level,
            max_steps=config.max_steps,
        ),
        rng=RngStreams.from_seed(seed),
        card_registry=registry,
    )

    # ---- 111-114：对象实例化与落位 ----
    for seat, deck in enumerate(decks):
        # 传奇→传奇区（111）；选定英雄→英雄区（112）
        legend_uid = _spawn(state, deck.legend.def_id, seat, Zone.LEGEND_ZONE)
        state.players[seat].legend_zone.append(legend_uid)
        hero_uid = _spawn(state, deck.chosen_hero.def_id, seat, Zone.HERO_ZONE)
        state.players[seat].hero_zone.append(hero_uid)
        # 主牌堆（未洗先入区，114 再洗）
        for c in deck.main_deck:
            uid = _spawn(state, c.def_id, seat, Zone.MAIN_DECK)
            state.players[seat].main_deck.append(uid)
        for c in deck.rune_deck:
            uid = _spawn(state, c.def_id, seat, Zone.RUNE_DECK)
            state.players[seat].rune_deck.append(uid)
        # 113：战场搁置 → 485 各选 1
        idx = state.rng.randrange(STREAM_BATTLEFIELD_PICK, len(deck.battlefields))
        chosen = deck.battlefields[idx]
        for i, bf_def in enumerate(deck.battlefields):
            if i == idx:
                continue
            _spawn(state, bf_def.def_id, seat, Zone.ASIDE)
        bf_uid = _spawn(state, chosen.def_id, seat, Zone.BATTLEFIELD)
        state.battlefields.append(BattlefieldState(index=len(state.battlefields), uid=bf_uid))

    # 114 洗牌（双堆，各玩家独立）
    for seat in (0, 1):
        state.rng.shuffle(STREAM_SHUFFLE_MAIN, state.players[seat].main_deck)
        state.rng.shuffle(STREAM_SHUFFLE_RUNE, state.players[seat].rune_deck)

    # 115 回合顺序随机；后手补偿（485）
    first = state.rng.randrange(STREAM_EFFECT, 2)
    state.turn_player = first
    state.players[1 - first].first_channel_extra = 1
    state.meta.config["first_player"] = first

    # 116 各抽 4（不发生燃尽的路径；牌堆 36≥4）
    for seat in (0, 1):
        for _ in range(4):
            uid = state.players[seat].main_deck.pop()
            state.players[seat].hand.append(uid)
            o = state.obj(uid)
            o.zone, o.zone_owner = Zone.HAND, seat

    state.phase = Phase.SETUP
    emit(state, EventType.SETUP, rule_ids=["R-CR-110", "R-CR-111", "R-CR-112", "R-CR-113", "R-CR-114", "R-CR-115", "R-CR-116"],
         public={"first_player": first, "battlefields": [b.uid for b in state.battlefields]})

    # 117 调度：按回合序逐个请求
    state.current_request = DecisionRequest(
        DecisionKind.MULLIGAN, first, options={"max_set_aside": 2}
    ).to_dict()
    return state


def _spawn(state: GameState, def_id: str, seat: int, zone: Zone) -> int:
    uid = state.new_uid()
    o = GameObject(
        uid=uid, def_id=def_id, owner=seat, controller=seat,
        zone=zone, zone_owner=seat if zone not in (Zone.BATTLEFIELD,) else None,
        battlefield=None,
        entered_turn=0,
    )
    state.objects[uid] = o
    return uid
