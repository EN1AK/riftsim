# -*- coding: utf-8 -*-
"""rag_query 检索工具层单测：tmp_path 迷你 rules.db，离线可运行。

覆盖：get_card_rules JOIN / search_rules（含扩展文本召回）/ lookup_rule 三形态 /
EvidencePool 去重保序 / one-shot 关键函数（extract_terms、keyword_recall、fuse）
行为不变（与重构前语义一致）。
"""
import sqlite3

import pytest

import rag_query
from rag_query import (EvidencePool, extract_terms, fuse, get_card_rules,
                       keyword_recall, lookup_rule, search_rules)

_RULE_ROW_COLS = ("rule_id", "topic", "proposed_canonical_rule",
                  "official_interpretation", "exception", "example", "status")


def _row(rule_id, topic, pcr, oi=None):
    return (rule_id, topic, pcr, oi, None, None, "reconciled")


@pytest.fixture()
def rules_db(tmp_path):
    path = str(tmp_path / "rules.db")
    db = sqlite3.connect(path)
    db.execute("""CREATE TABLE rules (
        rule_id TEXT PRIMARY KEY, topic TEXT, proposed_canonical_rule TEXT,
        official_interpretation TEXT, exception TEXT, example TEXT, status TEXT)""")
    db.execute("""CREATE TABLE rule_cards (
        rule_id TEXT NOT NULL, card_id TEXT NOT NULL, origin TEXT NOT NULL)""")
    db.execute("""CREATE TABLE rule_keywords (
        rule_id TEXT NOT NULL, keyword TEXT NOT NULL, source_field TEXT NOT NULL)""")
    db.executemany(
        "INSERT INTO rules VALUES (?,?,?,?,?,?,?)",
        [
            _row("R-CR-716.1", "连锁", "连锁规则一：反制可以响应"),
            _row("R-CR-716.10", "连锁", "连锁规则十：后发先至"),
            _row("R-CR-700.1", "回合结构", "回合流程从重置开始"),
            _row("R-CARD-OGN-242", "card:OGN-242 (Baited Hook / 海兽钓钩)",
                 "海兽钓钩的规范效果文本"),
            _row("R-FAQ-001", "FAQ：连锁", None, "连锁常见问题解答"),
        ],
    )
    db.executemany(
        "INSERT INTO rule_cards VALUES (?,?,?)",
        [
            ("R-CARD-OGN-242", "OGN-242", "rule_id"),
            ("R-CR-716.1", "OGN-242", "evidence"),
            ("R-FAQ-001", "OGN-242", "evidence"),
            ("R-CR-700.1", "OGN-999", "evidence"),
        ],
    )
    db.executemany(
        "INSERT INTO rule_keywords VALUES (?,?,?)",
        [
            ("R-CR-716.1", "连锁", "topic"),
            ("R-CR-716.10", "连锁", "topic"),
            ("R-FAQ-001", "连锁", "topic"),
        ],
    )
    db.commit()
    yield db
    db.close()


def _ids(rows):
    return [r[0] for r in rows]


# ---------- get_card_rules ----------

def test_get_card_rules_join(rules_db):
    rows = get_card_rules(rules_db, "OGN-242")
    assert _ids(rows) == ["R-CARD-OGN-242", "R-CR-716.1", "R-FAQ-001"]
    # 列形状与 fetch_rows 一致（7 列，rule_id 在前）
    assert len(rows[0]) == 7
    assert rows[0][1] is not None


def test_get_card_rules_top_k_and_miss(rules_db):
    assert _ids(get_card_rules(rules_db, "OGN-242", top_k=2)) == [
        "R-CARD-OGN-242", "R-CR-716.1"]
    assert get_card_rules(rules_db, "VEN-999") == []


# ---------- search_rules ----------

def _fake_vec(text):
    """脚本化向量通道：按文本内容返回固定召回。"""
    out = {}
    if "反制" in text:
        out["R-CR-700.1"] = (1, 0.9)
    if "扩展关键词" in text:
        out["R-CR-700.1"] = (1, 0.9)
        out["R-FAQ-001"] = (2, 0.8)
    return out


