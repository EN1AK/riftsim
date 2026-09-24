# -*- coding: utf-8 -*-
"""rag_server 契约 v2 单测：parse_request / 模式分发 / v2 响应装配 / HTTP 层。

HTTP 层用裸 ASGI scope 驱动（不启动真实服务）；agent 路径用桩 runner，
离线可运行。
"""
import asyncio
import json

import pytest

import agent_loop
import rag_server
from rag_server import (DEFAULT_MODE, GenerationError, RagService, create_app,
                        parse_request)


# ---------- parse_request（3.1） ----------

def test_parse_legacy_body_defaults_to_agent():
    query, top_k, mode, trace = parse_request({"query": "什么是迅捷"})
    assert query == "什么是迅捷" and top_k == 6
    assert mode == "agent" and trace is False


def test_parse_v2_fields():
    _, top_k, mode, trace = parse_request(
        {"query": " q ", "top_k": 8, "mode": "oneshot", "trace": True})
    assert top_k == 8 and mode == "oneshot" and trace is True


def test_parse_invalid_mode_rejected():
    with pytest.raises(ValueError):
        parse_request({"query": "q", "mode": "turbo"})
    with pytest.raises(ValueError):
        parse_request({"query": "q", "mode": 1})


def test_parse_invalid_trace_rejected():
    with pytest.raises(ValueError):
        parse_request({"query": "q", "trace": "yes"})


def test_parse_unknown_keys_ignored():
    query, _, mode, _ = parse_request(
        {"query": "q", "debug_level": 3})
    assert query == "q" and mode == DEFAULT_MODE


def test_parse_legacy_validation_unchanged():
    for bad in ({}, {"query": ""}, {"query": "  "}, {"query": 1},
                {"query": "q", "top_k": 0}, {"query": "q", "top_k": 21},
                {"query": "q", "top_k": "3"}, "not-a-dict"):
        with pytest.raises(ValueError):
            parse_request(bad)


# ---------- 模式分发（3.2） ----------

class _DispatchSpy(RagService):
    def __init__(self):
        super().__init__()
        self.calls = []

    def _answer_oneshot(self, query, top_k):
        self.calls.append(("oneshot", query, top_k))
        return {"answer": "o", "warnings": [], "sources": []}

    def _answer_agent(self, query, top_k, trace_wanted):
        self.calls.append(("agent", query, top_k, trace_wanted))
        return {"answer": "a"}


def test_dispatch_defaults_to_agent():
    svc = _DispatchSpy()
    assert svc.answer("q", 6)["answer"] == "a"
    assert svc.calls == [("agent", "q", 6, False)]


def test_dispatch_explicit_modes():
    svc = _DispatchSpy()
    svc.answer("q", 6, mode="agent", trace=True)
    svc.answer("q", 6, mode="oneshot")
    assert svc.calls == [("agent", "q", 6, True), ("oneshot", "q", 6)]


# ---------- v2 响应装配（3.3，服务层） ----------

def _scripted_result(**overrides):
    base = dict(
        answer="答案 [R-CR-1]", warnings=["w1"],
        sources=[{"rule_id": "R-CR-1", "topic": "t"}],
        exhausted=False,
        resolved_cards=[{"card_id": "OGN-242", "mention": "海兽钓钩"}],
        unresolved_mentions=["某卡"],
        ambiguous_mentions=[{"mention": "蔚",
                             "candidates": [{"card_id": "OGN-066a"}]}],
        trace=[{"step": 1, "tool": "search_rules", "arguments": {},
                "ok": True, "summary": "2 rules"}],
    )
    base.update(overrides)
    return agent_loop.AgentResult(**base)


class _StubRunnerService(RagService):
    """桩掉 runner 构建的服务：返回脚本化 AgentResult。"""

    def __init__(self, result=None, error=None):
        super().__init__()
        self._scripted = result
        self._error = error
        self.runner_calls = []

    def _build_agent_runner(self, model_name, generate_timeout, warnings_sink,
                            thinking_disabled=False):
        self.runner_calls.append(model_name)
        outer = self

        class _Runner:
            def run(self, query, top_k):
                if outer._error is not None:
                    raise outer._error
                return outer._scripted

        return _Runner()


@pytest.fixture()
def llm_env(monkeypatch):
    monkeypatch.setenv("RAG_LLM_MODEL", "fixture-model")
    monkeypatch.setenv("OPENAI_API_KEY", "fixture-key")


