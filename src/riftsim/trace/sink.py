# TraceSink：off/summary/sampled/debug 四等级缓冲写盘（docs/training_architecture.md §8）
from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any

LEVELS = ("off", "summary", "sampled", "debug")


class TraceSink:
    """事件/决策/快照缓冲；局末一次性写盘（summary/sampled）或滚动缓冲（debug 亦可局末）。
    引擎热路径零格式化：仅在对应等级需要时由 runner 传记录对象进来。"""

    def __init__(self, level: str = "summary", *, sample_every: int = 20) -> None:
        assert level in LEVELS
        self.level = level
        self.sample_every = sample_every
        self.records: list[dict[str, Any]] = []
        self.event_count = 0

    @property
    def enabled(self) -> bool:
        return self.level != "off"

    def on_header(self, rec: dict) -> None:
        if self.enabled:
            self.records.append(rec)

    def on_decision(self, rec: dict) -> None:
        if self.level != "off":
            self.records.append(rec)

    def on_event(self, rec: dict) -> None:
        if self.level in ("summary", "sampled", "debug"):
            self.records.append(rec)

    def on_snapshot(self, rec: dict, *, step_id: int) -> None:
        if self.level == "debug" or (self.level == "sampled" and step_id % self.sample_every == 0):
            self.records.append(rec)

    def on_footer(self, rec: dict) -> None:
        if self.level != "off":
            self.records.append(rec)

    def flush(self, out_dir: str | Path) -> Path | None:
        if self.level == "off" or not self.records:
            return None
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        match_id = self.records[0].get("match_id", "unknown")
        path = out / f"{match_id}.jsonl"
        with path.open("w", encoding="utf-8", newline="\n") as f:
            for rec in self.records:
                f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
        return path
