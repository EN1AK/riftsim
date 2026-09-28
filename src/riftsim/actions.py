# Action / DecisionRequest（docs/api_contract.md §4/§6）
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from .enums import ActionKind, DecisionKind


@dataclass(frozen=True)
class Action:
    kind: ActionKind
    actor: int
    source_uid: int | None = None
    params: dict[str, Any] = field(default_factory=dict)

    def digest(self) -> str:
        return json.dumps(
            {
                "kind": self.kind.value, "actor": self.actor,
                "source_uid": self.source_uid, "params": self.params,
            },
            ensure_ascii=False, sort_keys=True, default=str,
        )


@dataclass(frozen=True)
class DecisionRequest:
    """引擎停驻的决策点（architecture §3）。options 为请求的参数化描述。"""

    kind: DecisionKind
    player: int
    options: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind.value, "player": self.player, "options": self.options}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "DecisionRequest":
        return cls(kind=DecisionKind(d["kind"]), player=d["player"], options=d["options"])
