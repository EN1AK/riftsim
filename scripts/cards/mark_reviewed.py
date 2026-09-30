# cardfx 批量标 reviewed（一次性工具；用法：python scripts/cards/mark_reviewed.py <def_id 清单文件>)
# 对 cardfx/*.py 中 card("ID", ...) 调用在 def_id 实参后插入 reviewed=True（幂等：已有则不重复）。
# 只改文本；语义确认由调用方在清单生成前完成（.tmp/batch1_marking.py 之类）。
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FX = ROOT / "src" / "riftsim" / "cardfx"


def main() -> int:
    ids = [ln.strip() for ln in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
           if ln.strip() and not ln.startswith("#")]
    if not ids:
        print("empty list")
        return 1
    hit, already, missing = [], [], []
    for def_id in ids:
        pat = re.compile(r'card\("' + re.escape(def_id) + r'"')
        found = False
        for path in FX.glob("*.py"):
            t = path.read_text(encoding="utf-8")
            m = pat.search(t)
            if not m:
                continue
            found = True
            seg = t[m.start():m.start() + 120]
            if "reviewed=" in seg.split("(", 2)[-1][:40]:
                already.append(def_id)
                continue
            # 在 card("ID" 之后插入 reviewed=True,（兼容有/无后续实参两种形态）
            new_t = t[:m.end()] + ", reviewed=True" + t[m.end():]
            path.write_text(new_t, encoding="utf-8")
            hit.append(def_id)
        if not found:
            missing.append(def_id)
    print(f"marked: {len(hit)} already: {len(already)} missing: {len(missing)}")
    if already:
        print("already:", already)
    if missing:
        print("MISSING (无 card() 登记):", missing)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
