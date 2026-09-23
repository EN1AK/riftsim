"""
合并 cards_en/cards.db 与 cards_cn/cards.db 为双语卡表。

输出：当前目录 cards_bilingual.db，单表 cards。
仅保留描述卡牌本身的字段（无画师/商品来源/抓取元数据），
异画等变体保留独立行占位（image_path 留空，之后补卡图）。

匹配键：系列前缀 + 编号本体（忽略 - / · 分隔符与 /MAX 后缀），
如 EN "OGN-066a/298" 与 CN "OGN·066a/298" 都归一为 "OGN-066a"。

数值字段映射（两边模型不同）：
  energy      = 能量费（一致）
  rune_power  = EN power（力量/符文费）= CN return_energy
  might       = EN might（单位战力）= CN power（单位为战力）
  might_bonus = EN might_bonus（装备加成 "+4"）= CN power（装备为加成，存 "+N"）
"""

import re
import sqlite3

EN_DB = "cards_en/cards.db"
CN_DB = "cards_cn/cards.db"
OUT_DB = "cards_bilingual.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS cards (
    card_key          TEXT PRIMARY KEY,   -- 归一编号，如 "OGN-066a" / "VEN-190*" / "VEN-SP1"
    set_id            TEXT NOT NULL,      -- OGN / OGS / SFD / UNL / VEN / ARC / FND / SGN
    number            TEXT NOT NULL,      -- 编号本体（含变体后缀），如 "066a" / "190*" / "SP1"
    variant           TEXT NOT NULL,      -- base / alt / sp / star / token
    name_en           TEXT,
    name_cn           TEXT,
    sub_title_cn      TEXT,               -- 副标题，如 "复仇天使"（EN 卡名自带，并入 name_en）
    type_en           TEXT,               -- Unit / Spell / Gear / Rune / Legend / Battlefield
    type_cn           TEXT,               -- 单位 / 法术 / 装备 / 符文 / 传奇 / 战场
    super_type        TEXT,               -- Champion / Signature / Basic / Token（仅 EN 有）
    domain_en         TEXT,               -- Fury / Calm / ... / Colorless
    color_cn          TEXT,               -- 红色 / 绿色 / ... / 无
    energy            INTEGER,            -- 能量费用
    rune_power        INTEGER,            -- 符文(力量)费用 = EN power / CN return_energy
    might             INTEGER,            -- 单位战力 = EN might / CN power(单位)
    might_bonus       TEXT,               -- 装备战力加成 = EN might_bonus / CN power(装备)，如 "+4"
    rarity_en         TEXT,               -- Common / Uncommon / Rare / Epic / Showcase
    rarity_cn         TEXT,               -- 普通 / 不凡 / 稀有 / 史诗 / 异画
    extend_rarity_cn  TEXT,               -- 平卡 / 异画 / 超编 / 签名超编（仅 CN 有）
    tags_en           TEXT,               -- 如 "Mech, Piltover"
    tag_cn            TEXT,               -- 如 "约德尔人"
    hero_cn           TEXT,               -- 关联英雄
    region_cn         TEXT,               -- 地区
    text_en           TEXT,               -- 异能（EN，大会标占位符 :rb_*:）
    text_cn           TEXT,               -- 异能（CN，占位符 {{...}}）
    flavor_cn         TEXT,               -- 风味文字（仅 CN 有）
    errata_cn         TEXT,               -- 勘误（仅 CN 有）
    image_url_en      TEXT,               -- 官网卡图地址（占位用，未下载）
    image_url_cn      TEXT,               -- 国服卡图地址（占位用，未下载）
    image_path        TEXT                -- 预留：本地卡图路径
);

