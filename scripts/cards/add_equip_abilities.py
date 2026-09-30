# rq-4 一次性：为带 {{装配}} 关键词的 cardfx 装备卡批量插入 kind="equip" 的 AbilityDef。
# 费用符号由 .tmp/equip_fx.py 同款逻辑从卡片文本装配行抽取（生成时已人工核对输出）。
# 用法：python scripts/cards/add_equip_abilities.py   （幂等：已有 kind=equip 的卡跳过）
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from riftsim import cardfx  # noqa: E402
from riftsim.enums import Keyword  # noqa: E402

FX_DIR = ROOT / "src" / "riftsim" / "cardfx"
COLOR = {"红": "R", "蓝": "B", "绿": "G", "橙": "O", "黄": "Y", "紫": "P"}


def parse_equip_cost(line: str) -> tuple[str, ...]:
    seg = line.split("（")[0]
    body = re.sub(r"\{\{|\}\}", " ", seg).replace("装配", " ")
    out = list(re.findall(r"\d+", body))
    out += [en for zh, en in COLOR.items() if zh in body]
    return tuple(out)


def main() -> int:
    con = sqlite3.connect(f"file:{ROOT / 'cards_bilingual.db'}?mode=ro", uri=True)
    texts = dict(con.execute("SELECT card_key, text_cn FROM cards"))
    con.close()

    reg = cardfx.registry()
    targets = {}
    for k, fx in sorted(reg.items()):
        if Keyword.EQUIP not in fx["keywords"]:
            continue
        if any(ab.kind == "equip" for ab in fx["abilities"]):
            continue
        equip_line = next((ln for ln in (texts.get(k) or "").splitlines() if "装配" in ln), "")
        syms = parse_equip_cost(equip_line)
        if not syms:
            print(f"SKIP(费用抽取失败): {k}: {equip_line!r}")
            continue
        targets[k] = syms

    changed = 0
    for def_id, syms in targets.items():
        pat = re.compile(r'(card\("' + re.escape(def_id) + r'"[^)]*\n?)(\s*\))', re.S)
        ab = (
            ",\n    abilities=(\n"
            f'        AbilityDef(ability_id="{def_id}:equip:0", kind="equip", timing="action",\n'
            '                   rules_ref=("R-CR-818.1", "R-CR-818.1.b", "R-CR-818.1.c.2"),\n'
            f'                   cost_symbols={syms!r}, target_scope="unit"),\n'
            "    )"
        )
        for path in FX_DIR.glob("*.py"):
            t = path.read_text(encoding="utf-8")
            m = pat.search(t)
            if not m:
                continue
            # 在闭合右括号前插入 abilities 实参（单行/多行调用统一）
            new_t = t[:m.end() - len(m.group(2))] + ab + "\n" + m.group(2) + t[m.end():]
            path.write_text(new_t, encoding="utf-8")
            print(f"{def_id}: {syms}")
            changed += 1
            break
    print(f"changed: {changed}/{len(targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