def test_search_rules_basic(rules_db):
    rows = search_rules(rules_db, "反制怎么响应", 5,
                        vec=_fake_vec, kw_vocab=["连锁", "反制"])
    # 关键词通道命中 R-CR-716.1（文本含“反制”），向量通道命中 R-CR-700.1
    assert set(_ids(rows)) == {"R-CR-716.1", "R-CR-700.1"}


def test_search_rules_expansion_changes_recall(rules_db):
    base = search_rules(rules_db, "反制怎么响应", 5,
                        vec=_fake_vec, kw_vocab=["连锁", "反制"])
    expanded = search_rules(rules_db, "反制怎么响应", 5,
                            vec=_fake_vec, kw_vocab=["连锁", "反制"],
                            expansion_texts=["扩展关键词 补充文本"])
    assert "R-FAQ-001" not in _ids(base)
    assert "R-FAQ-001" in _ids(expanded)  # 扩展文本通道引入了新的召回
    assert set(_ids(base)) <= set(_ids(expanded))


def test_search_rules_no_vec_channel(rules_db):
    rows = search_rules(rules_db, "反制怎么响应", 5,
                        vec=None, kw_vocab=["连锁", "反制"])
    assert _ids(rows) == ["R-CR-716.1"]


def test_search_rules_all_channels_empty(rules_db):
    assert search_rules(rules_db, "zzz", 5, vec=None, kw_vocab=[]) == []


# ---------- lookup_rule ----------

def test_lookup_rule_exact(rules_db):
    assert _ids(lookup_rule(rules_db, "R-CR-716.1")) == ["R-CR-716.1"]
    assert _ids(lookup_rule(rules_db, "R-CARD-OGN-242")) == ["R-CARD-OGN-242"]
    assert lookup_rule(rules_db, "R-CR-999") == []


def test_lookup_rule_bare_number(rules_db):
    assert _ids(lookup_rule(rules_db, "716.1")) == ["R-CR-716.1", "R-CR-716.10"]


def test_lookup_rule_empty_ref(rules_db):
    assert lookup_rule(rules_db, "") == []
    assert lookup_rule(rules_db, "   ") == []


# ---------- EvidencePool ----------

def test_evidence_pool_dedup_keeps_insertion_order():
    r1 = _row("R-CR-1", "t", "x")
    r2 = _row("R-CR-2", "t", "x")
    r3 = _row("R-CR-3", "t", "x")
    pool = EvidencePool()
    pool.add([r1, r2])
    pool.add([r1, r3])  # r1 重复：去重且不换序
    assert len(pool) == 3
    assert pool.rule_ids == ["R-CR-1", "R-CR-2", "R-CR-3"]
    assert pool.rows() == [r1, r2, r3]


# ---------- one-shot 函数行为回归 ----------

def test_keyword_recall_semantics_unchanged(rules_db):
    # hits 语义 = 命中的词元数（每个词元在任一字段 LIKE 命中记 1）
    res = keyword_recall(rules_db, ["连锁"], 30)
    expect = {"R-CR-716.1": 1, "R-CR-716.10": 1, "R-FAQ-001": 1}
    assert {rid: hits for rid, (_, hits) in res.items()} == expect
    assert [rank for (rank, _) in res.values()] == [1, 2, 3]
    # 多词元：R-CR-716.1 同时含“连锁/反制”，hits=2 且排最前
    res2 = keyword_recall(rules_db, ["连锁", "反制"], 30)
    assert res2["R-CR-716.1"] == (1, 2)
    assert res2["R-CR-716.10"] == (2, 1)


def test_extract_terms_semantics_unchanged():
    terms = extract_terms("716.1 与 OGN-242 的 stack 结算顺序", ["连锁"])
    assert "716.1" in terms
    assert "OGN-242" in terms
    assert "stack" in terms
    assert "连锁" not in terms


def test_fuse_semantics_unchanged():
    order, aux = fuse({"A": (1, 0.9)}, {"B": (1, 1), "A": (2, 1)}, 5)
    assert order[0] == "A"  # 双通道命中者 RRF 分数更高
    assert set(order) == {"A", "B"}
    assert aux["A"]["sim"] == 0.9 and aux["A"]["hits"] == 1
    assert aux["B"]["hits"] == 1
