# -*- coding: utf-8 -*-
"""Riftbound 规则 RAG HTTP 服务（kami-man 契约）

接口（契约 v2，字段均为增量、legacy 消费方不受影响）：
    POST /api/query   请求 {"query": 非空字符串, "top_k": 可选整数(1-20, 默认 6),
                            "mode": 可选 "agent"(默认) | "oneshot",
                            "trace": 可选布尔(默认 false)}
        agent 模式    200 {"answer": str, "warnings": [...],
                          "sources": [{"rule_id", "topic"}],
                          "mode": "agent", "exhausted": bool,
                          "resolved_cards": [...],
                          "coverage": {"unresolved_mentions": [...],
                                       "ambiguous_mentions": [...]},
                          ("trace": [...]，仅请求 trace=true)}
        oneshot 模式  200 {"answer": str, "warnings": [...],
                          "sources": [...]}（legacy 形状，无 v2 字段）
        400 {"error": str}  请求体非法（非 JSON / query 为空 / top_k 越界 / mode 非法 / trace 非布尔）
        500 {"error": str}  生成失败（未配置 LLM / LLM API 异常）
    GET  /healthz     200 {"ok": true}（不加载模型，仅探活）
    其余方法/路径     405 / 404，均返回 {"error": str}

实现要点（沿用 ygo-rag 在同机的 proven 模式）：
    - 裸 ASGI 应用 + uvicorn，不引入 Web 框架；
    - BGE-M3 嵌入在持久子进程 worker 中运行（stdin/stdout JSON lines 协议），
      与网络进程隔离；模型在首次请求时才加载（冷启动数十秒，bot 侧 240s 超时覆盖）；
    - 规则向量（约 12MB）常驻主进程内存，rules.db 走 sqlite；
    - 召回/提示词/生成逻辑复用 scripts/rag/rag_query.py，保持与 CLI 同一语义。

环境变量（与 rag_query 一致 + 服务专属）：
    OPENAI_API_KEY / OPENAI_BASE_URL / RAG_LLM_MODEL   生成端（如 DeepSeek）
    RAG_LLM_MODEL_DEEP           深度思考模型：问题含"深度思考"时使用，
                                 并统一附加 thinking=disabled（用强模型、关扩展思考）
    RAG_EMBED_MODEL              嵌入模型（默认 BAAI/bge-m3；本地 workspace/rag/bge-m3 优先）
    RAG_SERVER_EMBED_TIMEOUT     单次嵌入请求超时秒数（默认 300）
    RAG_SERVER_GENERATE_TIMEOUT  单次生成超时秒数（默认 180，需小于 bot 侧 240）
    RAG_AGENT_MAX_STEPS          agent 模式最大步数（默认 4，钳制 1-8）
    卡名解析相关（RAG_CARDS_DB_PATH / RAG_CARD_RESOLUTION_* / RAG_LLM_CARD_*）
        见 scripts/rag/card_resolver.py

运行：
    python scripts/rag/rag_server.py --host 127.0.0.1 --port 7862 [--preload]
    --preload 在启动时预热 sqlite / 向量 / 嵌入 worker（探活式编码一条短文本）。
"""
import argparse
import json
import os
import queue
import re
import sqlite3
import subprocess
import sys
import threading

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import agent_loop  # noqa: E402  agent 模式循环（契约 v2）
import rag_query  # noqa: E402  复用召回与生成逻辑

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7862
DEFAULT_TOP_K = 6
MAX_TOP_K = 20
CANDIDATE = 30
DEFAULT_MODE = "agent"
VALID_MODES = ("agent", "oneshot")


class GenerationError(RuntimeError):
    """生成阶段失败（未配置 LLM 或 LLM API 异常），映射为 HTTP 500。"""


def _env_flag(name):
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def _make_llm_extract(chat):
    """llm_extract(query) -> [str]：LLM 卡名提取（仍须过本地索引解析）。"""
    def extract(query):
        system = ("你是《符文战场》规则问答的卡名提取器。从用户问题中提取被提及的"
                  "卡名，逐字摘取、不得改写或编造。只输出 JSON 字符串数组，"
                  "没有则输出 []。")
        try:
            out = chat([
                {"role": "system", "content": system},
                {"role": "user", "content": query},
            ]) or ""
            start, end = out.find("["), out.rfind("]")
            if start < 0 or end <= start:
                return []
            names = json.loads(out[start:end + 1])
            if not isinstance(names, list):
                return []
            return [n.strip() for n in names
                    if isinstance(n, str) and n.strip()]
        except Exception as exc:
            print("rag_server: LLM 卡名提取失败: %s" % exc, file=sys.stderr)
            return []
    return extract


