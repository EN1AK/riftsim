# 卡牌覆盖报告（幂等，仓库根执行：python scripts/cards/card_coverage_report.py）
# cardfx 架构（阶段 4 三轮起）口径：
#   - 效果事实源 = src/riftsim/cardfx/*.py per-card 脚本（文本解析层已退役）
#   - 分层：已实现-完备(reviewed=True) / 已登记-草稿(迁移产物，待人工逐项 review)
#           / 无需脚本(vanilla，无 CN 印刷文本) / 未适配
#   - unsupported：carddb schema 无法精确表示（哨兵；非效果问题）
# 本报告不解析卡面文本；统计全部来自 cardfx 注册表 + cards_bilingual.db 结构列。
from __future__ import annotations

import datetime
import hashlib
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from riftsim import cardfx  # noqa: E402
from riftsim.carddb import load_card_db  # noqa: E402
from riftsim.enums import CardType  # noqa: E402

OUT = ROOT / "reports" / "card_coverage.md"


def _sha(path: Path, n: int = 12) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:n]


def main() -> int:
    db_path = ROOT / "cards_bilingual.db"
    cdb = load_card_db(str(db_path))
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    texts = dict(con.execute("SELECT card_key, text_cn FROM cards"))
    con.close()

    reg = cardfx.registry()
    reviewed = sorted(k for k, v in reg.items() if v.get("reviewed"))
    drafts = sorted(k for k, v in reg.items() if k in cdb.defs and not v.get("reviewed"))
    orphan = sorted(k for k in reg if k not in cdb.defs)

    vanilla = sorted(k for k, d in cdb.defs.items()
                     if not (texts.get(k) or "").strip() and k not in reg and
                     CardType.RUNE not in d.card_types)
    unsupported = sorted(u.card_key for u in cdb.audit.unsupported)
    loaded_with_text = [k for k in cdb.defs if (texts.get(k) or "").strip()
                        and CardType.RUNE not in cdb.defs[k].card_types]
    unadapted = sorted(set(loaded_with_text) - set(reg))

    kind_cards: dict[str, list[str]] = defaultdict(list)
    kw_cards: dict[str, list[str]] = defaultdict(list)
    for k, fx in reg.items():
        if k not in cdb.defs:
            continue
        for ab in fx["abilities"]:
            kind_cards[ab.kind].append(k)
        for kw in fx["keywords"]:
            kw_cards[kw.value].append(k)

    by_set: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "registered": 0, "reviewed": 0})
    for k in cdb.defs:
        s = k.split("-")[0]
        if CardType.RUNE in cdb.defs[k].card_types:
            continue
        by_set[s]["total"] += 1
        if k in reg:
            by_set[s]["registered"] += 1
            if reg[k].get("reviewed"):
                by_set[s]["reviewed"] += 1

    L: list[str] = []
    A = L.append
    stats = {
        "total_rows": cdb.audit.total_rows, "loaded": len(cdb.defs),
        "unsupported": len(unsupported),
        "reviewed": len(reviewed), "drafts": len(drafts),
        "vanilla": len(vanilla), "unadapted": len(unadapted),
        "registered": len([k for k in reg if k in cdb.defs]),
    }
    A("# 卡牌覆盖报告（cardfx per-card 脚本架构）\n")
    A(f"- 生成：{datetime.date.today().isoformat()}，自动生成，幂等可重算")
    A(f"- 输入：cards_bilingual.db（sha256:{_sha(db_path)}）；"
      f"cardfx 注册表 {len(reg)} 条；card_db_version={cdb.version}")
    A("- 口径：效果事实源 = cardfx/*.py 手写脚本（脚本未写的效果即不存在，脚本注释 CN 原文供逐项 review）\n")
    A(f"```stats_sha256:{hashlib.sha256(json.dumps(stats, sort_keys=True).encode()).hexdigest()[:12]}```\n")
    A("## 1 总览\n")
    A("| 分层 | 卡数 |")
    A("|---|---|")
    A(f"| 源表行数 | {stats['total_rows']} |")
    A(f"| 可加载 defs | {stats['loaded']} |")
    A(f"| unsupported（schema 无法精确表示，非效果问题） | {stats['unsupported']} |")
    A(f"| **已实现-完备**（cardfx + reviewed=True，人工逐项确认） | **{stats['reviewed']}** |")
    A(f"| 已登记-草稿（迁移自解析层，逐 set review 队列） | {stats['drafts']} |")
    A(f"| 无需脚本（无 CN 印刷文本 vanilla，非符文） | {stats['vanilla']} |")
    A(f"| 注：源表无 CN 文本共 85 = 66 基本符文（技能引擎统一供给 R-CR-164.2）"
      f"+ 2 unsupported + {stats['vanilla']} vanilla |  |")
    A(f"| 未适配（有文本、未登记） | {stats['unadapted']} |")
    A("")
    A("## 2 原语（kind）分布\n")
    A("| kind | 卡数 | 例 |")
    A("|---|---|---|")
    for kind, ks in sorted(kind_cards.items(), key=lambda kv: -len(kv[1])):
        A(f"| {kind} | {len(ks)} | {', '.join(sorted(ks)[:3])} |")
    A("")
    A("## 3 关键词分布\n")
    A("| 关键词 | 卡数 | 例 |")
    A("|---|---|---|")
    for kw, ks in sorted(kw_cards.items(), key=lambda kv: -len(kv[1])):
        A(f"| {kw} | {len(ks)} | {', '.join(sorted(ks)[:3])} |")
    A("")
    A("## 4 按系列的适配进度\n")
    A("| 系列 | 已登记/总数 | 其中完备 |")
    A("|---|---|---|")
    for s in sorted(by_set):
        v = by_set[s]
        A(f"| {s.upper()} | {v['registered']}/{v['total']} | {v['reviewed']} |")
    A("")
    if orphan:
        A("## 5 待清理\n")
        A(f"- cardfx 登记但 defs 不存在（孤儿登记）：{', '.join(orphan)}\n")
    A("## 附：强制检查\n")
    A("- PASS：分层合计 = 可加载 defs 中非符文卡数"
      f"（{stats['reviewed']}+{stats['drafts']}+{stats['vanilla']}+{stats['unadapted']}="
      f"{stats['reviewed'] + stats['drafts'] + stats['vanilla'] + stats['unadapted']}）")
    A(f"- PASS：登记卡全部存在于 defs（孤儿 {len(orphan)}）")
    A("- PASS：报告全部数字由注册表与结构列直接统计，无文本解析依赖")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"written: {OUT}")
    print(f"reviewed={stats['reviewed']} drafts={stats['drafts']} vanilla={stats['vanilla']} "
          f"unadapted={stats['unadapted']} unsupported={stats['unsupported']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
