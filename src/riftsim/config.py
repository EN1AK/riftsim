# GameConfig（docs/api_contract.md §2）
from __future__ import annotations

from dataclasses import dataclass

from .cards import DeckList


@dataclass(frozen=True)
class GameConfig:
    decks: tuple[DeckList, DeckList]
    mode: str = "duel_1v1"          # 仅支持（R-CR-485）
    win_score: int = 8
    trace_level: str = "summary"    # off|summary|sampled|debug
    max_steps: int = 5000
    match_id: str | None = None
    spec_version: str | None = None  # 启动断言与 spec/rules_spec.yaml hash 一致（可选）
    sample_every: int = 20           # trace_level=sampled 时公共快照间隔