def _make_llm_select(chat, resolver):
    """llm_select(mention, card_ids) -> id | None：ambiguous 候选仲裁，未知 id 拒绝。"""
    def select(mention, card_ids):
        lines = []
        for cid in card_ids:
            info = (getattr(resolver, "cards", None) or {}).get(cid) or {}
            lines.append("- %s（%s / %s）" % (
                cid, info.get("name_cn") or "?", info.get("name_en") or "?"))
        system = ("你是《符文战场》卡名消歧器。给定卡名提及与候选卡号，选出最匹配"
                  "的一个；无法确定就用 null。只输出 JSON："
                  "{\"card_id\": \"<id>\"} 或 {\"card_id\": null}。")
        try:
            out = chat([
                {"role": "system", "content": system},
                {"role": "user", "content": "提及：%s\n候选：\n%s"
                                          % (mention, "\n".join(lines))},
            ]) or ""
            start, end = out.find("{"), out.rfind("}")
            if start < 0 or end <= start:
                return None
            chosen = json.loads(out[start:end + 1]).get("card_id")
            return chosen if chosen in card_ids else None
        except Exception as exc:
            print("rag_server: LLM 消歧失败: %s" % exc, file=sys.stderr)
            return None
    return select


class SubprocessEmbedder:
    """持久子进程嵌入 worker：模型常驻子进程，与网络进程隔离（同 ygo-rag 模式）。"""

    def __init__(self, model_name, timeout_seconds=300):
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds
        self._process = None
        self._lock = threading.Lock()

    def embed_query(self, text):
        payload = self._request({"operation": "query", "text": text})
        return [float(v) for v in payload["vector"]]

    def close(self):
        process = self._process
        self._process = None
        if process is None or process.poll() is not None:
            return
        try:
            process.stdin.close()
            process.wait(timeout=5)
        except Exception:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

    def _request(self, payload):
        with self._lock:
            process = self._ensure_process()
            process.stdin.write(json.dumps(payload, ensure_ascii=True) + "\n")
            process.stdin.flush()
            response_queue = queue.Queue(maxsize=1)
            reader = threading.Thread(
                target=lambda: response_queue.put(process.stdout.readline()),
                daemon=True,
            )
            reader.start()
            try:
                raw = response_queue.get(timeout=self.timeout_seconds)
            except queue.Empty as exc:
                self.close()
                raise RuntimeError(
                    "嵌入 worker 超时（%ds）" % self.timeout_seconds
                ) from exc
            if not raw:
                code = process.poll()
                self.close()
                raise RuntimeError(
                    "嵌入 worker 无响应退出%s"
                    % ("（返回码 %s）" % code if code is not None else "")
                )
            response = json.loads(raw)
            if not response.get("ok"):
                raise RuntimeError("嵌入 worker 失败: %s" % response.get("error"))
            return response

    def _ensure_process(self):
        if self._process is not None and self._process.poll() is None:
            return self._process
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        env["RAG_EMBED_MODEL"] = self.model_name
        env.setdefault("USE_TF", "0")
        env.setdefault("USE_FLAX", "0")
        env.setdefault("TRANSFORMERS_NO_TF", "1")
        env.setdefault("TRANSFORMERS_NO_FLAX", "1")
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        self._process = subprocess.Popen(
            [sys.executable, os.path.abspath(__file__), "--embedding-worker"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            # stderr 直接继承：模型加载日志/报错进入主进程 stderr（systemd journal 可见）
            text=True,
            encoding="utf-8",
            errors="strict",
            bufsize=1,
            env=env,
            creationflags=creationflags,
        )
        return self._process

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def _embedding_worker_main():
    """子进程入口：加载 BGE-M3 并逐行响应嵌入请求。"""
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(
        rag_query.resolve_model(os.environ.get("RAG_EMBED_MODEL", rag_query.MODEL_NAME)),
        device="cpu",
    )
    for line in sys.stdin:
        try:
            payload = json.loads(line)
            if payload.get("operation") == "query":
                vec = model.encode(
                    [str(payload["text"])], normalize_embeddings=True
                )[0]
                response = {"ok": True, "vector": [float(x) for x in vec]}
            else:
                raise ValueError("unsupported embedding operation: %s"
                                 % payload.get("operation"))
        except Exception as exc:
            response = {"ok": False, "error": str(exc)}
        sys.stdout.write(json.dumps(response, ensure_ascii=True) + "\n")
        sys.stdout.flush()
    return 0


class RagService:
    """召回 + 生成的有状态封装：sqlite / 关键字表 / 向量 / 嵌入 worker 全部惰性加载。"""

    def __init__(self):
        self._db = None
        self._kw_vocab = None
        self._vecs = None
        self._meta = None
        self._embedder = None
        self._resolver = None

    def _get_db(self):
        if self._db is None:
            self._db = sqlite3.connect(rag_query.DB)
        return self._db

    def _get_kw_vocab(self):
        if self._kw_vocab is None:
            db = self._get_db()
            self._kw_vocab = [
                r[0] for r in db.execute("SELECT DISTINCT keyword FROM rule_keywords")
            ]
        return self._kw_vocab

    def _load_vectors(self):
        """返回 (vecs, meta)；索引缺失时返回 (None, None)。"""
        if self._vecs is not None:
            return self._vecs, self._meta
        if not (os.path.exists(rag_query.VEC_PATH)
                and os.path.exists(rag_query.IDX_PATH)):
            return None, None
        import numpy as np

        with open(rag_query.IDX_PATH, encoding="utf-8") as f:
            self._meta = json.load(f)
        self._vecs = np.load(rag_query.VEC_PATH)
        return self._vecs, self._meta

    def _get_embedder(self):
        if self._embedder is None:
            _, meta = self._load_vectors()
            model_name = (meta or {}).get("model") or os.environ.get(
                "RAG_EMBED_MODEL", rag_query.MODEL_NAME
            )
            timeout = int(os.environ.get("RAG_SERVER_EMBED_TIMEOUT", "300"))
            self._embedder = SubprocessEmbedder(model_name, timeout_seconds=timeout)
        return self._embedder

    def _vector_recall(self, query, warnings):
        import numpy as np

        vecs, meta = self._load_vectors()
        if vecs is None:
            warnings.append("未找到向量索引，仅使用关键词召回")
            return None
        try:
            q = np.asarray(self._get_embedder().embed_query(query), dtype=np.float32)
        except Exception as exc:
            warnings.append("向量召回失败，已退回关键词召回: %s" % exc)
            return None
        sims = vecs @ q
        top = np.argsort(-sims)[:CANDIDATE]
        return {
            meta["rule_ids"][i]: (r + 1, float(sims[i]))
            for r, i in enumerate(top)
        }

    def retrieve(self, query, top_k, warnings):
        db = self._get_db()
        terms = rag_query.extract_terms(query, self._get_kw_vocab())
        vec = self._vector_recall(query, warnings)
        kw = rag_query.keyword_recall(db, terms, CANDIDATE)
        if vec is None and not kw:
            return []
        order, _ = rag_query.fuse(vec, kw, top_k)
        return rag_query.fetch_rows(db, order)

    def answer(self, query, top_k, mode=DEFAULT_MODE, trace=False):
        """按模式分发：oneshot 走 legacy 单次管线，agent 走工具循环。"""
        if mode == "oneshot":
            return self._answer_oneshot(query, top_k)
        return self._answer_agent(query, top_k, trace)

    def _pick_model(self, query):
        """按问题选择模型并返回 (model_name, thinking_disabled)。

        问题含"深度思考"时改用 RAG_LLM_MODEL_DEEP（且附加 thinking=disabled，
        用更强的模型但关掉扩展思考）；否则用默认 RAG_LLM_MODEL。
        """
        model_name = self._check_generation_config()
        deep = "深度思考" in (query or "")
        if deep:
            model_name = os.environ.get("RAG_LLM_MODEL_DEEP") or model_name
        return model_name, deep

    def _answer_oneshot(self, query, top_k):
        """legacy 单次检索+生成；生成失败抛 GenerationError。"""
        warnings = []
        rows = self.retrieve(query, top_k, warnings)
        if not rows:
            warnings.append("检索结果为空")
            return {
                "answer": agent_loop.EMPTY_RETRIEVAL_ANSWER,
                "warnings": warnings,
                "sources": [],
            }

        model_name, thinking_disabled = self._pick_model(query)
        timeout = float(os.environ.get("RAG_SERVER_GENERATE_TIMEOUT", "180"))
        try:
            answer, _ = rag_query.generate(
                query, rows, model_name, timeout=timeout,
                thinking_disabled=thinking_disabled)
        except GenerationError:
            raise
        except Exception as exc:
            raise GenerationError("生成失败: %s" % exc) from exc

        return {
            "answer": answer,
            "warnings": warnings,
            "sources": [
                {"rule_id": r[0], "topic": r[1] or ""} for r in rows
            ],
        }

    def _check_generation_config(self):
        model_name = os.environ.get("RAG_LLM_MODEL")
        if not model_name:
            raise GenerationError("未配置生成模型（RAG_LLM_MODEL）")
        if not (os.environ.get("OPENAI_API_KEY") or os.environ.get("RAG_API_KEY")):
            raise GenerationError("未配置生成端 API Key（OPENAI_API_KEY）")
        return model_name

    def _answer_agent(self, query, top_k, trace_wanted):
        """agent 模式：planner→工具循环 + 引用校验 + 确定性回退（契约 v2）。"""
        model_name, thinking_disabled = self._pick_model(query)
        timeout = float(os.environ.get("RAG_SERVER_GENERATE_TIMEOUT", "180"))
        vec_warnings = []
        chapter_hint = self._classify_chapter_hint(query, model_name,
                                                   thinking_disabled)
        runner = self._build_agent_runner(model_name, timeout, vec_warnings,
                                          thinking_disabled=thinking_disabled,
                                          chapter_hint=chapter_hint)
        try:
            result = runner.run(query, top_k)
        except GenerationError:
            raise
        except Exception as exc:
            raise GenerationError("生成失败: %s" % exc) from exc
        response = {
            "answer": result.answer,
            "warnings": result.warnings + vec_warnings,
            "sources": result.sources,
            "mode": "agent",
            "exhausted": result.exhausted,
            "resolved_cards": result.resolved_cards,
            "coverage": {
                "unresolved_mentions": result.unresolved_mentions,
                "ambiguous_mentions": result.ambiguous_mentions,
            },
        }
        if trace_wanted:
            response["trace"] = result.trace
        return response

    @staticmethod
    def _classify_chapter_hint(query, model_name, thinking_disabled):
        """前置章节分类（RAG_RULEBOOK_CLASSIFY 可关；失败静默 [] —— 无引导=现状）。"""
        if not agent_loop.rulebook_classify_enabled():
            return []
        return agent_loop.classify_chapters(
            query, model_name, 30.0, thinking_disabled=thinking_disabled)

    def _build_agent_runner(self, model_name, generate_timeout, warnings_sink,
                            thinking_disabled=False, chapter_hint=None):
        """构造 agent 循环执行器（测试可覆盖为桩）。"""
        seen = set()

        def vec(text):
            local = []
            out = self._vector_recall(text, local)
            for msg in local:
                if msg not in seen:
                    seen.add(msg)
                    warnings_sink.append(msg)
            return out

        return agent_loop.AgentRunner(
            db=self._get_db(),
            resolver=self._get_resolver(),
            kw_vocab=self._get_kw_vocab(),
            vec=vec,
            model_name=model_name,
            generate_timeout=generate_timeout,
            thinking_disabled=thinking_disabled,
            chapter_hint=chapter_hint,
        )

    def _get_resolver(self):
        """惰性构建卡名解析器（cards DB 缺失时降级为规则库卡名索引）。"""
        if self._resolver is None:
            import card_resolver
            resolver = card_resolver.CardResolver()
            self._attach_llm_helpers(resolver)
            self._resolver = resolver
        return self._resolver

    @staticmethod
    def _attach_llm_helpers(resolver):
        """API Key 与生成模型可用时按环境开关注入 llm_extract / llm_select。"""
        model_name = os.environ.get("RAG_LLM_MODEL")
        if not model_name:
            return
        if not (os.environ.get("OPENAI_API_KEY") or os.environ.get("RAG_API_KEY")):
            return

        def chat(messages):
            return agent_loop.call_planner(messages, model_name, 30.0)

        if _env_flag("RAG_LLM_CARD_EXTRACTION"):
            resolver.llm_extract = _make_llm_extract(chat)
        if _env_flag("RAG_LLM_CARD_SELECTION"):
            resolver.llm_select = _make_llm_select(chat, resolver)

    def preload(self):
        self._get_kw_vocab()
        self._load_vectors()
        try:
            self._get_resolver()
        except Exception as exc:
            print("预热卡名解析器失败（首次请求时会重试）: %s" % exc,
                  file=sys.stderr)
        try:
            self._get_embedder().embed_query("预热")
        except Exception as exc:
            print("预热嵌入失败（首次请求时会重试）: %s" % exc, file=sys.stderr)

    def close(self):
        if self._embedder is not None:
            self._embedder.close()
        if self._db is not None:
            self._db.close()


def parse_request(payload):
    """契约 v2 校验；非法输入抛 ValueError（映射为 HTTP 400）。"""
    if not isinstance(payload, dict):
        raise ValueError("请求体必须是 JSON 对象")
    query = payload.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query 必须是非空字符串")
    top_k = payload.get("top_k", DEFAULT_TOP_K)
    if isinstance(top_k, bool) or not isinstance(top_k, int):
        raise ValueError("top_k 必须是整数")
    if not 1 <= top_k <= MAX_TOP_K:
        raise ValueError("top_k 必须在 1-%d 之间" % MAX_TOP_K)
    mode = payload.get("mode", DEFAULT_MODE)
    if not isinstance(mode, str) or mode not in VALID_MODES:
        raise ValueError("mode 必须是 agent 或 oneshot")
    trace = payload.get("trace", False)
    if not isinstance(trace, bool):
        raise ValueError("trace 必须是布尔值")
    return query.strip(), top_k, mode, trace


async def _read_body(receive):
    chunks = []
    while True:
        message = await receive()
        if message["type"] != "http.request":
            continue
        chunks.append(message.get("body", b""))
        if not message.get("more_body"):
            break
    return b"".join(chunks)


async def _send_json(send, status, obj):
    body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [
            (b"content-type", b"application/json; charset=utf-8"),
            (b"content-length", str(len(body)).encode("ascii")),
        ],
    })
    await send({"type": "http.response.body", "body": body})


