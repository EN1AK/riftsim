# 错误类型（docs/api_contract.md §1/§9）
from __future__ import annotations


class RiftError(Exception):
    """引擎基础错误。"""


class IllegalActionError(RiftError):
    """非法动作：状态不得被修改（docs/api_contract.md §9，T-0037 等）。

    reason 必须含规则出处（rule_id 或机制名），供 trace 与调试归因。
    """

    def __init__(
        self,
        step_id: int,
        player: int,
        action_digest: str,
        reason: str,
        legal_digest: str = "",
    ) -> None:
        self.step_id = step_id
        self.player = player
        self.action_digest = action_digest
        self.reason = reason
        self.legal_digest = legal_digest
        super().__init__(
            f"IllegalAction(step={step_id}, player={player}, action={action_digest}): {reason}"
        )


class DeckValidationError(RiftError):
    """组卡校验失败（R-CR-101..103，T-0001..T-0006）。"""

    def __init__(self, violations: list[str]) -> None:
        self.violations = violations
        super().__init__("Deck invalid: " + "; ".join(violations))


class EngineInvariantError(RiftError):
    """引擎内部不变量被破坏（属 bug；runner 捕获后导出最小复现，T-0131 流程）。"""


class ReplayMismatchError(RiftError):
    """replay 与 trace 记录的状态哈希不一致（T-0131/0132）。"""

    def __init__(self, step_id: int, expected: str, actual: str) -> None:
        self.step_id = step_id
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"Replay mismatch at step {step_id}: expected {expected}, got {actual}"
        )


class TraceFormatError(RiftError):
    """trace 文件损坏/不兼容（docs/visualization_spec.md §2.6）。"""
