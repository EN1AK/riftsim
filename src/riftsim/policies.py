# 策略协议与内置策略（runner 自举与回归用；训练器适配见 docs/training_architecture.md §5）
from __future__ import annotations

import random
from typing import Protocol, Sequence

from .actions import Action
from .enums import ActionKind


class Policy(Protocol):
    policy_id: str

    def act(self, obs: dict, legal: Sequence[Action], rng: random.Random) -> Action: ...


class RandomPolicy:
    """均匀随机；rng 自带（不消费引擎种子流）。"""

    def __init__(self, seed: int = 0, policy_id: str = "random/v1") -> None:
        self.rng = random.Random(seed)
        self.policy_id = policy_id

    def act(self, obs: dict, legal: Sequence[Action], rng: random.Random) -> Action:
        return legal[self.rng.randrange(len(legal))]


class EndTurnPolicy:
    """调试基线：主阶段仅 END_MAIN；其他请求选第一个合法。"""

    policy_id = "endturn/v1"

    def act(self, obs: dict, legal: Sequence[Action], rng: random.Random) -> Action:
        for a in legal:
            if a.kind == ActionKind.END_MAIN:
                return a
        return legal[0]


class ScriptedPolicy:
    """固定动作脚本（回放/确定性测试）；脚本耗尽后回退第一个合法动作。"""

    def __init__(self, script: Sequence[Action], policy_id: str = "scripted/v1") -> None:
        self._script = list(script)
        self.policy_id = policy_id

    def act(self, obs: dict, legal: Sequence[Action], rng: random.Random) -> Action:
        if self._script:
            want = self._script.pop(0)
            for a in legal:
                if a.digest() == want.digest():
                    return a
        return legal[0]
