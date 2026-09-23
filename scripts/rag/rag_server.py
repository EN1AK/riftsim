# -*- coding: utf-8 -*-
"""Riftbound 规则 RAG HTTP 服务（kami-man 契约）

接口：
    POST /api/query   请求 {"query": 非空字符串, "top_k": 可选整数(1-20, 默认 6)}
        200 {"answer": str, "warnings": [str, ...],
             "sources": [{"rule_id": str, "topic": str}, ...]}
        400 {"error": str}  请求体非法（非 JSON / query 为空 / top_k 越界）
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
    RAG_EMBED_MODEL              嵌入模型（默认 BAAI/bge-m3；本地 workspace/rag/bge-m3 优先）
    RAG_SERVER_EMBED_TIMEOUT     单次嵌入请求超时秒数（默认 300）
    RAG_SERVER_GENERATE_TIMEOUT  单次生成超时秒数（默认 180，需小于 bot 侧 240）

运行：
    python scripts/rag/rag_server.py --host 127.0.0.1 --port 7862 [--preload]
    --preload 在启动时预热 sqlite / 向量 / 嵌入 worker（探活式编码一条短文本）。
"""
import argparse
import json
import os
import queue
import sqlite3
import subprocess
import sys
import threading

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import rag_query  # noqa: E402  复用召回与生成逻辑

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7862
DEFAULT_TOP_K = 6
MAX_TOP_K = 20
CANDIDATE = 30

EMPTY_RETRIEVAL_ANSWER = (
    "未在规则库中检索到与该问题相关的条目，"
    "请补充章节号（如 716.1）、卡号（如 OGN-131）或换一种问法后重试。"
)


class GenerationError(RuntimeError):
    """生成阶段失败（未配置 LLM 或 LLM API 异常），映射为 HTTP 500。"""


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

    def answer(self, query, top_k):
        """返回契约响应 dict；生成失败抛 GenerationError。"""
        warnings = []
        rows = self.retrieve(query, top_k, warnings)
        if not rows:
            warnings.append("检索结果为空")
            return {
                "answer": EMPTY_RETRIEVAL_ANSWER,
                "warnings": warnings,
                "sources": [],
            }

        model_name = os.environ.get("RAG_LLM_MODEL")
        if not model_name:
            raise GenerationError("未配置生成模型（RAG_LLM_MODEL）")
        if not (os.environ.get("OPENAI_API_KEY") or os.environ.get("RAG_API_KEY")):
            raise GenerationError("未配置生成端 API Key（OPENAI_API_KEY）")

        timeout = float(os.environ.get("RAG_SERVER_GENERATE_TIMEOUT", "180"))
        try:
            answer, _ = rag_query.generate(query, rows, model_name, timeout=timeout)
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

    def preload(self):
        self._get_kw_vocab()
        self._load_vectors()
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
    """契约校验；非法输入抛 ValueError（映射为 HTTP 400）。"""
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
    return query.strip(), top_k


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
                "usage": "POST /api/query {\"query\": str, \"top_k\": int}",
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
            query, top_k = parse_request(payload)
        except ValueError as exc:
            await _send_json(send, 400, {"error": str(exc)})
            return

        try:
            result = service.answer(query, top_k)
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
