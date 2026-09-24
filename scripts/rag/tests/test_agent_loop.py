# -*- coding: utf-8 -*-
"""agent_loop 单测：脚本化 planner / fixture DB / 解析器桩，离线可运行。

覆盖：多步执行顺序与观察回灌、证据池跨步累积（3+5-1=7）、步数上限与钳制、
重复动作拒绝、两个连续无效输出停止、submit_answer 引用校验（拒绝可重提）、
确定性 fallback（含空池固定答案、planner 抛异常）、以及卡名解析/扩展文本接线。
"""
import json
import sqlite3

import pytest

import agent_loop
from agent_loop import AgentRunner, agent_max_steps

_EMPTY_OUTCOME = {"resolved": [], "ambiguous": [], "unresolved": []}


def _row(rule_id, topic, pcr, oi=None):
    return (rule_id, topic, pcr, oi, None, None, "reconciled")


def _resolved_item(card_id, mention, name_cn=None):
    return {"card_id": card_id, "mention": mention, "name_cn": name_cn,
            "name_en": None, "confidence": "exact", "source": "deterministic"}


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
            _row("R-CR-100.1", "连锁", "连锁规则 100.1（含反制）"),
            _row("R-CR-100.2", "连锁", "连锁规则 100.2"),
            _row("R-CR-100.3", "连锁", "连锁规则 100.3（含反制）"),
            _row("R-CR-716.1", "连锁", "连锁规则一：反制可以响应"),
            _row("R-CR-716.10", "连锁", "连锁规则十"),
            _row("R-CARD-OGN-242", "card:OGN-242 (Baited Hook / 海兽钓钩)",
                 "海兽钓钩的规范效果文本"),
            _row("R-FAQ-001", "FAQ：连锁", None, "连锁常见问题解答"),
        ],
    )
    db.executemany(
        "INSERT INTO rule_cards VALUES (?,?,?)",
        [
            ("R-CARD-OGN-242", "OGN-242", "rule_id"),
            ("R-CR-100.3", "OGN-242", "evidence"),
            ("R-CR-716.1", "OGN-242", "evidence"),
            ("R-CR-716.10", "OGN-242", "evidence"),
            ("R-FAQ-001", "OGN-242", "evidence"),
        ],
    )
    db.executemany(
        "INSERT INTO rule_keywords VALUES (?,?,?)",
        [("R-CR-716.1", "连锁", "topic"), ("R-CR-100.1", "连锁", "topic")],
    )
    db.commit()
    yield db
    db.close()


class _ScriptedPlanner:
    """按脚本逐步输出（JSON 字符串或异常）的 fixture planner，并记录入参消息。"""

    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = []

    def __call__(self, messages):
        self.calls.append([dict(m) for m in messages])
        out = self.outputs.pop(0)
        if isinstance(out, Exception):
            raise out
        return out


class _FakeResolver:
    def __init__(self, query_outcome=None, by_mention=None):
        self._query_outcome = query_outcome or _EMPTY_OUTCOME
        self._by_mention = by_mention or {}

    def resolve(self, query):
        return self._query_outcome

    def resolve_name(self, mention):
        return self._by_mention.get(
            mention, {"resolved": [], "ambiguous": [],
                      "unresolved": [mention]})


def _generate_spy(calls):
    def spy(query, rows, model, timeout=180.0):
        calls.append({"query": query, "rows": rows, "model": model})
        return "fallback-生成答案", 0.1
    return spy


def _step(tool, **arguments):
    return json.dumps({"tool": tool, "arguments": arguments,
                       "rationale": "r"}, ensure_ascii=False)


def _submit(answer, citations=()):
    return _step("submit_answer", answer=answer, citations=list(citations))


def _runner(rules_db, planner, generate_calls=None, resolver=None,
            max_steps=None, vec=None):
    return AgentRunner(
        db=rules_db, resolver=resolver, kw_vocab=["连锁", "反制"],
        vec=vec or (lambda text: None),
        planner=planner,
        generate_fn=_generate_spy(generate_calls if generate_calls is not None
                                  else []),
        max_steps=max_steps)


# ---------- 1.1 多步执行顺序与观察回灌 ----------

