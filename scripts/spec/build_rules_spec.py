#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""阶段 1 生成器：spec/rule_semantics.yaml + workspace/rules_work.db -> spec/rules_spec.yaml

用法（仓库根目录）：
    python scripts/spec/build_rules_spec.py            # 校验 + 生成
    python scripts/spec/build_rules_spec.py --check    # 仅校验（含覆盖完整性/引用完整性）

校验项：
 1) 语义层 YAML 可解析；mechanism_id 唯一；tier 合法；dependencies 引用存在
 2) covers 区间语法合法、无重叠，且覆盖 workspace/rules_work.db 中全部 R-CR-* 规则
 3) 每条规则的来源可定位（evidence 存在；文件路径存在性给出警告）
 4) MVP tier 的行为规则（legality/transition 非空）具备 test_ids 或所属机制提供 test_hints
产出：
  spec/rules_spec.yaml（AGENTS.md 阶段 1 字段：rule_id/title/source/prerequisites/
  legality/transition/timing/exceptions/dependencies/test_ids/status + tier/mechanism_ref）
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "workspace" / "rules_work.db"
SEM_PATH = ROOT / "spec" / "rule_semantics.yaml"
OUT_PATH = ROOT / "spec" / "rules_spec.yaml"
MATRIX_PATH = ROOT / "spec" / "rule_test_matrix.md"
UNRESOLVED_PATH = ROOT / "docs" / "unresolved_rules.md"

TIERS = {"MVP", "P1", "P2", "OUT"}
AUTHORITY_MAP = {"rule": "core_rules", "errata": "errata", "faq": "faq"}
# 主来源层级：zh 核心规则 > en 核心规则 > 勘误 > FAQ > 其他
SOURCE_RANK = {"source_009": 0, "source_018": 1}
TYPE_RANK = {"rule": 2, "errata": 3, "faq": 4}
LANG_DIR = {"zh": "loltcg_pdfs", "en": "riftbound_en_rules"}

COVERS_RE = re.compile(r"^R-CR-([A-Z]+|\d+)\.\.R-CR-([A-Z]+|\d+)$")
TEST_HEAD_RE = re.compile(r"^###\s+(T-\d+)\b", re.M)
TEST_RULES_RE = re.compile(r"^-\s*rules?:\s*(.+)$", re.M)
UNRESOLVED_RE = re.compile(r"^-\s*rule_ids?:\s*(.+)$", re.M)


class NoAliasDumper(yaml.SafeDumper):
    """禁用 YAML 别名/锚点（共享引用导致 *idNNN），保证输出可 grep/diff。"""

    def ignore_aliases(self, data):
        return True


def main_key(rule_id: str) -> str:
    """R-CR-315.1.a -> '315'；R-CR-FRONT -> 'FRONT'。"""
    rest = rule_id.split("-", 2)[2]
    return rest.split(".")[0]


def parse_covers(cov: str) -> tuple[str, str]:
    m = COVERS_RE.match(cov.strip())
    if not m:
        raise ValueError(f"covers 语法非法: {cov!r}（应为 R-CR-A..R-CR-B）")
    return m.group(1), m.group(2)


def in_range(head: str, lo: str, hi: str) -> bool:
    if lo == "FRONT" or hi == "FRONT":
        return head == "FRONT" and lo == hi == "FRONT"
    if not head.isdigit():
        return False
    return int(lo) <= int(head) <= int(hi)


def load_semantics() -> dict:
    with SEM_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_rules() -> list[sqlite3.Row]:
    con = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT rule_id, topic, proposed_canonical_rule, status FROM rules"
    ).fetchall()
    con.close()
    return rows


