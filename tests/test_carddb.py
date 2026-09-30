# 真实卡库（cards_bilingual.db）加载测试（阶段 4；carddb.py）
# 不硬编码总行数：总量断言均以 audit.total_rows 为准；抽样卡经 .tmp/probe_carddb_facts 核实。
# 规则锚点：R-CR-164.2（基本符文技能）、R-CR-134/103.3.a.1（特性与回填）、R-CR-206（费用印刷为准）、
# R-CR-369.3/377.1/417.1（OGN-017 双 hook）。
import re
import sqlite3
from pathlib import Path

import pytest

from riftsim import cardfx
from riftsim.carddb import card_db_version, load_card_db
from riftsim.enums import CardType, Domain

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "cards_bilingual.db"

pytestmark = pytest.mark.skipif(not DB.exists(), reason="cards_bilingual.db 不在仓库根目录")


@pytest.fixture(scope="module")
def cdb():
    return load_card_db(str(DB))


@pytest.fixture(scope="module")
def conn():
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    yield con
    con.close()


# ---------------------------------------------------------------- 总量与完整性
def test_loaded_plus_unsupported_equals_total_rows(cdb):
    a = cdb.audit
    assert a.total_rows > 0
    assert len(cdb.defs) + len(a.unsupported) == a.total_rows


def test_no_duplicate_card_key_in_source(conn, cdb):
    dup = conn.execute(
        "SELECT card_key, COUNT(*) c FROM cards GROUP BY card_key HAVING c > 1"
    ).fetchall()
    assert dup == []
    # defs 数恰等于行数 - unsupported 数已由上一条断言；此条锁源表无重复键
    assert len(cdb.defs) == len(set(cdb.defs))


def test_def_id_equals_card_key(cdb):
    assert all(k == d.def_id for k, d in cdb.defs.items())
    assert all(u.card_key not in cdb.defs for u in cdb.audit.unsupported)


# ---------------------------------------------------------------- 版本（api_contract §10）
def test_version_format_and_determinism(cdb):
    v = cdb.version
    assert re.fullmatch(r"cdb1:[0-9a-f]{12}@cards_bilingual\.db", v)
    assert card_db_version(str(DB)) == v
    # lru_cache：两次加载同一对象（重复加载不重扫库）
    assert load_card_db(str(DB)) is cdb
    assert load_card_db(str(DB)).version == v


# ---------------------------------------------------------------- 基本符文（R-CR-164.2）
def test_basic_runes_have_1642_abilities(cdb, conn):
    keys = [
        r["card_key"]
        for r in conn.execute(
            "SELECT card_key FROM cards WHERE super_type='Basic'"
            " AND (type_en='Rune' OR type_cn='符文')"
        )
    ]
    assert keys, "源表应有基本符文行"
    for k in keys:
        d = cdb.defs.get(k)
        assert d is not None, f"基本符文 {k} 应可加载"
        assert CardType.RUNE in d.card_types
        assert d.domains, f"基本符文 {k} 必须带特性（103.3.a.1）"
        ids = {ab.ability_id for ab in d.abilities}
        assert {"rune_exhaust_gain", "rune_recycle_gain"}.issubset(ids)
        grants = [ab for ab in d.abilities if ab.kind == "gain_resource"]
        assert len(grants) == 2
        for ab in grants:
            assert "R-CR-164.2" in ab.rules_ref
        ex = next(ab for ab in grants if ab.ability_id == "rune_exhaust_gain")
        re_ = next(ab for ab in grants if ab.ability_id == "rune_recycle_gain")
        assert ex.cost_exhaust_self and ex.grant_energy == 1          # [E]：得 1 法力
        assert re_.cost_recycle_self and re_.grant_power_self_domain  # 回收：得[C]


# ---------------------------------------------------------------- 特性回填（R-CR-134）
def test_arc001_domain_backfilled_red(cdb):
    d = cdb.defs["ARC-001"]  # 蔚：domain_en 缺省，color_cn=红色 → 回填 [R]
    assert d.domains == frozenset({Domain.R})
    assert "ARC-001" in cdb.audit.derived_domain_cards


# ---------------------------------------------------------------- unsupported（混色符能费用，206 印刷为准）
def test_mixed_domain_power_cost_cards_unsupported(cdb):
    reasons = [u for u in cdb.audit.unsupported if "符能费用" in u.reason]
    assert reasons, "应存在混色符能费卡在 unsupported"
    assert all(u.card_key not in cdb.defs for u in reasons)
    # schema 无多特性符能列可精确归属 → 不猜（哨兵 UnsupportedCard 而非异常）
    known = {u.card_key for u in reasons}
    assert "OGN-248" in known  # 探针核实：Fury,Mind 双色 3 符能费


# ---------------------------------------------------------------- OGN-017 双技能登记（369.3 + 377.1/417.1）
def test_ogn017_fx_registered(cdb):
    """cardfx 架构（阶段 4 三轮起）：OGN-017 的两个技能由 cardfx/ogn.py 登记，
    结构与迁移前解析产物一致（保真 diff 验过：.tmp/defs_fx_baseline.json vs after_switch）。"""
    fx = cardfx.fx_for("OGN-017")
    assert fx is not None, "OGN-017 必须在 cardfx 登记"
    d = cdb.defs["OGN-017"]
    kinds = {ab.kind for ab in d.abilities}
    assert kinds == {"enters_exhausted", "deal_damage"}
    deal = next(ab for ab in d.abilities if ab.kind == "deal_damage")
    assert deal.damage == 2 and deal.target_scope == "unit_at_battlefield"
    assert deal.cost_exhaust_self and deal.timing == "action"
    static_ab = next(ab for ab in d.abilities if ab.kind == "enters_exhausted")
    assert static_ab.timing == "passive"


def test_cardfx_architecture_audit(cdb):
    """cardfx 新架构口径：解析层已退役，conflicts/unparsed 恒空；
    hook_cards 来自 cardfx 注册的 abilities.kind（引擎原语结算键）。"""
    a = cdb.audit
    assert a.conflicts == [] and a.unparsed_text_cards == []
    assert cardfx.registered_count() > 0
    assert set(a.hook_cards) <= {
        "enters_exhausted", "deal_damage",
        "gain_resource", "extra_cost", "enters_ready",
        "location_open_battlefield", "spell_damage", "spell_draw",
        "on_play_draw", "no_combat_damage", "last_damage",
        # 批次 3（cardfx 手写）：临时修正原语
        "spell_pump", "on_play_pump",
        # rq-4：818 装配（equip 原语）
        "equip",
        # 383 触发注册表（trigger 原语；triggers.fire 入链、playing 载荷 dispatch）
        "trigger",
    }
    assert "OGN-017" in a.hook_cards["enters_exhausted"]
    assert "OGN-017" in a.hook_cards["deal_damage"]
