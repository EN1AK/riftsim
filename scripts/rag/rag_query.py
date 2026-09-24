# -*- coding: utf-8 -*-
"""Riftbound 规则知识库 RAG 查询 CLI

召回：BGE-M3 向量召回 + 关键词召回（规则号 / 卡号 / 关键字表 / 拉丁词元），
      RRF 融合。生成：OpenAI 兼容 API（DeepSeek、通义、智谱、OpenAI 等均可）。

除一次性 CLI 管线外，本文件还提供基于连接的检索工具层（agent loop 调用，
rag_server agent 模式使用；原有 CLI 函数签名与行为保持不变）：
    EvidencePool      以 rule_id 为键累积规则行（去重、保持插入序）
    get_card_rules    按 card_id 经 rule_cards 关联取规则行
    search_rules      混合召回函数化（向量通道依赖注入支持扩展文本召回）
    lookup_rule       精确 rule_id / 裸规则号模糊定位

用法（仓库根目录执行）：
    python scripts/rag/rag_query.py "反制堆叠上限是多少"
    python scripts/rag/rag_query.py "OGN-131 现行效果" --retrieve-only   # 只看召回
    python scripts/rag/rag_query.py "chain 内响应顺序" --top-k 8

生成端环境变量（不配也能用 --retrieve-only）：
    OPENAI_API_KEY     必填（或 RAG_API_KEY）
    OPENAI_BASE_URL    例 https://api.deepseek.com/v1（或 RAG_BASE_URL）
    RAG_LLM_MODEL      例 deepseek-chat

注意：rules_fts 是 FTS5 默认 tokenizer，对中文基本无效，故关键词通道走 LIKE；
      向量通道负责语义召回。先用 --retrieve-only 验证召回质量再接生成。
"""
import argparse
import datetime
import json
import os
import re
import sqlite3
import sys

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
# hf_xet 的 CAS 端点国内常不可达导致下载挂起，回退普通 CDN 下载
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.join(ROOT, "workspace", "final", "rules.db")
RAG_DIR = os.path.join(ROOT, "workspace", "rag")
VEC_PATH = os.path.join(RAG_DIR, "rules_vectors.npy")
IDX_PATH = os.path.join(RAG_DIR, "rules_index.json")
MODEL_NAME = os.environ.get("RAG_EMBED_MODEL", "BAAI/bge-m3")

_RE_RULE_NO = re.compile(r"\b\d{3}(?:\.\d+[a-z]?){1,4}\b")
_RE_CARD_ID = re.compile(r"\b[A-Z]{2,4}-\d{3}\b")
_RE_LATIN = re.compile(r"[A-Za-z][A-Za-z0-9_\-]{1,}")
RRF_K = 60
CANDIDATE = 30
# rules 表参与召回/展示的列（fetch_rows / get_card_rules / lookup_rule 统一）
_RULE_COLS = ("rule_id, topic, proposed_canonical_rule, official_interpretation,"
              " exception, example, status")


def resolve_model(default=MODEL_NAME):
    """本地模型目录（workspace/rag/bge-m3，权重文件就位）优先，否则在线加载。"""
    local = os.path.join(RAG_DIR, "bge-m3")
    if os.path.exists(os.path.join(local, "pytorch_model.bin")):
        return local
    return default


def log(msg):
    print(msg, file=sys.stderr)


def extract_terms(query, keywords_vocab):
    terms = set()
    terms.update(_RE_RULE_NO.findall(query))
    terms.update(_RE_CARD_ID.findall(query.upper()))
    for m in _RE_LATIN.finditer(query):
        if len(m.group()) >= 2:
            terms.add(m.group())
    # 关键字表（迅捷/反制/证物 等 83 个官方术语）高精匹配
    terms.update(kw for kw in keywords_vocab if kw and kw in query)
    return [t for t in terms if len(t) >= 2][:8]


def vector_recall(query, candidate):
    """返回 {rule_id: (rank, sim)}；索引缺失时返回 None。"""
    import numpy as np
    from sentence_transformers import SentenceTransformer

    if not (os.path.exists(VEC_PATH) and os.path.exists(IDX_PATH)):
        return None
    with open(IDX_PATH, encoding="utf-8") as f:
        meta = json.load(f)
    vecs = np.load(VEC_PATH)
    model = SentenceTransformer(resolve_model(meta.get("model", MODEL_NAME)), device="cpu")
    q = model.encode([query], normalize_embeddings=True)[0].astype(np.float32)
    sims = vecs @ q
    top = np.argsort(-sims)[:candidate]
    return {meta["rule_ids"][i]: (r + 1, float(sims[i])) for r, i in enumerate(top)}