def create_app(service):
    async def app(scope, receive, send):
        if scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    await send({"type": "lifespan.startup.complete"})
                elif message["type"] == "lifespan.shutdown":
                    service.close()
                    await send({"type": "lifespan.shutdown.complete"})
                    return
            return

        if scope["type"] != "http":
            return

        method = scope.get("method", "GET").upper()
        path = scope.get("path", "/")

        if method == "GET" and path == "/healthz":
            await _send_json(send, 200, {"ok": True})
            return
        if method == "GET" and path == "/":
            await _send_json(send, 200, {
                "service": "rift-rag",
                "usage": ("POST /api/query {\"query\": str, \"top_k\": int, "
                          "\"mode\": \"agent|oneshot\", \"trace\": bool}"),
            })
            return
        if path != "/api/query":
            await _send_json(send, 404, {"error": "未知路径: %s" % path})
            return
        if method != "POST":
            await _send_json(send, 405, {"error": "方法不允许: %s" % method})
            return

        try:
            raw = await _read_body(receive)
            payload = json.loads(raw.decode("utf-8") or "null")
        except Exception:
            await _send_json(send, 400, {"error": "请求体不是合法 JSON"})
            return

        try:
            query, top_k, mode, trace = parse_request(payload)
        except ValueError as exc:
            await _send_json(send, 400, {"error": str(exc)})
            return

        try:
            result = service.answer(query, top_k, mode=mode, trace=trace)
        except GenerationError as exc:
            await _send_json(send, 500, {"error": str(exc)})
            return
        except Exception as exc:
            await _send_json(send, 500, {"error": "服务内部错误: %s" % exc})
            return

        await _send_json(send, 200, result)

    return app


def main():
    ap = argparse.ArgumentParser(description="Riftbound 规则 RAG HTTP 服务")
    ap.add_argument("--host", default=os.environ.get("RAG_SERVER_HOST", DEFAULT_HOST))
    ap.add_argument("--port", type=int,
                    default=int(os.environ.get("RAG_SERVER_PORT", DEFAULT_PORT)))
    ap.add_argument("--preload", action="store_true",
                    help="启动时预热 sqlite / 向量 / 嵌入 worker")
    ap.add_argument("--embedding-worker", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()

    if args.embedding_worker:
        raise SystemExit(_embedding_worker_main())

    import uvicorn

    service = RagService()
    if args.preload:
        print("预热中（加载向量索引 + 嵌入模型）...", file=sys.stderr)
        service.preload()
        print("预热完成", file=sys.stderr)

    uvicorn.run(create_app(service), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
