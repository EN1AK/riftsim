# 确定性 RNG（docs/architecture.md §6）：单一 seed → 命名子流；消费顺序由主循环固定。
from __future__ import annotations

import hashlib
import random
from typing import Any


# 命名流清单（固定顺序仅文档意义；真正确定性来自“同一路径按同名流消费”）
STREAM_BATTLEFIELD_PICK = "battlefield_pick"   # R-CR-485 各选 1 战场
STREAM_SHUFFLE_MAIN = "shuffle_main"           # R-CR-114
STREAM_SHUFFLE_RUNE = "shuffle_rune"
STREAM_MULLIGAN = "mulligan"                   # R-CR-117 相关随机（若有）
STREAM_RECYCLE_ORDER = "recycle_random_order"  # R-CR-416.5 多张回主牌堆随机序
STREAM_BURNOUT_SHUFFLE = "burnout_shuffle"     # R-CR-431 废牌堆洗入牌堆
STREAM_EFFECT = "effect_random"                # 效果内随机（随机弃置等）

ALL_STREAMS = (
    STREAM_BATTLEFIELD_PICK,
    STREAM_SHUFFLE_MAIN,
    STREAM_SHUFFLE_RUNE,
    STREAM_MULLIGAN,
    STREAM_RECYCLE_ORDER,
    STREAM_BURNOUT_SHUFFLE,
    STREAM_EFFECT,
)


def _stream_seed(seed: int, name: str) -> int:
    h = hashlib.sha256(f"riftsim:{seed}:{name}".encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big")


class RngStreams:
    """按名称索引的 random.Random 集合；snapshot 保存/恢复各流状态。"""

    def __init__(self, streams: dict[str, random.Random]) -> None:
        self._streams = dict(streams)
        self._counts: dict[str, int] = {n: 0 for n in streams}

    @classmethod
    def from_seed(cls, seed: int) -> "RngStreams":
        return cls({n: random.Random(_stream_seed(seed, n)) for n in ALL_STREAMS})

    def get(self, name: str) -> random.Random:
        if name not in self._streams:
            raise KeyError(f"unknown rng stream: {name}")
        return self._streams[name]

    def shuffle(self, name: str, seq: list[Any]) -> None:
        self._counts[name] += 1
        self.get(name).shuffle(seq)

    def choice(self, name: str, seq: list[Any]) -> Any:
        self._counts[name] += 1
        return self.get(name).choice(seq)

    def randrange(self, name: str, stop: int) -> int:
        self._counts[name] += 1
        return self.get(name).randrange(stop)

    def counts(self) -> dict[str, int]:
        return dict(self._counts)

    def get_state(self) -> dict[str, tuple]:
        return {n: r.getstate() for n, r in self._streams.items()}

    def set_state(self, states: dict[str, tuple], counts: dict[str, int] | None = None) -> None:
        for n, st in states.items():
            if n not in self._streams:
                raise KeyError(f"unknown rng stream in snapshot: {n}")
            self._streams[n].setstate(st)
        if counts:
            self._counts.update(counts)

    # --- 序列化（snapshot 用；random 状态为 tuple，需转 list 以便 JSON） ---
    def to_json(self) -> dict[str, Any]:
        def conv(t: tuple) -> list:
            return [conv(x) if isinstance(x, tuple) else x for x in t]

        return {
            "states": {n: conv(st) for n, st in self.get_state().items()},
            "counts": self.counts(),
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "RngStreams":
        def conv(x: Any) -> Any:
            if isinstance(x, list):
                return tuple(conv(i) for i in x)
            return x

        obj = cls({n: random.Random(0) for n in data["states"]})
        obj.set_state({n: conv(st) for n, st in data["states"].items()}, data.get("counts"))
        return obj
