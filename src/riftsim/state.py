# GameState 完整内部状态（docs/architecture.md §4；字段均有规则依据）。
# 提供 to_dict/from_dict 规范序列化（snapshot/replay 基础）。
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .enums import CardType, Domain, Keyword, Phase, Termination, Zone
from .objects import GameObject
from .rng import RngStreams


@dataclass
class PlayerState:
    seat: int
    hand: list[int] = field(default_factory=list)
    main_deck: list[int] = field(default_factory=list)      # 有序：list[0]=牌堆底，[-1]=顶
    rune_deck: list[int] = field(default_factory=list)
    trash: list[int] = field(default_factory=list)
    banish: list[int] = field(default_factory=list)
    hero_zone: list[int] = field(default_factory=list)
    legend_zone: list[int] = field(default_factory=list)
    aside: list[int] = field(default_factory=list)          # 搁置（Setup 调度）
    rune_energy: int = 0                                    # 法力（163.1）
    rune_power: dict[str, int] = field(default_factory=dict)  # 符能按特性（163.2）
    score: int = 0
    # 每战场得分回合标记（470：每战场每回合每玩家限 1 分）
    score_marks: dict[int, list[int]] = field(default_factory=dict)
    conquered_this_turn: bool = False                       # 本回合是否征服过（383 触发条件面，UNL-019 类）
    conceded: bool = False
    first_channel_extra: int = 0                            # 485 后手首回合补偿 1


@dataclass
class CombatContext:
    battlefield: int
    attacker: int
    defender: int
    step: int = 1                        # 1 对决 / 2 伤害 / 3 结算（R-CR-463）
    assign_side: int | None = None       # 当前分配方（进攻先，465.2）
    assigned: dict[int, int] = field(default_factory=dict)  # 目标 uid -> 伤害（当前侧累计）
    pool: int = 0                        # 当前侧伤害池（总战力）
    identities_cleared: bool = False


@dataclass
class BattlefieldState:
    index: int
    uid: int                    # 战场卡 uid
    controller: int | None = None
    contested: bool = False
    contested_by: int | None = None   # 争夺发起方（进攻方/焦点，345）
    showdown_pending: bool = False
    combat_pending: bool = False
    showdown_active: bool = False
    combat: CombatContext | None = None
    hidden_slot: list[int] = field(default_factory=list)   # ≤1（811）
    occupants: list[int] = field(default_factory=list)     # 单位等场上物 uid


@dataclass
class ChainItem:
    """结算链项目（R-CR-325..331）。status: pending(待处理) | finalized(已确认)。"""

    item_id: int
    kind: str                  # "card" | "ability" | "trigger" | "reflexive"
    source_uid: int            # 链上该对象 uid（卡牌本体/技能来源）
    controller: int
    status: str = "pending"
    choices: dict[str, Any] = field(default_factory=dict)   # 步骤 2 锁定选择（355）
    targets: list[int] = field(default_factory=list)
    total_cost: dict[str, Any] | None = None   # {"energy":int,"power":{D:int},"extras":[...]}（356）
    paid: bool = False
    origin: Zone | None = None
    ability: dict[str, Any] | None = None      # 技能描述（kind=ability/trigger）
    last_known: dict | None = None             # 绝念类最后状态（808.1.d.2/3）
    created_seq: int = 0                       # 入链序（337.1.b、触发排序 383.3.d.1）


@dataclass
class ContinuousMod:
    """持续效果挂点（P1 Layers 全量；M1 骨架：战力/关键词临时修正，3d/下场清）。"""

    target_uid: int
    might_add: int = 0
    keywords_add: tuple[str, ...] = ()
    duration: str = "turn"    # "turn"(317.2.d) | "perm"(至离场) | "while"(条件存续)
    source: str = "fixture"


@dataclass
class EffectRegistries:
    continuous: list[ContinuousMod] = field(default_factory=list)
    replacements: list[dict] = field(default_factory=list)   # P1（MECH-REPLACEMENT 挂点）
    delayed: list[dict] = field(default_factory=list)        # P1（MECH-DELAYED 挂点）


