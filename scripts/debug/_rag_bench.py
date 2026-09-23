# -*- coding: utf-8 -*-
"""BGE-M3 CPU 编码速度基准（排查索引构建慢的问题）。"""
import os, time
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOCAL = os.path.join(ROOT, "workspace", "rag", "bge-m3")

print("torch threads (intra-op):", torch.get_num_threads())

from sentence_transformers import SentenceTransformer
m = SentenceTransformer(LOCAL, device="cpu")

docs = ["反制咒语时，可以再次反制。结算按链式顺序逆序进行。" * 6] * 16  # ~100+ token / 条
for label in (1, 2):
    t = time.time()
    v = m.encode(docs, batch_size=16, normalize_embeddings=True)
    print("run %d: 16 docs -> %.1fs" % (label, time.time() - t))

# 限制线程对比
torch.set_num_threads(max(1, torch.get_num_threads() // 2))
print("threads ->", torch.get_num_threads())
t = time.time()
m.encode(docs, batch_size=16, normalize_embeddings=True)
print("half threads: 16 docs -> %.1fs" % (time.time() - t))
