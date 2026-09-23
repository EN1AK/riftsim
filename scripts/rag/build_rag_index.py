# -*- coding: utf-8 -*-
"""从 workspace/final/rules.db 构建 BGE-M3 向量索引 → workspace/rag/

分片可恢复：长文本优先排序后切成若干分片，每次运行编码一个分片并存盘；
全部完成后 --merge 合并为最终向量与元数据。任何运行方式（前台/后台/中断）
都不会浪费已完成的分片。

用法（仓库根目录执行）：
    python scripts/rag/build_rag_index.py              # 编码下一个缺失的分片
    python scripts/rag/build_rag_index.py --part 3     # 编码指定分片
    python scripts/rag/build_rag_index.py --merge      # 全部完成后的合并
    python scripts/rag/build_rag_index.py --status     # 查看进度
"""
import argparse
import datetime
import glob
import json
import os
import sqlite3
import sys
import time

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
# hf_xet 的 CAS 端点国内常不可达导致下载挂起，回退普通 CDN 下载
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.join(ROOT, "workspace", "final", "rules.db")
OUT_DIR = os.path.join(ROOT, "workspace", "rag")
PARTS_DIR = os.path.join(OUT_DIR, "parts")
MODEL_NAME = os.environ.get("RAG_EMBED_MODEL", "BAAI/bge-m3")
BATCH_SIZE = 16
BATCHES_PER_PART = 12        # 每分片 12 批 × 16 = 192 条
MAX_CHARS = 2000             # 索引文本上限（绝大多数条目远低于此；截断仅影响超长官方解释的尾部）


def resolve_model():
    """本地模型目录（workspace/rag/bge-m3，权重文件就位）优先，否则在线加载。"""
    local = os.path.join(OUT_DIR, "bge-m3")
    if os.path.exists(os.path.join(local, "pytorch_model.bin")):
        return local
    return MODEL_NAME


def build_text(row):
    parts = [v.strip() for v in row if v and v.strip()]
    return "\n".join(parts)[:MAX_CHARS]


def load_docs():
    db = sqlite3.connect(DB)
    rows = db.execute(
        "SELECT rule_id, topic, proposed_canonical_rule, official_interpretation,"
        " exception, example FROM rules ORDER BY rule_id"
    ).fetchall()
    ids, texts = [], []
    for r in rows:
        t = build_text(r[1:])
        if t:
            ids.append(r[0])
            texts.append(t)
    return ids, texts


def sorted_order(texts):
    """长文本优先：各分片内填充长度接近，整体耗时最低；跨运行顺序确定。"""
    return sorted(range(len(texts)), key=lambda i: -len(texts[i]))


def part_files():
    return sorted(glob.glob(os.path.join(PARTS_DIR, "part_*.npy")))


def main():
    ap = argparse.ArgumentParser(description="构建 rules BGE-M3 向量索引（分片可恢复）")
    ap.add_argument("--part", type=int, default=None, help="只编码指定分片（默认下一个缺失的）")
    ap.add_argument("--merge", action="store_true", help="合并全部分片为最终索引")
    ap.add_argument("--status", action="store_true", help="只打印进度")
    args = ap.parse_args()

    ids, texts = load_docs()
    order = sorted_order(texts)
    per_part = BATCHES_PER_PART * BATCH_SIZE
    chunks = [order[i:i + per_part] for i in range(0, len(order), per_part)]
    done = {int(os.path.basename(p)[5:-4]) for p in part_files()}

    if args.status:
        print("规则 %d 条，分片 %d 个，已完成 %d 个: %s"
              % (len(ids), len(chunks), len(done), sorted(done)))
        return

    os.makedirs(PARTS_DIR, exist_ok=True)
    import numpy as np

    if args.merge:
        missing = [i for i in range(len(chunks)) if i not in done]
        if missing:
            sys.exit("还有 %d 个分片未完成: %s" % (len(missing), missing))
        vecs = None
        dim = None
        collected = []
        for ci in range(len(chunks)):
            v = np.load(os.path.join(PARTS_DIR, "part_%02d.npy" % ci))
            if dim is None:
                dim = v.shape[1]
                vecs = np.empty((len(ids), dim), dtype=np.float32)
            vecs[ci * per_part: ci * per_part + len(chunks[ci])] = v
            collected.extend(chunks[ci])
        # vecs 按“长文本排序后的顺序”存放 → 还原回 rule_id 顺序
        final = np.empty_like(vecs)
        for slot, doc_idx in enumerate(collected):
            final[doc_idx] = vecs[slot]
        np.save(os.path.join(OUT_DIR, "rules_vectors.npy"), final)
        meta = {
            "model": MODEL_NAME,
            "rule_ids": ids,
            "texts": texts,
            "count": len(ids),
            "dim": int(final.shape[1]),
            "built_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "normalized": True,
        }
        with open(os.path.join(OUT_DIR, "rules_index.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False)
        print("索引完成: %d 条 × %d 维 → %s" % (len(ids), final.shape[1], OUT_DIR))
        return

    # 编码一个分片
    ci = args.part if args.part is not None else next(
        (i for i in range(len(chunks)) if i not in done), None)
    if ci is None:
        print("全部分片已完成，运行 --merge 合并")
        return
    if ci < 0 or ci >= len(chunks):
        sys.exit("分片编号越界: %d (共 %d 个)" % (ci, len(chunks)))

    from sentence_transformers import SentenceTransformer
    t0 = time.time()
    sel = chunks[ci]
    docs = [texts[i] for i in sel]
    print("分片 %d/%d：%d 条（最长 %d 字符），模型: %s"
          % (ci, len(chunks) - 1, len(docs), max(len(d) for d in docs), resolve_model()))
    model = SentenceTransformer(resolve_model(), device="cpu")
    vecs = model.encode(docs, batch_size=BATCH_SIZE, normalize_embeddings=True,
                        show_progress_bar=True).astype(np.float32)
    np.save(os.path.join(PARTS_DIR, "part_%02d.npy" % ci), vecs)
    print("分片 %d 完成：%d 条，耗时 %.1fs" % (ci, len(docs), time.time() - t0))


if __name__ == "__main__":
    main()