DELETE FROM cards;
"""


def parse_code(code: str):
    """编号 -> (set_id, number, variant)。"""
    m = re.match(r"^([A-Z]+)[-·](.+)$", code.strip())
    if not m:
        raise ValueError(f"无法解析编号: {code}")
    prefix, rest = m.groups()
    num = rest.split("/")[0].split("·")[0]

    if num.endswith("*"):
        variant = "star"
    elif num.startswith("SP"):
        variant = "sp"
    elif re.match(r"^T\d+$", num):
        variant = "token"
    elif re.match(r"^(\d+|R\d+)[ab]$", num):
        variant = "alt"
    else:
        variant = "base"
    return prefix, num, variant


def load_en() -> dict:
    conn = sqlite3.connect(EN_DB)
    conn.row_factory = sqlite3.Row
    out = {}
    for r in conn.execute("SELECT * FROM cards"):
        set_id, num, variant = parse_code(r["public_code"])
        key = f"{set_id}-{num}"
        assert key not in out, f"EN 编号冲突: {key}"
        out[key] = {
            "set_id": set_id,
            "number": num,
            "variant": variant,
            "name_en": r["name"],
            "type_en": r["card_type"],
            "super_type": r["super_type"],
            "domain_en": r["domain"],
            "energy": r["energy"],
            "rune_power": r["power"],
            "might": r["might"],
            "might_bonus": r["might_bonus"],
            "rarity_en": r["rarity"],
            "tags_en": r["tags"],
            "text_en": r["text_plain"],
            "image_url_en": r["image_url"],
        }
    return out


def load_cn() -> dict:
    conn = sqlite3.connect(CN_DB)
    conn.row_factory = sqlite3.Row
    out = {}
    for r in conn.execute("SELECT * FROM cards"):
        set_id, num, variant = parse_code(r["card_no"])
        key = f"{set_id}-{num}"
        assert key not in out, f"CN 编号冲突: {key}"

        cats = r["categories"] or ""
        power = r["power"]
        # CN power 一列两用：单位为战力，装备为加成（格式化成 EN 风格 "+N"）
        if power is not None and "装备" in cats and "单位" not in cats:
            might, might_bonus = None, f"+{power}"
        else:
            might, might_bonus = power, None

        out[key] = {
            "set_id": set_id,
            "number": num,
            "variant": variant,
            "name_cn": r["name"],
            "sub_title_cn": r["sub_title"],
            "type_cn": cats,
            "color_cn": r["colors"],
            "energy": r["energy"],
            "rune_power": r["return_energy"],
            "might": might,
            "might_bonus": might_bonus,
            "rarity_cn": r["rarity"],
            "extend_rarity_cn": r["extend_rarity"],
            "tag_cn": r["tag"],
            "hero_cn": r["hero"],
            "region_cn": r["region"],
            "text_cn": r["effect"],
            "flavor_cn": r["flavor_text"],
            "errata_cn": r["errata"],
            "image_url_cn": r["front_image"],
        }
    return out


FIELDS = [
    "card_key", "set_id", "number", "variant",
    "name_en", "name_cn", "sub_title_cn",
    "type_en", "type_cn", "super_type",
    "domain_en", "color_cn",
    "energy", "rune_power", "might", "might_bonus",
    "rarity_en", "rarity_cn", "extend_rarity_cn",
    "tags_en", "tag_cn", "hero_cn", "region_cn",
    "text_en", "text_cn", "flavor_cn", "errata_cn",
    "image_url_en", "image_url_cn", "image_path",
]


def main():
    en = load_en()
    cn = load_cn()
    print(f"EN {len(en)} 条，CN {len(cn)} 条")

    all_keys = sorted(
        set(en) | set(cn),
        key=lambda k: (
            k.split("-")[0],
            k.split("-", 1)[1].rstrip("*ab"),
            k,
        ),
    )

    matched = sum(1 for k in all_keys if k in en and k in cn)
    only_en = [k for k in all_keys if k in en and k not in cn]
    only_cn = [k for k in all_keys if k in cn and k not in en]

    rows = []
    for key in all_keys:
        row = dict.fromkeys(FIELDS)
        row["card_key"] = key

        for src in (en.get(key), cn.get(key)):
            if src:
                for f, v in src.items():
                    if v is not None:
                        row[f] = v

        rows.append(row)

    conn = sqlite3.connect(OUT_DB)
    with conn:
        conn.executescript(SCHEMA)
        conn.executemany(
            f"INSERT INTO cards ({', '.join(FIELDS)}) "
            f"VALUES ({', '.join(':' + f for f in FIELDS)})",
            rows,
        )

    print(f"\n合并完成: {len(rows)} 行 -> {OUT_DB}")
    print(f"  双语匹配: {matched}")
    print(f"  仅 EN:    {len(only_en)}  {only_en}")
    print(f"  仅 CN:    {len(only_cn)}  {only_cn}")


if __name__ == "__main__":
    main()