def load_sources(rule_ids: list[str]) -> dict[str, list[sqlite3.Row]]:
    """rule_id -> evidence rows（含 relationship）。"""
    con = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    out: dict[str, list[sqlite3.Row]] = {rid: [] for rid in rule_ids}
    # 常量表达式占位符分批，避免变量数上限
    batch = 500
    for i in range(0, len(rule_ids), batch):
        part = rule_ids[i : i + batch]
        q = ",".join("?" * len(part))
        for r in con.execute(
            "SELECT re.rule_id, re.relationship, e.source_id, e.source_type,"
            " e.source_language, e.source_document, e.version, e.date, e.page,"
            " e.section, e.heading, e.rule_number"
            " FROM rule_evidence re JOIN evidence e ON re.evidence_id = e.evidence_id"
            f" WHERE re.rule_id IN ({q})",
            part,
        ):
            out[r["rule_id"]].append(r)
    con.close()
    return out


def pick_primary(evs: list[sqlite3.Row]) -> sqlite3.Row | None:
    if not evs:
        return None

    def rank(r: sqlite3.Row) -> tuple:
        rel = 0 if r["relationship"] == "same" else 1
        src = SOURCE_RANK.get(r["source_id"], TYPE_RANK.get(r["source_type"], 5))
        lang = 0 if r["source_language"] == "zh" else 1
        return (rel, src, lang)

    return sorted(evs, key=rank)[0]


def build_source_block(evs: list[sqlite3.Row], warnings: list[str], rid: str) -> tuple[dict, list[dict]]:
    prim = pick_primary(evs)
    if prim is None:
        warnings.append(f"{rid}: 无任何 evidence，source 置 null")
        return None, []
    doc = prim["source_document"] or ""
    lang = prim["source_language"] or "zh"
    path = f"{LANG_DIR.get(lang, 'loltcg_pdfs')}/{doc}" if doc else None
    if path and not (ROOT / path).exists():
        warnings.append(f"{rid}: source 文件未找到 {path}（仍记录）")
    loc_parts = []
    if prim["section"]:
        loc_parts.append(str(prim["section"]))
    if prim["rule_number"]:
        loc_parts.append(f"rule {prim['rule_number']}")
    if prim["heading"]:
        loc_parts.append(str(prim["heading"]))
    if prim["page"] is not None:
        loc_parts.append(f"p.{prim['page']}")
    stype = prim["source_type"] or ""
    source = {
        "path": path,
        "location": " / ".join(loc_parts) if loc_parts else None,
        "version": f"{prim['version']} / {prim['date']}"
        if prim["version"] or prim["date"]
        else None,
        "authority": AUTHORITY_MAP.get(stype, stype or None),
        "language": lang,
    }
    seen, extra = set(), []
    for r in evs:
        if r is prim:
            continue
        key = (r["source_id"], r["rule_number"], r["page"])
        if key in seen:
            continue
        seen.add(key)
        if r["source_type"] in ("errata", "faq"):
            extra.append(
                {
                    "source_id": r["source_id"],
                    "authority": AUTHORITY_MAP[r["source_type"]],
                    "date": r["date"],
                }
            )
        if len(extra) >= 5:
            break
    return source, extra


def make_title(canon: str | None, topic: str | None) -> str:
    if canon:
        first = canon.strip().split("\n", 1)[0]
        first = re.split(r"(?<=[。；])", first)[0] or first
        return first[:60]
    return (topic or "").strip()[:60]


