# -*- coding: utf-8 -*-
"""card_resolver 单测：迷你 sqlite fixture（tmp_path），离线可运行。"""
import sqlite3

import pytest

import card_resolver
from card_resolver import CardResolver


@pytest.fixture()
def mini_dbs(tmp_path):
    """迷你 cards/rules DB；列只保留 resolver 实际查询的字段。"""
    cards_path = str(tmp_path / "cards.db")
    db = sqlite3.connect(cards_path)
    db.execute("""CREATE TABLE cards (card_key TEXT PRIMARY KEY,
                                      name_en TEXT, name_cn TEXT, sub_title_cn TEXT)""")
    db.executemany(
        "INSERT INTO cards VALUES (?,?,?,?)",
        [
            ("OGN-242", "Baited Hook", "海兽钓钩", None),
            ("ARC-001", None, "蔚", "铲除者"),
            ("OGN-036", "Vi, Destructive", "蔚", None),
            ("OGN-076", "Yasuo, Unforgiven", "亚索", None),
            ("SFD-235", "Yasuo, Wanderer", "亚索", None),
            ("OGN-900", "Wandering Swordsman", "德莱·厄斯", None),
            ("OGN-030", "Jinx, Demolitionist", "金克丝", None),
        ],
    )
    db.commit()
    db.close()

    rules_path = str(tmp_path / "rules.db")
    db = sqlite3.connect(rules_path)
    db.execute("CREATE TABLE rules (rule_id TEXT PRIMARY KEY, topic TEXT)")
    db.executemany(
        "INSERT INTO rules VALUES (?,?)",
        [
            ("R-CARD-OGN-242", "card:OGN-242 (Baited Hook / 海兽钓钩)"),
            ("R-CARD-ARC-001", "card:ARC-001 (蔚)"),
        ],
    )
    db.commit()
    db.close()
    return {"cards": cards_path, "rules": rules_path}


@pytest.fixture()
def resolver(mini_dbs):
    return CardResolver(rules_db_path=mini_dbs["rules"],
                        cards_db_path=mini_dbs["cards"])


def _card_ids(result):
    return [r["card_id"] for r in result["resolved"]]


def test_exact_cn_name(resolver):
    res = resolver.resolve("海兽钓钩 能回收几张牌？")
    assert "OGN-242" in _card_ids(res)
    item = next(r for r in res["resolved"] if r["card_id"] == "OGN-242")
    assert item["confidence"] == "exact"
    assert item["source"] == "deterministic"
    assert item["name_cn"] == "海兽钓钩"
    assert item["name_en"] == "Baited Hook"


def test_subtitle_full_name_hit(resolver):
    # 组合全名命中比裸名更强 → 唯一解析到 ARC-001
    res = resolver.resolve("铲除者 蔚 的被动是什么")
    assert _card_ids(res) == ["ARC-001"]
    assert not res["ambiguous"]
    item = res["resolved"][0]
    assert item["name_cn"] == "铲除者 蔚"


def test_en_name_hit(resolver):
    res = resolver.resolve("Baited Hook 怎么结算？")
    assert "OGN-242" in _card_ids(res)


def test_fallback_without_cards_db(mini_dbs, tmp_path, capsys):
    # cards DB 不存在：降级为 R-CARD topic + card-id 字面匹配，且不崩溃
    missing = str(tmp_path / "no_such_cards.db")
    r = CardResolver(rules_db_path=mini_dbs["rules"], cards_db_path=missing)
    res = r.resolve("OGN-242 的现行效果")
    assert "OGN-242" in _card_ids(res)
    res2 = r.resolve("海兽钓钩 这张牌")  # 别名来自 R-CARD topic
    assert "OGN-242" in _card_ids(res2)
    assert "降级" in capsys.readouterr().err


def test_quoted_segment_hit(resolver):
    res = resolver.resolve("《海兽钓钩》先后手都能用吗")
    item = next(r for r in res["resolved"] if r["card_id"] == "OGN-242")
    assert item["mention"] == "海兽钓钩"
    assert item["confidence"] == "exact"


def test_same_name_variants_ambiguous(resolver):
    res = resolver.resolve("亚索 怎么玩")
    assert not res["resolved"]
    assert len(res["ambiguous"]) == 1
    cand_ids = {c["card_id"] for c in res["ambiguous"][0]["candidates"]}
    assert cand_ids == {"OGN-076", "SFD-235"}
    assert res["ambiguous"][0]["mention"] == "亚索"


def test_bare_name_multi_card_ambiguous(resolver):
    # 裸名 "蔚" 同时属于 ARC-001 / OGN-036 → ambiguous
    res = resolver.resolve("蔚 的技能怎么用")
    assert len(res["ambiguous"]) == 1
    cand_ids = {c["card_id"] for c in res["ambiguous"][0]["candidates"]}
    assert cand_ids == {"ARC-001", "OGN-036"}


def test_normalized_punctuation_hit(resolver):
    # 别名含 ·，query 用空格写法 → 归一化命中
    res = resolver.resolve("德莱 厄斯 怎么结算")
    item = next(r for r in res["resolved"] if r["card_id"] == "OGN-900")
    assert item["confidence"] == "normalized"


def test_fuzzy_unique_hit(resolver):
    # 引号内文本与别名错位（“金克丝”不在场），模糊匹配唯一命中
    res = resolver.resolve("《暴走金克》是哪位")
    assert "OGN-030" in _card_ids(res)
    item = next(r for r in res["resolved"] if r["card_id"] == "OGN-030")
    assert item["confidence"] == "fuzzy"


def test_retry_still_unresolved(resolver):
    res = resolver.resolve("《无名卡牌》怎么用")
    assert res["unresolved"] == ["无名卡牌"]


def test_llm_extraction_disabled_by_default(mini_dbs):
    calls = []

    def fake_llm(query):
        calls.append(query)
        return ["海兽钓钩"]

    r = CardResolver(rules_db_path=mini_dbs["rules"],
                     cards_db_path=mini_dbs["cards"],
                     llm_extract=fake_llm)
    res = r.resolve("完全无关的一个问题")
    assert calls == []  # 默认关闭：不调用 llm callable
    assert not res["resolved"]


def test_llm_extraction_enabled(mini_dbs, monkeypatch):
    monkeypatch.setenv("RAG_LLM_CARD_EXTRACTION", "1")
    calls = []

    def fake_llm(query):
        calls.append(query)
        return ["海兽钓钩"]

    r = CardResolver(rules_db_path=mini_dbs["rules"],
                     cards_db_path=mini_dbs["cards"],
                     llm_extract=fake_llm)
    res = r.resolve("完全无关的一个问题")
    assert calls  # 开启后：确定性抽取一无所获才调用
    item = res["resolved"][0]
    assert item["card_id"] == "OGN-242"
    assert item["source"] == "llm_extract"