def test_agent_response_shape(llm_env):
    svc = _StubRunnerService(result=_scripted_result())
    resp = svc.answer("q", 6)
    assert resp["mode"] == "agent"
    assert resp["exhausted"] is False
    assert resp["resolved_cards"] == [
        {"card_id": "OGN-242", "mention": "海兽钓钩"}]
    assert resp["coverage"] == {
        "unresolved_mentions": ["某卡"],
        "ambiguous_mentions": [{"mention": "蔚",
                                "candidates": [{"card_id": "OGN-066a"}]}],
    }
    assert "trace" not in resp  # 未请求 trace
    assert resp["warnings"] == ["w1"]


def test_agent_response_trace_only_on_request(llm_env):
    svc = _StubRunnerService(result=_scripted_result())
    resp = svc.answer("q", 6, trace=True)
    assert resp["trace"][0]["tool"] == "search_rules"


def test_agent_missing_llm_config_is_generation_error(monkeypatch):
    monkeypatch.delenv("RAG_LLM_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("RAG_API_KEY", raising=False)
    svc = _StubRunnerService(result=_scripted_result())
    with pytest.raises(GenerationError):
        svc.answer("q", 6)
    monkeypatch.setenv("RAG_LLM_MODEL", "m")
    with pytest.raises(GenerationError):  # 有模型无 key
        svc.answer("q", 6)


def test_agent_runner_exception_wrapped(llm_env):
    svc = _StubRunnerService(error=RuntimeError("boom"))
    with pytest.raises(GenerationError, match="生成失败"):
        svc.answer("q", 6)


def test_oneshot_response_keeps_legacy_shape():
    svc = _DispatchSpy()  # _answer_oneshot 返回固定三字段
    resp = svc.answer("q", 6, mode="oneshot")
    assert set(resp) == {"answer", "warnings", "sources"}


def test_preload_warms_resolver(monkeypatch):
    warmed = []

    class _Svc(RagService):
        def _get_kw_vocab(self):
            warmed.append("kw")

        def _load_vectors(self):
            warmed.append("vec")

        def _get_resolver(self):
            warmed.append("resolver")
            return object()

        def _get_embedder(self):
            warmed.append("embedder")

            class _E:
                def embed_query(self, text):
                    return [0.0]

            return _E()

    _Svc().preload()
    assert "resolver" in warmed


# ---------- HTTP 层（裸 ASGI scope 驱动） ----------

def _run_http(app, payload=None, path="/api/query", method="POST"):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    sent = [{"type": "http.request", "body": body, "more_body": False}]
    responses = []

    async def receive():
        return sent.pop(0)

    async def send(message):
        responses.append(message)

    scope = {"type": "http", "method": method, "path": path}
    asyncio.run(app(scope, receive, send))
    status = next(m["status"] for m in responses
                  if m["type"] == "http.response.start")
    data = b"".join(m.get("body", b"") for m in responses
                    if m["type"] == "http.response.body")
    return status, json.loads(data.decode("utf-8"))


class _StubService:
    """HTTP 层用的最小服务桩。"""

    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def answer(self, query, top_k, mode="agent", trace=False):
        self.calls.append((query, top_k, mode, trace))
        if self.error is not None:
            raise self.error
        return self.result

    def close(self):
        pass


def test_http_agent_roundtrip_mode_trace_forwarded():
    body = {"answer": "a", "warnings": [], "sources": [], "mode": "agent",
            "exhausted": False, "resolved_cards": [],
            "coverage": {"unresolved_mentions": [], "ambiguous_mentions": []}}
    svc = _StubService(result=body)
    status, data = _run_http(
        create_app(svc),
        {"query": "海兽钓钩能反制吗", "mode": "agent", "trace": False})
    assert status == 200 and data == body
    assert svc.calls == [("海兽钓钩能反制吗", 6, "agent", False)]


def test_http_legacy_request_runs_with_defaults():
    body = {"answer": "a", "warnings": [], "sources": []}
    svc = _StubService(result=body)
    status, data = _run_http(create_app(svc), {"query": "什么是迅捷"})
    assert status == 200 and data == body
    assert svc.calls[0][2:] == ("agent", False)


def test_http_oneshot_shape_passthrough():
    body = {"answer": "a", "warnings": [], "sources": []}
    svc = _StubService(result=body)
    status, data = _run_http(
        create_app(svc), {"query": "q", "mode": "oneshot"})
    assert status == 200
    assert set(data) == {"answer", "warnings", "sources"}
    assert svc.calls[0][2] == "oneshot"


def test_http_400_on_invalid_body():
    svc = _StubService(result={})
    status, data = _run_http(create_app(svc), {"query": "q", "mode": "turbo"})
    assert status == 400 and "error" in data
    assert svc.calls == []  # 校验失败不打到服务


def test_http_500_on_generation_error():
    svc = _StubService(error=GenerationError("未配置生成模型（RAG_LLM_MODEL）"))
    status, data = _run_http(create_app(svc), {"query": "q"})
    assert status == 500 and "未配置生成模型" in data["error"]


def test_http_error_semantics_unchanged():
    svc = _StubService(result={"answer": "a", "warnings": [], "sources": []})
    status, data = _run_http(
        create_app(svc), {"query": "q"}, path="/nope")
    assert status == 404 and "error" in data
    status, data = _run_http(create_app(svc), {"query": "q"}, method="GET")
    assert status == 405
    status, data = _run_http(
        create_app(svc), None, path="/healthz", method="GET")
    assert status == 200 and data == {"ok": True}


# ---------- LLM 辅助解析开关（RAG_LLM_CARD_EXTRACTION / SELECTION） ----------

class _BareResolver:
    def __init__(self):
        self.llm_extract = None
        self.llm_select = None
        self.cards = {"OGN-242": {"name_cn": "海兽钓钩",
                                  "name_en": "Baited Hook"}}


def test_llm_helpers_attached_only_with_flags(llm_env, monkeypatch):
    calls = []

    def fake_chat(messages, model_name, timeout):
        calls.append(messages)
        last = messages[-1]["content"]
        if "候选" in last:
            return '{"card_id": "OGN-242"}'
        return '["海兽钓钩"]'

    monkeypatch.setattr(rag_server.agent_loop, "call_planner", fake_chat)
    resolver = _BareResolver()
    monkeypatch.delenv("RAG_LLM_CARD_EXTRACTION", raising=False)
    monkeypatch.delenv("RAG_LLM_CARD_SELECTION", raising=False)
    RagService._attach_llm_helpers(resolver)
    assert resolver.llm_extract is None and resolver.llm_select is None

    monkeypatch.setenv("RAG_LLM_CARD_EXTRACTION", "1")
    monkeypatch.setenv("RAG_LLM_CARD_SELECTION", "1")
    RagService._attach_llm_helpers(resolver)
    assert resolver.llm_extract("海兽钓钩和蔚怎么结算") == ["海兽钓钩"]
    assert resolver.llm_select("海兽钓钩", ["OGN-242", "OGN-243"]) == "OGN-242"


def test_llm_select_rejects_unknown_id(llm_env, monkeypatch):
    def fake_chat(messages, model_name, timeout):
        return '{"card_id": "ZZZ-999"}'

    monkeypatch.setattr(rag_server.agent_loop, "call_planner", fake_chat)
    monkeypatch.setenv("RAG_LLM_CARD_SELECTION", "1")
    resolver = _BareResolver()
    RagService._attach_llm_helpers(resolver)
    assert resolver.llm_select("海兽钓钩", ["OGN-242"]) is None


def test_llm_helpers_skipped_without_model_config(monkeypatch):
    monkeypatch.delenv("RAG_LLM_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("RAG_API_KEY", raising=False)
    monkeypatch.setenv("RAG_LLM_CARD_EXTRACTION", "1")
    resolver = _BareResolver()
    RagService._attach_llm_helpers(resolver)
    assert resolver.llm_extract is None


# ---------- 深度思考触发模型切换（_pick_model） ----------

def test_pick_model_defaults_to_main_model(llm_env):
    monkeypatch_del = RagService.__new__(RagService)
    model, flag = monkeypatch_del._pick_model("什么是迅捷")
    assert model == "fixture-model" and flag is False


def test_pick_model_deep_trigger(llm_env, monkeypatch):
    monkeypatch.setenv("RAG_LLM_MODEL_DEEP", "deep-model-x")
    svc = RagService.__new__(RagService)
    model, flag = svc._pick_model("请深度思考：两者结算顺序")
    assert model == "deep-model-x" and flag is True


def test_pick_model_deep_falls_back_without_env(llm_env, monkeypatch):
    monkeypatch.delenv("RAG_LLM_MODEL_DEEP", raising=False)
    svc = RagService.__new__(RagService)
    model, flag = svc._pick_model("深度思考一下这个问题")
    assert model == "fixture-model" and flag is True