def test_valid_sequence_executes_tools_in_order(rules_db):
    planner = _ScriptedPlanner([
        _step("lookup_rule", ref="100."),
        _step("get_card_rules", card_id="OGN-242"),
        _submit("回答见 [R-CR-100.1]", ["R-CR-716.1"]),
    ])
    result = _runner(rules_db, planner).run("反制怎么结算")

    assert result.exhausted is False
    assert [t["tool"] for t in result.trace] == [
        "lookup_rule", "get_card_rules", "submit_answer"]
    # 第 2 步 planner 看到了第 1 步的观察（3 行命中；R-CR-100.3 也在其中）
    obs = json.loads(planner.calls[1][-1]["content"])
    assert obs["ok"] is True and obs["rows"] == 3
    assert obs["preview"][0]["rule_id"] == "R-CR-100.1"
    # 每步 trace 都有完整形状
    assert all({"step", "tool", "arguments", "ok", "summary"} <= set(t)
               for t in result.trace[:2])


# ---------- 1.2 证据池跨步累积（3 + 5 - 1 = 7）----------

def test_pool_accumulates_distinct_rows_across_steps(rules_db):
    gen_calls = []
    planner = _ScriptedPlanner([
        _step("lookup_rule", ref="100."),       # 3 行
        _step("get_card_rules", card_id="OGN-242"),  # 5 行，重叠 R-CR-100.3
    ])
    result = _runner(rules_db, planner, generate_calls=gen_calls,
                     max_steps=2).run("连锁与反制")

    assert result.exhausted is True  # 步数耗尽进 fallback
    assert len(gen_calls) == 1
    ids = [r[0] for r in gen_calls[0]["rows"]]
    assert len(ids) == 7 and len(set(ids)) == 7
    assert set(ids) == {"R-CR-100.1", "R-CR-100.2", "R-CR-100.3",
                        "R-CR-716.1", "R-CR-716.10",
                        "R-CARD-OGN-242", "R-FAQ-001"}
    assert len(result.sources) == 7


# ---------- 1.3 步数上限 / 钳制 / 重复 / 连续无效 ----------

def test_step_limit_stops_loop(rules_db):
    planner = _ScriptedPlanner([_step("lookup_rule", ref="100.")] * 9)
    result = _runner(rules_db, planner, max_steps=2).run("q")
    assert result.exhausted is True
    assert len(planner.calls) == 2  # 恰好调用 max_steps 次


def test_max_steps_env_clamped(monkeypatch):
    monkeypatch.setenv("RAG_AGENT_MAX_STEPS", "99")
    assert agent_max_steps() == 8
    monkeypatch.setenv("RAG_AGENT_MAX_STEPS", "0")
    assert agent_max_steps() == 1
    monkeypatch.setenv("RAG_AGENT_MAX_STEPS", "abc")
    assert agent_max_steps() == 4
    monkeypatch.delenv("RAG_AGENT_MAX_STEPS")
    assert agent_max_steps() == 4


def test_duplicate_action_rejected(rules_db):
    planner = _ScriptedPlanner([
        _step("lookup_rule", ref="100."),
        _step("lookup_rule", ref="100."),  # 完全重复
        _submit("回答 [R-CR-100.1]"),
    ])
    result = _runner(rules_db, planner).run("q")

    assert result.exhausted is False
    # 重复动作被拒：不进 trace、不再执行（证据池未新增行）
    assert [t["tool"] for t in result.trace] == ["lookup_rule", "submit_answer"]
    obs = json.loads(planner.calls[2][-1]["content"])
    assert obs["ok"] is False and "重复动作" in obs["error"]


def test_two_consecutive_invalid_outputs_stop_loop(rules_db):
    gen_calls = []
    planner = _ScriptedPlanner(["完全不是 JSON", "garbage {broken",
                                _submit("不应到达")])
    result = _runner(rules_db, planner, generate_calls=gen_calls).run("q")

    assert result.exhausted is True
    assert len(planner.calls) == 2  # 两个连续无效即停止，第三个输出未消费
    assert any("动作无效" in m["content"] for call in planner.calls
               for m in call if m["role"] == "user")


# ---------- 2.1 submit_answer 引用校验 ----------

def test_valid_submit_ends_loop(rules_db):
    planner = _ScriptedPlanner([
        _step("lookup_rule", ref="100."),
        _submit("回答见 [R-CR-100.1] 与 [R-CR-100.2]", ["R-CR-100.3"]),
    ])
    result = _runner(rules_db, planner).run("q")

    assert result.exhausted is False
    assert result.answer == "回答见 [R-CR-100.1] 与 [R-CR-100.2]"
    assert [s["rule_id"] for s in result.sources] == [
        "R-CR-100.1", "R-CR-100.2", "R-CR-100.3"]


def test_unknown_citation_rejected_then_resubmit(rules_db):
    planner = _ScriptedPlanner([
        _step("lookup_rule", ref="100."),
        _submit("引用错误 [R-CR-999.9]", ["R-CR-999.9"]),
        _submit("修正后 [R-CR-100.1]"),
    ])
    result = _runner(rules_db, planner).run("q")

    assert result.exhausted is False
    obs = json.loads(planner.calls[2][-1]["content"])
    assert obs["ok"] is False and "R-CR-999.9" in obs["error"]
    assert "证据池" in obs["error"]
    assert result.sources[0]["rule_id"] == "R-CR-100.1"


