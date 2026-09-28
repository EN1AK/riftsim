"""riftsim —— 面向强化学习训练的《符文战场》规则驱动模拟器（阶段 3：最小核心引擎）。

依赖方向（AGENTS.md §4.1 / docs/architecture.md §2）：
    core（本包内除 rl/、trace 之外模块） → trace sink → runner → rl adapter → viewer
引擎核心为纯标准库实现，禁止 import 可视化/训练框架。
"""

from .version import (
    ENGINE_VERSION,
    RULESET_VERSION,
    TRACE_SCHEMA_VERSION,
    OBS_SCHEMA_VERSION,
    ACTION_LAYOUT_VERSION,
)

__all__ = [
    "ENGINE_VERSION",
    "RULESET_VERSION",
    "TRACE_SCHEMA_VERSION",
    "OBS_SCHEMA_VERSION",
    "ACTION_LAYOUT_VERSION",
]
