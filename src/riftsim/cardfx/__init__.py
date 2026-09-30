# cardfx：per-card 效果脚本注册表（阶段 4 三轮起：效果事实源，替代 effects.py 运行时解析）。
#
# 架构约定（ygopro 式分工 + AGENTS.md §2 特殊效果适配层）：
# - 引擎仍是合法动作唯一聚合者（目标枚举/费用/掩码/横切规则注入位不变）；
#   脚本只声明效果面数据：keywords / keyword_values / abilities。
# - abilities 的 kind 复用引擎原语结算（spell_damage/spell_draw/on_play_draw/…）；
#   白名单表达不了的孤例用 AbilityDef.resolve_fn 命名回调（本包 RESOLVERS）。
# - 命名注册是唯一事实载体：GameState/快照/trace 只携带 def_id 与字符串 key，
#   函数体不进序列化，回放与克隆不受影响。
# - 每个脚本必须带规则锚点（rules_ref）与卡面原文注释（CN 权威；EN 差异注记）。
from __future__ import annotations

import importlib
import pkgutil
from dataclasses import replace
from typing import Callable

from ..cards import AbilityDef, CardDefinition

# def_id -> {"keywords": frozenset, "keyword_values": dict, "abilities": tuple}
_FX: dict[str, dict] = {}
# 命名结算回调：key -> fn(state, item, ability)
RESOLVERS: dict[str, Callable] = {}

_loaded = False


def card(def_id: str, *, keywords=(), keyword_values=None, abilities=(), reviewed: bool = False) -> None:
    """登记一张卡的效果面（事实源）。重复登记直接报错（防静默覆盖）。
    reviewed=True 表示人工对照 CN 原文逐项确认效果面完备（覆盖报告「已适配-完备」档）。"""
    if def_id in _FX:
        raise ValueError(f"cardfx duplicate registration: {def_id}")
    _FX[def_id] = {
        "keywords": frozenset(keywords),
        "keyword_values": dict(keyword_values or {}),
        "abilities": tuple(abilities),
        "reviewed": reviewed,
    }


def resolver(key: str) -> Callable:
    """注册命名结算回调：fn(state, item, ability_dict) -> None（item=ChainItem）。"""
    def deco(fn: Callable) -> Callable:
        if key in RESOLVERS:
            raise ValueError(f"cardfx duplicate resolver: {key}")
        RESOLVERS[key] = fn
        return fn
    return deco


def _ensure_loaded() -> None:
    global _loaded
    if _loaded:
        return
    _loaded = True
    for m in pkgutil.iter_modules(__path__):
        if not m.name.startswith("_"):
            importlib.import_module(f"{__name__}.{m.name}")


def fx_for(def_id: str) -> dict | None:
    _ensure_loaded()
    return _FX.get(def_id)


def resolver_for(key: str) -> Callable:
    _ensure_loaded()
    try:
        return RESOLVERS[key]
    except KeyError:
        raise KeyError(f"cardfx resolver not registered: {key}") from None


def apply_fx(d: CardDefinition) -> CardDefinition:
    """把登记的效果面覆盖到 carddb 产出的静态定义上（无登记=vanilla，效果空）。"""
    fx = fx_for(d.def_id)
    if fx is None:
        return d
    return replace(
        d,
        keywords=fx["keywords"],
        keyword_values=fx["keyword_values"],
        abilities=fx["abilities"],
    )


def registered_count() -> int:
    _ensure_loaded()
    return len(_FX)


def registry() -> dict[str, dict]:
    """只读登记簿视图（覆盖报告统计用）。"""
    _ensure_loaded()
    return dict(_FX)


__all__ = [
    "AbilityDef", "RESOLVERS", "apply_fx", "card", "fx_for",
    "registered_count", "resolver", "resolver_for",
]