# ---------- 2.2 确定性 fallback ----------

def test_exhausted_fallback_generates_over_pool_rows(rules_db):
    gen_calls = []
    planner = _ScriptedPlanner([_step("lookup_rule", ref="100.")])
    result = _runner(rules_db, planner, generate_calls=gen_calls,
                     max_steps=1).run("连锁规则")

    assert result.exhausted is True
    assert result.answer == "fallback-生成答案"
    assert [r[0] for r in gen_calls[0]["rows"]] == [
        "R-CR-100.1", "R-CR-100.2", "R-CR-100.3"]


def test_empty_pool_fixed_answer_without_generation(rules_db):
    gen_calls = []
    planner = _ScriptedPlanner([_step("lookup_rule", ref="R-ZZZ-999")])
    result = _runner(rules_db, planner, generate_calls=gen_calls,
                     max_steps=1).run("asdfgh")

    assert result.exhausted is True
    assert result.answer == agent_loop.EMPTY_RETRIEVAL_ANSWER
    assert "检索结果为空" in result.warnings
    assert result.sources == []
    assert gen_calls == []  # 空池不触发生成


def test_planner_exception_lands_in_fallback(rules_db):
    gen_calls = []
    planner = _ScriptedPlanner([RuntimeError("boom")])
    result = _runner(rules_db, planner, generate_calls=gen_calls).run("q")

    assert result.exhausted is True  # 结构化结果而非异常
    assert result.answer == agent_loop.EMPTY_RETRIEVAL_ANSWER
    assert gen_calls == []


# ---------- 解析器接线 / 扩展文本 / 覆盖度 ----------

def test_coverage_flows_from_pre_resolution(rules_db):
    resolver = _FakeResolver(query_outcome={
        "resolved": [_resolved_item("OGN-242", "海兽钓钩", "海兽钓钩")],
        "ambiguous": [{"mention": "蔚", "candidates": [
            {"card_id": "OGN-066a", "name_cn": "蔚·铲除者"}]}],
        "unresolved": ["某卡名"],
    })
    planner = _ScriptedPlanner([
        _step("lookup_rule", ref="100."),
        _submit("回答 [R-CR-100.1]"),
    ])
    result = _runner(rules_db, planner, resolver=resolver).run(
        "海兽钓钩能反制蔚和某卡名吗")

    assert [c["card_id"] for c in result.resolved_cards] == ["OGN-242"]
    assert [a["mention"] for a in result.ambiguous_mentions] == ["蔚"]
    assert result.unresolved_mentions == ["某卡名"]


def test_search_rules_uses_resolved_card_expansion(rules_db):
    vec_texts = []

    def vec(text):
        vec_texts.append(text)
        return None

    resolver = _FakeResolver(query_outcome={
        "resolved": [_resolved_item("OGN-242", "海兽钓钩")],
        "ambiguous": [], "unresolved": [],
    })
    planner = _ScriptedPlanner([
        _step("search_rules", query="反制"),
        _submit("回答 [R-CR-716.1]"),
    ])
    result = _runner(rules_db, planner, resolver=resolver, vec=vec).run(
        "海兽钓钩能反制吗")

    assert any("海兽钓钩的规范效果文本" in t for t in vec_texts)
    assert result.exhausted is False  # R-CARD 条目入池后可被引用
    assert result.sources[0]["rule_id"] == "R-CR-716.1"


def test_resolve_cards_tool_merges_outcome(rules_db):
    resolver = _FakeResolver(by_mention={
        "海兽钓钩": {"resolved": [_resolved_item("OGN-242", "海兽钓钩")],
                   "ambiguous": [], "unresolved": []},
    })
    planner = _ScriptedPlanner([
        _step("resolve_cards", mentions=["海兽钓钩", "不存在的卡"]),
        _step("lookup_rule", ref="100."),
        _submit("回答 [R-CR-100.1]"),
    ])
    result = _runner(rules_db, planner, resolver=resolver).run("q")

    assert resolver is not None
    assert [c["card_id"] for c in result.resolved_cards] == ["OGN-242"]
    assert result.unresolved_mentions == ["不存在的卡"]
    obs = json.loads(planner.calls[1][-1]["content"])
    assert obs["ok"] is True and obs["results"][0]["resolved"] == ["OGN-242"]
    assert obs["results"][1]["unresolved"] == ["不存在的卡"]
