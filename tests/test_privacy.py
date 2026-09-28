# 隐私/观察过滤（T-0011/0018/0019/0130）
from riftsim import engine
from riftsim.enums import CardType, Keyword, Zone
from tests.helpers import fresh, give_hand, spawn_card


def _collect_uids(view) -> set[int]:
    """遍历观察 JSON 收集出现的 uid（递归）。"""
    out = set()

    def rec(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ("uid", "attached_to", "battlefield_uid") and isinstance(v, int):
                    out.add(v)
                rec(v)
        elif isinstance(x, list):
            for i in x:
                rec(i)

    rec(view)
    return out


def test_t0011_deck_order_secret():
    st, first = fresh()
    # 对手牌堆内容不可见：界面只暴露数量（且与内部一致）；内容键不存在
    for viewer in (0, 1):
        obs = engine.observe(st, viewer)
        opp = 1 - viewer
        assert obs["opponent"]["main_deck_count"] == len(st.players[opp].main_deck)
        assert obs["opponent"]["hand_count"] == len(st.players[opp].hand)
        assert "main_deck" not in obs["opponent"]
        assert "hand" not in obs["opponent"]


def test_t0018_three_levels():
    st, first = fresh()
    obs = engine.observe(st, 1 - first)
    # 公开：战场对象详情可见；私有：对手手牌内容不可见（含 def_id/name 字段均不出现）
    opp_hand_private_uids = set(st.players[first].hand)
    leaked = _collect_uids(obs) & opp_hand_private_uids
    assert leaked == set()
    # 自身手牌可见详情
    assert all("def_id" in c for c in obs["self"]["hand"])


def test_t0013_observe_self_vs_opponent_hand():
    st, first = fresh()
    obs_self = engine.observe(st, first)
    obs_opp = engine.observe(st, 1 - first)
    assert [c["uid"] for c in obs_self["self"]["hand"]] == st.players[first].hand
    assert obs_opp["opponent"]["hand_count"] == len(st.players[first].hand)
    assert _collect_uids(obs_opp).isdisjoint(set(st.players[first].hand))


def test_t0019_hidden_slot_privacy():
    st, first = fresh()
    # 注入[待命]卡到先手手牌；先放置单位保持控制（107.3.d 失控会清待命牌）
    from tests.helpers import place_battlefield_unit

    place_battlefield_unit(st, first, 0)
    st.battlefields[0].controller = first
    uid = give_hand(st, first, {"def_id": "t:h1", "name": "待命卡",
                                "card_types": {CardType.UNIT}, "cost_energy": 1,
                                "cost_power": (), "might": 1, "keywords": {Keyword.HIDDEN}})
    st.players[first].rune_power = {"R": 1}  # [A] 费用
    from riftsim.actions import Action
    from riftsim.enums import ActionKind

    engine.step(st, Action(ActionKind.HIDE, first, uid, {"battlefield": 0}))
    obs_self = engine.observe(st, first)
    obs_opp = engine.observe(st, 1 - first)
    slot_self = obs_self["board"][0]["hidden_slot"]
    slot_opp = obs_opp["board"][0]["hidden_slot"]
    assert len(slot_self) == 1 and slot_self[0]["content"]["uid"] == uid
    assert len(slot_opp) == 1 and slot_opp[0]["content"] is None  # 卡背：内容不可见