def keyword_recall(db, terms, candidate):
    """LIKE 多词元计分，返回 {rule_id: (rank, hits)}。"""
    if not terms:
        return {}
    conds, params = [], []
    cols = ("proposed_canonical_rule", "official_interpretation", "topic", "example")
    for t in terms:
        sub = " OR ".join("COALESCE(%s,'') LIKE ?" % c for c in cols)
        conds.append("(CASE WHEN %s THEN 1 ELSE 0 END)" % sub)
        params.extend(["%" + t + "%"] * len(cols))
    sql = ("SELECT rule_id, %s AS hits FROM rules WHERE hits > 0 "
           "ORDER BY hits DESC, rule_id LIMIT ?") % " + ".join(conds)
    params.append(candidate)
    return {rid: (r + 1, h) for r, (rid, h) in enumerate(db.execute(sql, params))}


def fuse(vec, kw, top_k):
    """RRF 融合两个召回通道的排序。"""
    score, aux = {}, {}
    for rid, (rank, sim) in (vec or {}).items():
        score[rid] = score.get(rid, 0.0) + 1.0 / (RRF_K + rank)
        aux.setdefault(rid, {})["sim"] = sim
    for rid, (rank, hits) in kw.items():
        score[rid] = score.get(rid, 0.0) + 1.0 / (RRF_K + rank)
        aux.setdefault(rid, {})["hits"] = hits
    order = sorted(score, key=lambda r: -score[r])[:top_k]
    return order, aux


def fetch_rows(db, rule_ids):
    mark = ",".join("?" for _ in rule_ids)
    rows = db.execute("SELECT %s FROM rules WHERE rule_id IN (%s)"
                      % (_RULE_COLS, mark), rule_ids).fetchall()
    by_id = {r[0]: r for r in rows}
    return [by_id[r] for r in rule_ids if r in by_id]


# ---------- 检索工具层（agent loop / 服务端使用；CLI 管线不受影响） ----------


class EvidencePool:
    """证据池：以 rule_id 为键累积规则行（fetch_rows 返回的行 tuple），
    去重且保持插入序。"""

    def __init__(self):
        self._rows = {}

    def add(self, rows):
        for r in rows or []:
            self._rows.setdefault(r[0], r)

    def rows(self):
        return list(self._rows.values())

    @property
    def rule_ids(self):
        return list(self._rows.keys())

    def __len__(self):
        return len(self._rows)


def get_card_rules(db, card_id, top_k=6):
    """按 card_id 经 rule_cards 关联取规则行（列与 fetch_rows 相同）。"""
    return db.execute(
        "SELECT r.%s FROM rules r JOIN rule_cards rc ON r.rule_id=rc.rule_id"
        " WHERE rc.card_id=? ORDER BY r.rule_id LIMIT ?"
        % _RULE_COLS.replace(", ", ", r."), (card_id, top_k)).fetchall()


def _fuse_channels(channels, top_k):
    """多通道 RRF 融合：channels 为 {rule_id: (rank, aux)} 列表。"""
    score = {}
    for ch in channels:
        for rid, (rank, _aux) in (ch or {}).items():
            score[rid] = score.get(rid, 0.0) + 1.0 / (RRF_K + rank)
    return sorted(score, key=lambda r: -score[r])[:top_k]


def search_rules(db, query, top_k, *, vec=None, kw_vocab, expansion_texts=()):
    """混合召回的函数化：关键词 LIKE + 向量通道（依赖注入）→ RRF → fetch_rows。

    vec：callable(text) -> {rule_id: (rank, sim)} 或 None；为 None 时跳过向量通道。
    expansion_texts：已解析卡的规范文本片段（最多 2 张卡），拼进向量查询文本
        （query + "\\n" + 文本）做扩展召回，与原查询结果 RRF 合并。
    两个通道都不可用时返回空列表。
    """
    terms = extract_terms(query, kw_vocab)
    channels = []
    if vec is not None:
        main_vec = vec(query)
        if main_vec:
            channels.append(main_vec)
        for text in list(expansion_texts)[:2]:
            exp_vec = vec(query + "\n" + text)
            if exp_vec:
                channels.append(exp_vec)
    kw = keyword_recall(db, terms, CANDIDATE)
    if kw:
        channels.append(kw)
    if not channels:
        return []
    return fetch_rows(db, _fuse_channels(channels, top_k))


def lookup_rule(db, ref):
    """精确 rule_id（如 R-CR-716.1 / R-CARD-OGN-242）或裸规则号（如 716.1 →
    rule_id LIKE '%716.1%'）检索；返回规则行列表（列与 fetch_rows 相同）。"""
    ref = (ref or "").strip()
    if not ref:
        return []
    if ref.upper().startswith("R-"):
        return db.execute("SELECT %s FROM rules WHERE rule_id=?" % _RULE_COLS,
                          (ref,)).fetchall()
    return db.execute(
        "SELECT %s FROM rules WHERE rule_id LIKE ? ORDER BY rule_id LIMIT 20"
        % _RULE_COLS, ("%" + ref + "%",)).fetchall()


