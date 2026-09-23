"""
Riftbound Card Gallery 爬虫

抓取 https://playriftbound.com/en-us/card-gallery/ 的全部卡牌数据，
文字信息存入 cards_en/cards.db (SQLite)。

图片暂不下载：cards.image_url 已入库，download_images() 为预留接口，
需要时运行 `python card_scraper.py --download-images`。

说明：页面是 Next.js SSR，所有卡牌数据内嵌在 __NEXT_DATA__ JSON 里，
用 requests 一次请求即可拿到，无需浏览器渲染。
"""

import argparse
import json
import re
import sqlite3
import time
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import urlsplit

import requests

GALLERY_URL = "https://playriftbound.com/en-us/card-gallery/"

OUT_DIR = Path("cards_en")
DB_PATH = OUT_DIR / "cards.db"
IMAGE_DIR = OUT_DIR / "images"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/152.0 Safari/537.36"
    )
}

NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    re.S,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS sets (
    id                   TEXT PRIMARY KEY,   -- 如 OGN / UNL / VEN
    name                 TEXT NOT NULL,      -- 如 Origins
    collector_number_max INTEGER
);

CREATE TABLE IF NOT EXISTS cards (
    id               TEXT PRIMARY KEY,   -- 如 ogn-056-298
    public_code      TEXT NOT NULL,      -- 如 OGN-056/298
    name             TEXT NOT NULL,
    set_id           TEXT NOT NULL REFERENCES sets(id),
    collector_number INTEGER,
    card_type        TEXT,               -- Unit / Spell / Gear / Rune / Legend / Battlefield
    super_type       TEXT,               -- Champion / Signature / Basic / Token，可空
    rarity           TEXT,               -- Common / Uncommon / Rare / Epic / Showcase
    domain           TEXT,               -- Fury / Calm / ... / Colorless，多个用逗号分隔
    energy           INTEGER,            -- 能量费用，可空
    power            INTEGER,            -- 力量费用，可空
    might            INTEGER,            -- 单位战力，可空
    might_bonus      TEXT,               -- 装备战力加成，如 "+3"，可空
    orientation      TEXT,               -- portrait / landscape
    tags             TEXT,               -- 逗号分隔，如 "Mech, Piltover"
    illustrator      TEXT,
    text_html        TEXT,               -- 异能原文（HTML，:rb_*: 为图标占位符）
    text_plain       TEXT,               -- 异能纯文本
    effect_html      TEXT,               -- 额外效果（如装备的负面效果），可空
    effect_plain     TEXT,
    image_url        TEXT,               -- 卡图地址（未下载）
    image_path       TEXT,               -- 预留：本地图片路径，下载后回写
    image_alt        TEXT,               -- 官方无障碍描述文本
    scraped_at       TEXT
);
"""


def safe_name(s: str) -> str:
    """Windows 安全文件名。"""
    s = re.sub(r'[<>:"/\\|?*]', "-", s)
    return re.sub(r"\s+", "_", s.strip())


def html_to_text(html_body: str) -> str:
    """卡面异能 HTML -> 纯文本（保留 :rb_*: 图标占位符）。"""
    if not html_body:
        return ""
    t = re.sub(r"<br\s*/?>", "\n", html_body)
    t = re.sub(r"</p>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    return unescape(t).strip()


def fetch_gallery() -> dict:
    """下载画廊页面并解析 __NEXT_DATA__。"""
    r = requests.get(GALLERY_URL, headers=HEADERS, timeout=60)
    r.raise_for_status()

    m = NEXT_DATA_RE.search(r.text)
    if not m:
        raise RuntimeError("页面中找不到 __NEXT_DATA__，站点结构可能已变更")

    return json.loads(m.group(1))


def find_card_blade(data: dict) -> dict:
    """在页面 blades 中定位卡牌数据块（不依赖固定下标）。"""
    for blade in data["props"]["pageProps"]["page"]["blades"]:
        if blade.get("type") == "riftboundCardGallery":
            return blade
    raise RuntimeError("找不到 riftboundCardGallery 数据块")


def _sub_value(node: dict, field: str, key: str = "id"):
    """取 {'value': {'id': ...}} 这类嵌套字段。"""
    if not isinstance(node, dict):
        return None
    value = node.get("value")
    if not isinstance(value, dict):
        return None
    return value.get(key)


def normalize_card(c: dict) -> dict:
    """把官网原始的复杂嵌套结构拍平成一行数据库记录。"""
    card_type = c.get("cardType") or {}

    types = [t["label"] for t in card_type.get("type", []) if t.get("label")]
    super_types = [
        t["label"] for t in card_type.get("superType", []) if t.get("label")
    ]
    domains = [
        v["label"] for v in (c.get("domain") or {}).get("values", [])
        if v.get("label")
    ]
    artists = [
        v["label"] for v in (c.get("illustrator") or {}).get("values", [])
        if v.get("label")
    ]
    tags = (c.get("tags") or {}).get("tags", [])

    text_html = ((c.get("text") or {}).get("richText") or {}).get("body") or ""
    effect_html = (
        (c.get("effect") or {}).get("richText") or {}
    ).get("body") or ""

    img = c.get("cardImage") or {}

    return {
        "id": c["id"],
        "public_code": c["publicCode"],
        "name": c["name"],
        "set_id": _sub_value(c.get("set"), "value", "id"),
        "collector_number": c.get("collectorNumber"),
        "card_type": ", ".join(types) or None,
        "super_type": ", ".join(super_types) or None,
        "rarity": _sub_value(c.get("rarity"), "value", "label"),
        "domain": ", ".join(domains) or None,
        "energy": _sub_value(c.get("energy"), "value"),
        "power": _sub_value(c.get("power"), "value"),
        "might": _sub_value(c.get("might"), "value"),
        "might_bonus": _sub_value(c.get("mightBonus"), "value", "label"),
        "orientation": c.get("orientation"),
        "tags": ", ".join(tags) or None,
        "illustrator": ", ".join(artists) or None,
        "text_html": text_html,
        "text_plain": html_to_text(text_html),
        "effect_html": effect_html or None,
        "effect_plain": html_to_text(effect_html) or None,
        "image_url": img.get("url"),
        "image_path": None,
        "image_alt": img.get("accessibilityText"),
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }


def save_to_db(sets: list, cards: list, db_path: Path = DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA)

        conn.executemany(
            """
            INSERT OR REPLACE INTO sets (id, name, collector_number_max)
            VALUES (:id, :name, :collectorNumberMax)
            """,
            [
                {
                    "id": s["id"],
                    "name": s["name"],
                    "collectorNumberMax": s.get("collectorNumberMax"),
                }
                for s in sets
            ],
        )

        rows = [normalize_card(c) for c in cards]
        conn.executemany(
            """
            INSERT OR REPLACE INTO cards (
                id, public_code, name, set_id, collector_number,
                card_type, super_type, rarity, domain,
                energy, power, might, might_bonus,
                orientation, tags, illustrator,
                text_html, text_plain, effect_html, effect_plain,
                image_url, image_path, image_alt, scraped_at
            ) VALUES (
                :id, :public_code, :name, :set_id, :collector_number,
                :card_type, :super_type, :rarity, :domain,
                :energy, :power, :might, :might_bonus,
                :orientation, :tags, :illustrator,
                :text_html, :text_plain, :effect_html, :effect_plain,
                :image_url, :image_path, :image_alt, :scraped_at
            )
            """,
            rows,
        )

    return rows


def download_images(
    db_path: Path = DB_PATH,
    image_dir: Path = IMAGE_DIR,
    only_missing: bool = True,
    delay: float = 0.2,
):
    """【预留接口】下载卡图。

    从数据库读取 image_url，保存到 cards_en/images/ 目录
    （文件名如 OGN-056-298.png），成功后回写 cards.image_path。

    only_missing=True 时跳过已下载的；delay 为请求间隔秒数。
    """
    image_dir.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, public_code, image_url, image_path FROM cards "
            "WHERE image_url IS NOT NULL"
        ).fetchall()

    todo = []
    for row in rows:
        ext = Path(urlsplit(row["image_url"]).path).suffix or ".png"
        path = image_dir / f"{safe_name(row['public_code'])}{ext}"
        if only_missing and row["image_path"] and Path(row["image_path"]).exists():
            continue
        todo.append((row["id"], row["image_url"], path))

    print(f"Downloading {len(todo)} card image(s) -> {image_dir.resolve()}")

    for i, (card_id, url, path) in enumerate(todo, start=1):
        try:
            r = requests.get(url, headers=HEADERS, stream=True, timeout=120)
            r.raise_for_status()

            with open(path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 256):
                    if chunk:
                        f.write(chunk)

            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    "UPDATE cards SET image_path = ? WHERE id = ?",
                    (str(path), card_id),
                )

            print(f"  [{i}/{len(todo)}] {path.name}")

        except Exception as e:
            print(f"  [{i}/{len(todo)}] FAILED {url}: {e}")

        time.sleep(delay)


def main():
    parser = argparse.ArgumentParser(
        description="Riftbound 英文卡牌爬虫（文字入库，图片可选下载）"
    )
    parser.add_argument(
        "--download-images",
        action="store_true",
        help="抓完文字后同时下载卡图（默认不下载）",
    )
    args = parser.parse_args()

    print("Fetching card gallery...")
    data = fetch_gallery()
    blade = find_card_blade(data)

    sets = blade["sets"]["items"]
    cards = blade["cards"]["items"]
    print(f"  Found {len(sets)} set(s), {len(cards)} card(s)")

    rows = save_to_db(sets, cards)

    # 按系列统计
    print("\nSaved to DB:")
    for s in sets:
        n = sum(1 for r in rows if r["set_id"] == s["id"])
        print(f"  {s['id']:<4} {s['name']:<20} {n} cards")

    print(f"\nDB: {DB_PATH.resolve()}")

    if args.download_images:
        print()
        download_images()
    else:
        print(
            "\nCard images not downloaded. "
            "Use --download-images or call download_images() later."
        )


if __name__ == "__main__":
    main()