@dataclass
class GameMeta:
    match_id: str
    seed: int
    engine_version: str
    ruleset_version: str
    spec_hash: str
    card_pool_version: str
    win_score: int = 8           # R-CR-485
    config: dict[str, Any] = field(default_factory=dict)
    trace_level: str = "summary"
    max_steps: int = 5000


@dataclass
class GameState:
    meta: GameMeta
    turn_player: int = 0
    turn_number: int = 1
    phase: Phase = Phase.SETUP
    sub_step: str = ""
    priority: int | None = None        # 优先行动权（312）
    focus: int | None = None           # 焦点（313；对决中）
    showdown_bf: int | None = None     # 当前进行对决的战场 index
    mulligan_set: set[int] = field(default_factory=set)  # 已完成调度的玩家
    ended: bool = False
    winner: int | None = None
    termination: Termination | None = None
    players: tuple[PlayerState, ...] = field(default_factory=lambda: (PlayerState(0), PlayerState(1)))
    battlefields: list[BattlefieldState] = field(default_factory=list)
    base_occupants: list[list[int]] = field(default_factory=lambda: [[], []])
    chain: list[ChainItem] = field(default_factory=list)   # 空=链不存在（330）
    chain_seq: int = 0
    # def_id → CardDefinition 注册表（随快照序列化；reset 时由 config.decks 构建）
    card_registry: dict[str, Any] = field(default_factory=dict)
    current_request: dict | None = None   # DecisionRequest 序列化（actor/kind/options…）
    fepr_pass: list[int] = field(default_factory=list)   # FEPR 连续让过序列（339）
    sd_pass: list[int] = field(default_factory=list)     # 对决焦点连续让过序列（348）
    rng: RngStreams = field(default_factory=lambda: RngStreams.from_seed(0))
    effects: EffectRegistries = field(default_factory=EffectRegistries)
    objects: dict[int, GameObject] = field(default_factory=dict)
    next_uid: int = 1
    step_id: int = 0
    event_seq: int = 0
    invalid_action_count: int = 0
    cleanups_run: int = 0
    pending_events: list[dict] = field(default_factory=list)

    # ---------------- 便捷查询 ----------------
    def new_uid(self) -> int:
        uid = self.next_uid
        self.next_uid += 1
        return uid

    def obj(self, uid: int) -> GameObject:
        return self.objects[uid]

    def opponents(self, seat: int) -> int:
        return 1 - seat

    def chain_live(self) -> bool:
        """R-CR-331：结算链非空 → 闭环。"""
        return len(self.chain) > 0

    def showdown_live(self) -> bool:
        """R-CR-343：存在进行中的法术对决/战斗 → 法术对决状态。"""
        return self.showdown_bf is not None or any(
            b.combat is not None for b in self.battlefields
        )

    def player_objects(self, seat: int, *, board_only: bool = False) -> list[int]:
        out = []
        for uid, o in self.objects.items():
            if o.controller != seat:
                continue
            if board_only and o.zone not in (Zone.BASE, Zone.BATTLEFIELD):
                continue
            out.append(uid)
        return out

    # ---------------- 序列化 ----------------
    def to_dict(self) -> dict[str, Any]:
        def obj_dict(o: GameObject) -> dict[str, Any]:
            return {
                "uid": o.uid, "def_id": o.def_id, "owner": o.owner,
                "controller": o.controller, "zone": o.zone.value,
                "zone_owner": o.zone_owner, "battlefield": o.battlefield,
                "damage": o.damage, "exhausted": o.exhausted, "stunned": o.stunned,
                "face_down": o.face_down, "might_temp": o.might_temp, "buffs": o.buffs,
                "keywords_extra": {k.value: v for k, v in o.keywords_extra.items()},
                "attachments": list(o.attachments), "attached_to": o.attached_to,
                "counters": dict(o.counters), "entered_turn": o.entered_turn,
                "last_known": o.last_known,
            }

        def player_dict(p: PlayerState) -> dict[str, Any]:
            return {
                "seat": p.seat, "hand": list(p.hand), "main_deck": list(p.main_deck),
                "rune_deck": list(p.rune_deck), "trash": list(p.trash),
                "banish": list(p.banish), "hero_zone": list(p.hero_zone),
                "legend_zone": list(p.legend_zone), "aside": list(p.aside),
                "rune_energy": p.rune_energy, "rune_power": dict(p.rune_power),
                "score": p.score,
                "score_marks": {str(k): sorted(v) for k, v in p.score_marks.items()},
                "conquered_this_turn": p.conquered_this_turn,
                "conceded": p.conceded, "first_channel_extra": p.first_channel_extra,
            }

        def bf_dict(b: BattlefieldState) -> dict[str, Any]:
            combat = None
            if b.combat:
                c = b.combat
                combat = {
                    "battlefield": c.battlefield, "attacker": c.attacker,
                    "defender": c.defender, "step": c.step,
                    "assign_side": c.assign_side, "assigned": {str(k): v for k, v in c.assigned.items()},
                    "pool": c.pool, "identities_cleared": c.identities_cleared,
                }
            return {
                "index": b.index, "uid": b.uid, "controller": b.controller,
                "contested": b.contested, "contested_by": b.contested_by,
                "showdown_pending": b.showdown_pending, "combat_pending": b.combat_pending,
                "showdown_active": b.showdown_active, "combat": combat,
                "hidden_slot": list(b.hidden_slot), "occupants": list(b.occupants),
            }

        def item_dict(it: ChainItem) -> dict[str, Any]:
            return {
                "item_id": it.item_id, "kind": it.kind, "source_uid": it.source_uid,
                "controller": it.controller, "status": it.status,
                "choices": it.choices, "targets": list(it.targets),
                "total_cost": it.total_cost, "paid": it.paid,
                "origin": it.origin.value if it.origin else None,
                "ability": it.ability, "last_known": it.last_known,
                "created_seq": it.created_seq,
            }

        def def_dict(d: Any) -> dict[str, Any]:
            return {
                "def_id": d.def_id, "name": d.name,
                "card_types": sorted(t.value for t in d.card_types),
                "domains": sorted(x.value for x in d.domains),
                "cost_energy": d.cost_energy,
                "cost_power": [x.value for x in d.cost_power],
                "might": d.might, "might_bonus": d.might_bonus,
                "tags": sorted(d.tags), "hero_tag": d.hero_tag,
                "keywords": sorted(k.value for k in d.keywords),
                "keyword_values": dict(d.keyword_values),
                "pool": d.pool,
                "abilities": [
                    {
                        "ability_id": a.ability_id, "kind": a.kind, "timing": a.timing,
                        "cost_exhaust_self": a.cost_exhaust_self,
                        "cost_recycle_self": a.cost_recycle_self,
                        "grant_energy": a.grant_energy,
                        "grant_power_self_domain": a.grant_power_self_domain,
                        "immediate": a.immediate, "rules_ref": list(a.rules_ref),
                        "damage": a.damage, "target_scope": a.target_scope,
                        "grant_power_domain": a.grant_power_domain,
                        "cost_symbols": list(a.cost_symbols),
                        "draw_count": a.draw_count,
                        "pump_value": a.pump_value,
                        "resolve_fn": a.resolve_fn,
                        "trigger": a.trigger,
                        "payload": a.payload,
                        "value": a.value,
                        "condition": a.condition,
                    }
                    for a in d.abilities
                ],
            }

        return {
            "meta": {
                "match_id": self.meta.match_id, "seed": self.meta.seed,
                "engine_version": self.meta.engine_version,
                "ruleset_version": self.meta.ruleset_version,
                "spec_hash": self.meta.spec_hash,
                "card_pool_version": self.meta.card_pool_version,
                "win_score": self.meta.win_score, "config": self.meta.config,
                "trace_level": self.meta.trace_level, "max_steps": self.meta.max_steps,
            },
            "turn_player": self.turn_player, "turn_number": self.turn_number,
            "phase": self.phase.value, "sub_step": self.sub_step,
            "priority": self.priority, "focus": self.focus,
            "showdown_bf": self.showdown_bf, "mulligan_set": sorted(self.mulligan_set),
            "ended": self.ended, "winner": self.winner,
            "termination": self.termination.value if self.termination else None,
            "players": [player_dict(p) for p in self.players],
            "battlefields": [bf_dict(b) for b in self.battlefields],
            "base_occupants": [list(x) for x in self.base_occupants],
            "chain": [item_dict(it) for it in self.chain],
            "chain_seq": self.chain_seq,
            "current_request": self.current_request,
            "fepr_pass": list(self.fepr_pass),
            "sd_pass": list(self.sd_pass),
            "effects": {
                "continuous": [
                    {"target_uid": m.target_uid, "might_add": m.might_add,
                     "keywords_add": list(m.keywords_add), "duration": m.duration,
                     "source": m.source}
                    for m in self.effects.continuous
                ],
                "replacements": self.effects.replacements,
                "delayed": self.effects.delayed,
            },
            "objects": {str(k): obj_dict(v) for k, v in sorted(self.objects.items())},
            "next_uid": self.next_uid, "step_id": self.step_id,
            "event_seq": self.event_seq, "invalid_action_count": self.invalid_action_count,
            "cleanups_run": self.cleanups_run,
            "rng": self.rng.to_json(),
            "card_registry": {k: def_dict(v) for k, v in self.card_registry.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GameState":
        m = data["meta"]
        st = cls(
            meta=GameMeta(
                match_id=m["match_id"], seed=m["seed"],
                engine_version=m["engine_version"], ruleset_version=m["ruleset_version"],
                spec_hash=m["spec_hash"], card_pool_version=m["card_pool_version"],
                win_score=m["win_score"], config=m["config"],
                trace_level=m["trace_level"], max_steps=m["max_steps"],
            )
        )
        st.turn_player = data["turn_player"]
        st.turn_number = data["turn_number"]
        st.phase = Phase(data["phase"])
        st.sub_step = data["sub_step"]
        st.priority = data["priority"]
        st.focus = data["focus"]
        st.showdown_bf = data["showdown_bf"]
        st.mulligan_set = set(data["mulligan_set"])
        st.ended = data["ended"]
        st.winner = data["winner"]
        st.termination = Termination(data["termination"]) if data["termination"] else None
        st.players = tuple(
            PlayerState(
                seat=p["seat"], hand=list(p["hand"]), main_deck=list(p["main_deck"]),
                rune_deck=list(p["rune_deck"]), trash=list(p["trash"]),
                banish=list(p["banish"]), hero_zone=list(p["hero_zone"]),
                legend_zone=list(p["legend_zone"]), aside=list(p["aside"]),
                rune_energy=p["rune_energy"], rune_power=dict(p["rune_power"]),
                score=p["score"],
                score_marks={int(k): set(v) for k, v in p["score_marks"].items()},
                conquered_this_turn=p.get("conquered_this_turn", False),
                conceded=p["conceded"], first_channel_extra=p["first_channel_extra"],
            )
            for p in data["players"]
        )
        bfs = []
        for b in data["battlefields"]:
            combat = None
            if b["combat"]:
                c = b["combat"]
                combat = CombatContext(
                    battlefield=c["battlefield"], attacker=c["attacker"],
                    defender=c["defender"], step=c["step"],
                    assign_side=c["assign_side"],
                    assigned={int(k): v for k, v in c["assigned"].items()},
                    pool=c["pool"], identities_cleared=c["identities_cleared"],
                )
            bfs.append(BattlefieldState(
                index=b["index"], uid=b["uid"], controller=b["controller"],
                contested=b["contested"], contested_by=b["contested_by"],
                showdown_pending=b["showdown_pending"], combat_pending=b["combat_pending"],
                showdown_active=b["showdown_active"], combat=combat,
                hidden_slot=list(b["hidden_slot"]), occupants=list(b["occupants"]),
            ))
        st.battlefields = bfs
        st.base_occupants = [list(x) for x in data["base_occupants"]]
        st.chain = [
            ChainItem(
                item_id=it["item_id"], kind=it["kind"], source_uid=it["source_uid"],
                controller=it["controller"], status=it["status"],
                choices=it["choices"], targets=list(it["targets"]),
                total_cost=it["total_cost"], paid=it["paid"],
                origin=Zone(it["origin"]) if it["origin"] else None,
                ability=it["ability"], last_known=it["last_known"],
                created_seq=it["created_seq"],
            )
            for it in data["chain"]
        ]
        st.chain_seq = data["chain_seq"]
        st.current_request = data["current_request"]
        st.fepr_pass = list(data.get("fepr_pass", []))
        st.sd_pass = list(data.get("sd_pass", []))
        st.effects = EffectRegistries(
            continuous=[
                ContinuousMod(
                    target_uid=c["target_uid"], might_add=c["might_add"],
                    keywords_add=tuple(c["keywords_add"]), duration=c["duration"],
                    source=c["source"],
                )
                for c in data["effects"]["continuous"]
            ],
            replacements=data["effects"]["replacements"],
            delayed=data["effects"]["delayed"],
        )
        st.objects = {
            int(k): GameObject(
                uid=v["uid"], def_id=v["def_id"], owner=v["owner"],
                controller=v["controller"], zone=Zone(v["zone"]),
                zone_owner=v["zone_owner"], battlefield=v["battlefield"],
                damage=v["damage"], exhausted=v["exhausted"], stunned=v["stunned"],
                face_down=v["face_down"], might_temp=v["might_temp"], buffs=v["buffs"],
                keywords_extra={Keyword(kk): vv for kk, vv in v["keywords_extra"].items()},
                attachments=list(v["attachments"]), attached_to=v["attached_to"],
                counters=dict(v["counters"]), entered_turn=v["entered_turn"],
                last_known=v["last_known"],
            )
            for k, v in data["objects"].items()
        }
        st.next_uid = data["next_uid"]
        st.step_id = data["step_id"]
        st.event_seq = data["event_seq"]
        st.invalid_action_count = data["invalid_action_count"]
        st.cleanups_run = data["cleanups_run"]
        st.rng = RngStreams.from_json(data["rng"])
        from .cards import AbilityDef, CardDefinition

        st.card_registry = {
            k: CardDefinition(
                def_id=v["def_id"], name=v["name"],
                card_types=frozenset(CardType(t) for t in v["card_types"]),
                domains=frozenset(Domain(x) for x in v["domains"]),
                cost_energy=v["cost_energy"],
                cost_power=tuple(Domain(x) for x in v["cost_power"]),
                might=v["might"], might_bonus=v["might_bonus"],
                tags=frozenset(v["tags"]), hero_tag=v["hero_tag"],
                keywords=frozenset(Keyword(kw) for kw in v["keywords"]),
                keyword_values=dict(v.get("keyword_values", {})),
                pool=v["pool"],
                abilities=tuple(
                    AbilityDef(
                        ability_id=a["ability_id"], kind=a["kind"], timing=a["timing"],
                        cost_exhaust_self=a["cost_exhaust_self"],
                        cost_recycle_self=a["cost_recycle_self"],
                        grant_energy=a["grant_energy"],
                        grant_power_self_domain=a["grant_power_self_domain"],
                        immediate=a["immediate"], rules_ref=tuple(a["rules_ref"]),
                        damage=a.get("damage", 0), target_scope=a.get("target_scope", ""),
                        grant_power_domain=a.get("grant_power_domain", ""),
                        cost_symbols=tuple(a.get("cost_symbols", ())),
                        draw_count=a.get("draw_count", 0),
                        pump_value=a.get("pump_value", 0),
                        resolve_fn=a.get("resolve_fn", ""),
                        trigger=a.get("trigger", ""),
                        payload=a.get("payload", ""),
                        value=int(a.get("value", 0)),
                        condition=a.get("condition", ""),
                    )
                    for a in v["abilities"]
                ),
            )
            for k, v in data.get("card_registry", {}).items()
        }
        return st
