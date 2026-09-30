# cardfx 登记审计测试（阶段 4 三轮起；AGENTS.md「无 reviewed 无测试不计完备」的防呆约束）
from pathlib import Path

import pytest

from riftsim import cardfx
from riftsim.carddb import load_card_db
from riftsim.enums import Keyword

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "cards_bilingual.db"

pytestmark = pytest.mark.skipif(not DB.exists(), reason="cards_bilingual.db 不在仓库根目录")

# 引擎已接线关键词（enums.Keyword 注释口径；batch1 批量标记以此为界）
WIRED_KEYWORDS = {
    Keyword.ACCELERATE, Keyword.ACTION, Keyword.ASSAULT, Keyword.DEFLECT,
    Keyword.GANKING, Keyword.HIDDEN, Keyword.REACTION, Keyword.SHIELD,
    Keyword.TANK, Keyword.TEMPORARY, Keyword.VISION, Keyword.AMBUSH,
    Keyword.UNIQUE, Keyword.BACKLINE,
    Keyword.EQUIP,  # rq-4：818 装配（场上主动技能）+ 819 灵便（反应时机+打出触发贴附）
    Keyword.QUICKDRAW,
}


@pytest.fixture(scope="module")
def reg():
    return cardfx.registry()


def test_no_orphan_registration(reg):
    """cardfx 登记的 def_id 必须全部存在于 carddb defs（孤儿登记=静默失效）。"""
    defs = load_card_db(str(DB)).defs
    orphan = sorted(k for k in reg if k not in defs)
    assert orphan == []


def test_reviewed_keywords_all_wired(reg):
    """reviewed=完备卡的关键词必须全部已接线（未接线机制的卡不得标完备）。"""
    bad = sorted(k for k, fx in reg.items()
                 if fx.get("reviewed") and not set(fx["keywords"]) <= WIRED_KEYWORDS)
    assert bad == []


def test_reviewed_ids_unique_and_nonempty(reg):
    """reviewed 集合非空且 def_id 全局唯一（重复登记在 card() 处已 raise，双保险）。"""
    reviewed = [k for k, fx in reg.items() if fx.get("reviewed")]
    assert len(reviewed) >= 30  # batch1(28) + fx-4 手写(6) 之后的下限（只增不减）
    assert len(reviewed) == len(set(reviewed))


def test_reviewed_has_no_unwired_effect_lines(reg):
    """防呆（rq-1a 失误 + rift 数据缺陷修复后升级，2026-09-30）：reviewed 卡的卡面若含
    非关键词效果行（strip 后非空），必须有 abilities 登记或属 819 触发关键词行。
    英文侧用独立白名单放行**关键词提示行**（如 [Assault 2] (+2...)/Ganking (...)/
    Deathknell (...)）与**类别声明行**（如 "I am a Mech."）、**等级条件提示（Level N[>])**；
    其余 strip 仍有内容的行一律视为未接线效果行而失败——CN/EN 双语双侧都查。"""
    import re
    import sqlite3

    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    texts_cn = dict(con.execute("SELECT card_key, text_cn FROM cards"))
    texts_en = dict(con.execute("SELECT card_key, text_en FROM cards"))
    con.close()

    # —— CN 侧审计（原判定）——
    bad_cn: list[str] = []
    for k, fx in reg.items():
        if not fx.get("reviewed"):
            continue
        for ln in (ln.strip() for ln in (texts_cn.get(k) or "").splitlines() if ln.strip()):
            stripped = re.sub(r"\{\{[^}]*\}\}", "", ln)
            stripped = re.sub(r"（[^）]*）", "", stripped)
            stripped = re.sub(r"\([^)]*\)", "", stripped)
            if not stripped.strip():
                continue
            if not fx["abilities"] and Keyword.QUICKDRAW not in fx["keywords"]:
                bad_cn.append(f"{k}: {ln}")
                break
    assert not bad_cn, "reviewed 卡 CN 侧存在未接线效果行：" + "; ".join(bad_cn)

    # —— EN 侧审计（rift 数据修复后补齐）——
    EN_REMINDER = re.compile(
        r"^("
        r"(I am a (?:an? )?(?:Mech|Unit|Gear)\.?)"  # 类别声明
        r"|(Ganking|Tanking?|Tank\b|Deflect( \d+)?|Assault( \d+)?|Shield( \d+)?|"
        r"Vision|Hunt|Deathknell|Weaponmaster|Quick-Draw|Reaction|Action|Ambush|"
        r"Hidden|Temporary|Backline|Accelerate|Unique|Empower|Flow|Burn( \d+)?|"
        r"Level( \d+)?|Repeat( \d+)?|Equip)\b"  # 关键词提示
        r")", re.IGNORECASE,
    )
    EN_CATEGORY_WHITELIST = {
        # 单独列出的类别/提示行（与 fx.keywords 一一对应，已按提示行处理）
        ("SFD-073", "I am a Mech."),
    }

    bad_en: list[str] = []
    for k, fx in reg.items():
        if not fx.get("reviewed"):
            continue
        for ln in (ln.strip() for ln in (texts_en.get(k) or "").splitlines() if ln.strip()):
            if EN_REMINDER.match(ln):
                continue
            if (k, ln) in EN_CATEGORY_WHITELIST:
                continue
            s = re.sub(r"\[[^\]]*\]", "", ln)
            s = re.sub(r":rb_[a-z_]+:", "", s)
            s = re.sub(r"\([^)]*\)", "", s)
            s = s.strip().strip(",").strip()
            if not s:
                continue
            if not fx["abilities"] and Keyword.QUICKDRAW not in fx["keywords"]:
                bad_en.append(f"{k}: {ln}")
                break
    assert not bad_en, "reviewed 卡 EN 侧存在未接线效果行：" + "; ".join(bad_en)


def test_reviewed_comment_lines_all_covered(reg):
    """reviewed 卡的 CN 原文行必须可归入两类：关键词/提醒行，或有 abilities 结算的效果行。
    判定与 .tmp/batch1_marking.py 相同的行级启发式；防「漏标行」静默进完备档。"""
    import re
    import sqlite3

    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    texts = dict(con.execute("SELECT card_key, text_cn FROM cards"))
    con.close()
    rep = re.compile(r"^\s*(?:\{\{[^{}]+\}\}|（[^）]*）|[\-\+]|[·\s])+\s*$")
    bad = []
    for k, fx in reg.items():
        if not fx.get("reviewed"):
            continue
        lines = [ln for ln in (texts.get(k) or "").strip().splitlines() if ln.strip()]
        effect_rows = [ln for ln in lines if not rep.match(ln)]
        if effect_rows and not fx["abilities"]:
            bad.append((k, effect_rows))
    assert bad == []