def load_test_mapping() -> dict[str, list[str]]:
    """从 rule_test_matrix.md 提取 rule_id -> [T-xxxx]。文件不存在返回空映射。"""
    if not MATRIX_PATH.exists():
        return {}
    text = MATRIX_PATH.read_text(encoding="utf-8")
    mapping: dict[str, list[str]] = {}
    heads = list(TEST_HEAD_RE.finditer(text))
    for i, h in enumerate(heads):
        tid = h.group(1)
        seg = text[h.end() : heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        m = TEST_RULES_RE.search(seg)
        if not m:
            continue
        for rid in re.split(r"[,，;；]", m.group(1)):
            rid = rid.strip().strip("`")
            if rid:
                mapping.setdefault(rid, []).append(tid)
    return mapping


def load_unresolved(valid_ids: set[str]) -> set[str]:
    """解析 docs/unresolved_rules.md 的 rule_id 行；仅保留真实存在的 rule_id，
    过滤文档模板/示例产生的畸形捕获。"""
    if not UNRESOLVED_PATH.exists():
        return set()
    text = UNRESOLVED_PATH.read_text(encoding="utf-8")
    ids: set[str] = set()
    for m in UNRESOLVED_RE.finditer(text):
        for rid in re.split(r"[,，;；]", m.group(1)):
            rid = rid.strip().strip("`")
            if rid in valid_ids:
                ids.add(rid)
    return ids


def main() -> int:
    check_only = "--check" in sys.argv
    errors: list[str] = []
    warnings: list[str] = []

    sem = load_semantics()
    mechs = sem.get("mechanisms", [])
    meta = sem.get("meta", {})

    # --- 语义层结构校验 ---
    seen_ids: set[str] = set()
    mech_by_id = {}
    for m in mechs:
        mid = m.get("mechanism_id")
        if not mid:
            errors.append("存在缺 mechanism_id 的机制条目")
            continue
        if mid in seen_ids:
            errors.append(f"mechanism_id 重复: {mid}")
        seen_ids.add(mid)
        mech_by_id[mid] = m
        if m.get("tier") not in TIERS:
            errors.append(f"{mid}: tier 非法 {m.get('tier')!r}")
        if not m.get("covers"):
            errors.append(f"{mid}: 缺少 covers")
    for m in mechs:
        for dep in (m.get("semantics") or {}).get("dependencies") or []:
            if dep not in seen_ids:
                errors.append(f"{m['mechanism_id']}: dependencies 引用不存在的机制 {dep}")

    # --- covers 展开与覆盖校验 ---
    rule_rows = load_rules()
    rid_set = {r["rule_id"] for r in rule_rows}
    rcr_ids = sorted(r for r in rid_set if r.startswith("R-CR-"))

    cover_map: dict[str, str] = {}  # rule_id -> mechanism_id
    for m in mechs:
        for cov in m.get("covers") or []:
            try:
                lo, hi = parse_covers(cov)
            except ValueError as e:
                errors.append(str(e))
                continue
            matched = [rid for rid in rcr_ids if in_range(main_key(rid), lo, hi)]
            if not matched:
                errors.append(f"{m['mechanism_id']}: covers {cov} 未匹配任何规则")
            for rid in matched:
                if rid in cover_map:
                    errors.append(
                        f"covers 重叠: {rid} 同时属 {cover_map[rid]} 与 {m['mechanism_id']}"
                    )
                cover_map[rid] = m["mechanism_id"]

    uncovered = [rid for rid in rcr_ids if rid not in cover_map]
    if uncovered:
        heads = sorted({main_key(r) for r in uncovered})
        errors.append(
            f"R-CR 覆盖不完整: {len(uncovered)} 条未覆盖，主编号段: {', '.join(heads[:20])}"
        )

    # --- 来源装配 ---
    all_ids = sorted(rid_set)
    src_map = load_sources(all_ids)

    test_map_raw = load_test_mapping()
    # 案例引用的规则按前缀展开：引 R-CR-465.2 即覆盖 R-CR-465.2 及其全部子条款
    test_map: dict[str, list[str]] = {}
    for ref, tids in test_map_raw.items():
        for rid in all_ids:
            if rid == ref or rid.startswith(ref + "."):
                test_map.setdefault(rid, [])
                for t in tids:
                    if t not in test_map[rid]:
                        test_map[rid].append(t)
    unresolved = load_unresolved(rid_set)

    # --- MVP 行为规则测试锚点校验 ---
    mvp_untested = []
    for rid in rcr_ids:
        mid = cover_map.get(rid)
        mech = mech_by_id.get(mid) if mid else None
        if not mech or mech.get("tier") != "MVP":
            continue
        sems = mech.get("semantics") or {}
        has_semantics = bool(sems.get("legality") or sems.get("transition"))
        if has_semantics and not test_map.get(rid) and not mech.get("test_hints"):
            mvp_untested.append(rid)
    if mvp_untested and MATRIX_PATH.exists():
        heads = sorted({main_key(r) for r in mvp_untested})
        warnings.append(
            f"MVP 行为规则缺测试锚点: {len(mvp_untested)} 条，主编号段: {', '.join(heads[:20])}"
        )

    # --- 汇总规则条目 ---
    rules_out = []
    tier_count: dict[str, int] = {}
    status_count: dict[str, int] = {}
    for row in rule_rows:
        rid = row["rule_id"]
        prefix = rid.split("-", 2)[1] if rid.count("-") >= 2 else ""
        if prefix in ("TOPIC", "ER", "FAQ", "MISC"):
            # 主题聚合条/勘误与FAQ前言/未归组条目桶：无可执行规则语义
            tier, status, mech_id = "meta", "verified", None
            sems = {"prerequisites": None, "legality": None, "transition": None,
                    "timing": None, "exceptions": [], "dependencies": []}
        elif prefix == "CARD":
            tier, status, mech_id = "cards", "deferred", None
            sems = {"prerequisites": None, "legality": None, "transition": None,
                    "timing": None, "exceptions": [], "dependencies": []}
        else:
            mech_id = cover_map.get(rid)
            mech = mech_by_id.get(mech_id) if mech_id else {}
            tier = mech.get("tier", "?")
            status = "ambiguous" if rid in unresolved else "verified"
            sems = mech.get("semantics") or {}
        source, extra = build_source_block(src_map.get(rid, []), warnings, rid)
        entry = {
            "rule_id": rid,
            "title": make_title(row["proposed_canonical_rule"], row["topic"]),
            "tier": tier,
            "status": status,
            "mechanism_ref": mech_id,
            "source": source,
            "additional_sources": extra,
            "prerequisites": sems.get("prerequisites"),
            "legality": sems.get("legality"),
            "transition": sems.get("transition"),
            "timing": sems.get("timing"),
            "exceptions": sems.get("exceptions") or [],
            "dependencies": sems.get("dependencies") or [],
            "test_ids": test_map.get(rid, []),
        }
        rules_out.append(entry)
        tier_count[tier] = tier_count.get(tier, 0) + 1
        status_count[status] = status_count.get(status, 0) + 1

    # --- 报告 ---
    print(f"机制条目: {len(mechs)}")
    print(f"规则总数: {len(rules_out)}  tier 分布: {tier_count}")
    print(f"status 分布: {status_count}")
    print(f"测试映射: {len(test_map)} 条规则已关联案例（矩阵文件{'存在' if MATRIX_PATH.exists() else '缺失'}）")
    print(f"未决歧义: {len(unresolved)} 条规则标记")
    for w in warnings:
        print(f"[WARN] {w}")
    for e in errors:
        print(f"[ERR ] {e}")

    if errors:
        print(f"\n校验失败：{len(errors)} 项错误。未写出 spec/rules_spec.yaml。")
        return 1
    if check_only:
        print("\n--check 模式：校验通过，未写出文件。")
        return 0

    doc = {
        "meta": {
            "schema": "riftsim.rules_spec/v1",
            "ruleset_version": meta.get("ruleset_version"),
            "generated_by": "scripts/spec/build_rules_spec.py",
            "mechanism_source": "spec/rule_semantics.yaml",
            "rule_count": len(rules_out),
            "tiers": tier_count,
        },
        "rules": rules_out,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        yaml.dump(doc, f, Dumper=NoAliasDumper, allow_unicode=True, sort_keys=False, width=120)
    print(f"\n已写出: {OUT_PATH.relative_to(ROOT)}（{OUT_PATH.stat().st_size / 1024:.0f} KB）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