def build_context(rows):
    blocks = []
    for i, r in enumerate(rows, 1):
        rid, topic, can, oi, exc, ex, status = r

        def cut(v, n):
            return (v[:n] + "…") if v and len(v) > n else (v or "")

        parts = ["[%d] %s（%s | 状态: %s）" % (i, rid, topic or "无主题", status)]
        if can:
            parts.append("规范规则: " + cut(can, 900))
        else:
            parts.append("规范规则: （FAQ 专属条目，无独立规范规则）")
        if oi:
            parts.append("官方解释: " + cut(oi, 700))
        if exc:
            parts.append("例外: " + cut(exc, 300))
        if ex:
            parts.append("案例: " + cut(ex, 300))
        blocks.append("\n".join(parts))
    return "\n\n".join(blocks)


def generate(query, context_rows, model_name, timeout=180.0):
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY") or os.environ.get("RAG_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL") or os.environ.get("RAG_BASE_URL"),
        timeout=timeout,
    )
    context = build_context(context_rows)
    sys_prompt = (
        "你是《符文战场》（Riftbound / LoL TCG）规则助手。仅依据给定参考条目回答，"
        "禁止引入条目外的规则知识；关键结论后用该条目开头标注的完整 rule_id 标注引用，"
        "格式如 [R-CR-383.4.b.2]；禁止使用条目序号（如 [1] [2]）作为引用；"
        "条目不足以回答时明确说明，不要编造。用提问的语言作答，先给结论再给依据。"
    )
    user_prompt = "问题：%s\n\n参考条目：\n%s" % (query, context)
    t0 = datetime.datetime.now()
    resp = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "system", "content": sys_prompt},
                  {"role": "user", "content": user_prompt}],
        temperature=0.2,
    )
    dt = (datetime.datetime.now() - t0).total_seconds()
    content = resp.choices[0].message.content
    # 兜底：模型有时仍用条序号 [n] 引用，按序号→rule_id 确定性改写
    id_map = {str(i): r[0] for i, r in enumerate(context_rows, 1)}
    content = re.sub(r"\[(\d{1,3})\]",
                     lambda m: "[" + id_map.get(m.group(1), m.group(1)) + "]",
                     content)
    return content, dt


def main():
    ap = argparse.ArgumentParser(description="Riftbound 规则 RAG 查询")
    ap.add_argument("query", help="自然语言问题")
    ap.add_argument("--top-k", type=int, default=6, help="融合后取前 k 条（默认 6）")
    ap.add_argument("--candidate", type=int, default=30, help="各通道召回池大小")
    ap.add_argument("--retrieve-only", action="store_true", help="只检索不生成")
    ap.add_argument("--no-vector", action="store_true", help="关闭向量通道")
    ap.add_argument("--no-keyword", action="store_true", help="关闭关键词通道")
    ap.add_argument("--model", default=os.environ.get("RAG_LLM_MODEL"),
                    help="生成模型名（默认取 RAG_LLM_MODEL）")
    args = ap.parse_args()

    db = sqlite3.connect(DB)
    kw_vocab = [r[0] for r in db.execute("SELECT DISTINCT keyword FROM rule_keywords")]
    terms = extract_terms(args.query, kw_vocab)

    vec = None
    if not args.no_vector:
        vec = vector_recall(args.query, args.candidate)
        if vec is None:
            log("提示：未找到向量索引，跳过向量通道（先运行 scripts/rag/build_rag_index.py）")
    kw = {} if args.no_keyword else keyword_recall(db, terms, args.candidate)
    if vec is None and not kw:
        sys.exit("两个召回通道都不可用")

    order, aux = fuse(vec, kw, args.top_k)
    rows = fetch_rows(db, order)

    print("== 召回 %d 条 ==" % len(rows))
    for i, r in enumerate(rows, 1):
        a = aux.get(r[0], {})
        tag = []
        if "sim" in a:
            tag.append("sim=%.3f" % a["sim"])
        if "hits" in a:
            tag.append("kw=%d" % a["hits"])
        print("  %d. %s | %s %s" % (i, r[0], (r[1] or "")[:48], "(" + ", ".join(tag) + ")"))
    if terms:
        log("关键词词元: " + ", ".join(terms))

    if args.retrieve_only:
        return
    if not args.model:
        sys.exit("未配置生成模型：设置 RAG_LLM_MODEL 或 --model（另有 --retrieve-only 模式）")
    if not (os.environ.get("OPENAI_API_KEY") or os.environ.get("RAG_API_KEY")):
        sys.exit("未配置 API Key：设置 OPENAI_API_KEY（或 RAG_API_KEY）")

    print("\n== 生成回答（%s）==" % args.model)
    answer, dt = generate(args.query, rows, args.model)
    print(answer)
    log("生成耗时 %.1fs" % dt)


if __name__ == "__main__":
    main()
