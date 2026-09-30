# trace 复验器（docs/visualization_spec.md §3.6 对应检查；VM-1 自动化证据）
# 与 viewer/index.html 内置「加载即复验」逻辑同规则：
#   1) 文件结构：首行 header（schema_version 主版本兼容 rifttrace/1）、末行 footer；
#   2) hash 链：事件按文件序把连续相同 (before,after) 对视为同一步级转移，
#      相邻转移之间要求 after == 下一个 before；任一侧 hash 为 null 跳过该段；
#   3) chosen∈legal：每个 decision 的 chosen_action_id 字符串 ∈ legal_action_ids；
#   4) completeness：footer.trace_completeness.ok，且 expected/written/实际事件数一致。
# 任一检查失败则该文件 FAIL，全部通过 exit 0，否则 exit 1。
from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

SCHEMA_MAJOR_OK = "rifttrace/1"  # 兼容主版本（§2.6：未知主版本拒绝读取）


def _schema_ok(v: object) -> bool:
    if not isinstance(v, str) or not v.startswith("rifttrace/"):
        return False
    try:
        major = int(v.split("/", 1)[1].split(".", 1)[0])
    except ValueError:
        return False
    return major == 1


def check_file(path: Path) -> list[str]:
    """返回问题列表；空列表 = 通过。"""
    issues: list[str] = []
    records: list[dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for ln, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:  # noqa: PERF203
                issues.append(f"第 {ln} 行 JSON 解析失败: {e}")
    if issues:
        return issues

    # --- 结构 ---
    if not records or records[0].get("type") != "header":
        issues.append("首行不是 header 记录")
    else:
        sv = records[0].get("schema_version")
        if not _schema_ok(sv):
            issues.append(f"不支持的 schema_version: {sv!r}（本校验器仅兼容 rifttrace/1.x）")
    if not records or records[-1].get("type") != "footer":
        issues.append("末行不是 footer 记录")
    footer = records[-1] if records and records[-1].get("type") == "footer" else None

    events = [r for r in records if r.get("type") == "event"]
    decisions = [r for r in records if r.get("type") == "decision"]

    # --- hash 链（步级转移边界） ---
    prev_group_after: str | None = None
    prev_group_key: tuple | None = None
    checked = skipped = broken = 0
    for e in events:
        key = (e.get("before_state_hash"), e.get("after_state_hash"))
        if key == prev_group_key:  # 同一转移内（多事件共享步级哈希）
            continue
        b, a = key
        if prev_group_key is not None:
            if prev_group_after is None or b is None:
                skipped += 1
            elif prev_group_after != b:
                broken += 1
                if broken <= 3:
                    issues.append(
                        f"hash 链断裂: event_seq={e.get('event_seq')} 的 before "
                        f"!= 上一转移 after（{str(prev_group_after)[:12]}… != {str(b)[:12]}…）"
                    )
            else:
                checked += 1
        prev_group_key, prev_group_after = key, a
    if broken > 3:
        issues.append(f"hash 链断裂共 {broken} 段")

    # --- chosen ∈ legal（字符串相等） ---
    bad_dec = 0
    for d in decisions:
        legal = d.get("legal_action_ids")
        chosen = d.get("chosen_action_id")
        if not isinstance(legal, list) or chosen not in legal:
            bad_dec += 1
            if bad_dec <= 3:
                issues.append(f"决策 step_id={d.get('step_id')}: chosen_action_id 不在 legal_action_ids 中")
    if bad_dec > 3:
        issues.append(f"chosen∉legal 决策共 {bad_dec} 个")

    # --- completeness ---
    if footer is None:
        issues.append("缺少 footer，无法核验 completeness")
    else:
        comp = footer.get("trace_completeness") or {}
        if not comp.get("ok"):
            issues.append(f"trace_completeness.ok = {comp.get('ok')!r}")
        expected = comp.get("expected_events")
        written = comp.get("written_events")
        if expected is not None and len(events) != expected:
            issues.append(f"实际事件数 {len(events)} != expected_events {expected}")
        if written is not None and expected is not None and written != expected:
            issues.append(f"written_events {written} != expected_events {expected}")

    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description="rifttrace/1 回放一致性复验器（viewer_check）")
    ap.add_argument("files", nargs="*", help="trace .jsonl 文件；缺省为 runs/fixtures/*.jsonl")
    args = ap.parse_args()

    if args.files:
        paths = [Path(p) for p in args.files]
    else:
        root = Path(__file__).resolve().parent.parent
        paths = sorted(Path(p) for p in glob.glob(str(root / "runs" / "fixtures" / "*.jsonl")))
    if not paths:
        print("未找到 trace 文件", file=sys.stderr)
        return 1

    all_ok = True
    for p in paths:
        if not p.is_file():
            print(f"[FAIL] {p}: 文件不存在")
            all_ok = False
            continue
        issues = check_file(p)
        try:
            with p.open("r", encoding="utf-8") as fh:
                header = json.loads(fh.readline())
            mid = header.get("match_id", "?")
        except Exception:
            mid = "?"
        if issues:
            all_ok = False
            print(f"[FAIL] {p.name} (match_id={mid})")
            for it in issues:
                print(f"   - {it}")
        else:
            print(f"[PASS] {p.name} (match_id={mid}) schema/hash链/completeness/chosen∈legal 全部通过")
    print("=" * 60)
    print("总体: " + ("PASS" if all_ok else "FAIL"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
