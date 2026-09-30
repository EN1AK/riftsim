# defs 效果面快照（保真基线/对照两用）：dump <out.json>
# 序列化每张卡的 keywords/keyword_values/abilities 关键字段，供 cardfx 切换前后 diff。
from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from riftsim.carddb import load_card_db  # noqa: E402


def main() -> int:
    out = Path(sys.argv[1])
    cdb = load_card_db(str(ROOT / "cards_bilingual.db"))
    data = {}
    for k, d in sorted(cdb.defs.items()):
        data[k] = {
            "keywords": sorted(x.value for x in d.keywords),
            "keyword_values": dict(sorted(d.keyword_values.items())),
            "abilities": [dataclasses.asdict(a) for a in d.abilities],
        }
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    print(f"dumped {len(data)} defs -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
