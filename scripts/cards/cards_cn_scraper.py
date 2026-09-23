"""
符文战场（国服）卡牌图鉴爬虫

数据源：https://playloltcg.com/card.html 使用的官方接口
  POST https://lol-api.playloltcg.com/xcx/card/searchCardCraftWeb  卡牌列表
  POST https://lol-api.playloltcg.com/xcx/dict/getDictList         字典（种类/颜色/稀有度）
  POST https://lol-api.playloltcg.com/xcx/product/getProductList   商品（系列）

文字信息存入 cards_cn/cards.db (SQLite)。

图片暂不下载：cards.front_image / back_image 已入库，download_images() 为预留接口，
需要时运行 `python cards_cn_scraper.py --download-images`。

注意：该 API 的服务器 WAF 对头部敏感，必须带 Origin/Referer/UA，
且偶尔会在 TLS 握手阶段断开（SSLError），已加重试。
"""

import argparse
import json
import re
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import requests

BASE_URL = "https://lol-api.playloltcg.com"

OUT_DIR = Path("cards_cn")
DB_PATH = OUT_DIR / "cards.db"
IMAGE_DIR = OUT_DIR / "images"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/152.0 Safari/537.36"
    ),
    "Content-Type": "application/json",
    "Origin": "https://playloltcg.com",
    "Referer": "https://playloltcg.com/",
}

# 接口一次最多返回多少条（超过 1261 会自动分页）
PAGE_SIZE = 500

SCHEMA = """
CREATE TABLE IF NOT EXISTS dicts (
    type TEXT NOT NULL,          -- card_category / card_color / card_rarity
    code TEXT NOT NULL,          -- 如 unit / red / rune_dust
    name TEXT NOT NULL,          -- 如 单位 / 红色 / 普通
    sort INTEGER,
    PRIMARY KEY (type, code)
);

CREATE TABLE IF NOT EXISTS products (
    code         TEXT PRIMARY KEY,   -- 如 "VEN(标准补充包)"
    name         TEXT NOT NULL,      -- 如 "化神争锋 标准补充包"
    product_type INTEGER,            -- 0=补充包 1=预组（官网原始值）
    sale_time    TEXT,
    image        TEXT,
    buy_url      TEXT
);

CREATE TABLE IF NOT EXISTS cards (
    id                 INTEGER PRIMARY KEY,  -- 接口自增 id
    card_no            TEXT UNIQUE,          -- 卡牌编号，如 "VEN·001"
    name               TEXT NOT NULL,        -- 卡名，如 "巴凯旋沙者"
    sub_title          TEXT,                 -- 副标题，如 "复仇天使"
    category_codes     TEXT,                 -- 种类 code，逗号分隔
    categories         TEXT,                 -- 种类中文，如 "英雄单位"
    color_codes        TEXT,                 -- 颜色 code，逗号分隔
    colors             TEXT,                 -- 颜色中文，如 "红色,绿色"
    hero               TEXT,                 -- 关联英雄
    region             TEXT,                 -- 地区，如 "恕瑞玛"
    tag                TEXT,                 -- 标签，如 "约德尔人"
    artist             TEXT,                 -- 画师
    effect             TEXT,                 -- 异能原文（{{...}} 为图标/关键词占位符）
    flavor_text        TEXT,                 -- 风味文字
    energy             INTEGER,              -- 能量费用，可空
    return_energy      INTEGER,              -- 返还/流转能量，可空
    power              INTEGER,              -- 战力，可空
    rarity_code        TEXT,                 -- 如 rune_dust
    rarity             TEXT,                 -- 普通 / 不凡 / 稀有 / 史诗 / 异画
    extend_rarity_code TEXT,
    extend_rarity      TEXT,                 -- 平卡 / 异画 / 超编 / 签名超编
    extend_type        TEXT,                 -- 扩展类型（官网预留，目前均为空）
    product_codes      TEXT,                 -- 所属商品 code，逗号分隔
    products           TEXT,                 -- 所属商品名，逗号分隔
    errata             TEXT,                 -- 勘误，可空
    qa_json            TEXT,                 -- cardQaList 原始 JSON，可空
    is_preview         INTEGER,              -- 是否预览卡
    card_group_limit   INTEGER,              -- 卡组限制，可空
    list_sort          INTEGER,              -- 官网排序
    front_image        TEXT,                 -- 卡图地址（未下载）
    back_image         TEXT,                 -- 卡背地址（目前为空）
    image_path         TEXT,                 -- 预留：本地图片路径，下载后回写
    scraped_at         TEXT
);
"""


def safe_name(s: str) -> str:
    """Windows 安全文件名。"""
    s = re.sub(r'[<>:"/\\|?*]', "-", s)
    return re.sub(r"\s+", "_", s.strip())


def post(endpoint: str, payload: dict, retries: int = 3) -> dict:
    """调用 API；WAF 偶发 TLS 断连，失败重试。返回 result 字段。"""
    for attempt in range(1, retries + 1):
        try:
            r = requests.post(
                BASE_URL + endpoint,
                json=payload,
                headers=HEADERS,
                timeout=60,
            )
            r.raise_for_status()
            data = r.json()
            if data.get("code") != 0:
                raise RuntimeError(
                    f"API 返回错误: {data.get('message')} ({endpoint})"
                )
            return data["result"]
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
            if attempt == retries:
                raise
            print(f"  连接被重置，重试第 {attempt}/{retries - 1} 次...")
            time.sleep(1.5)


def fetch_dicts() -> list:
    """卡牌种类 / 颜色 / 稀有度字典。"""
    result = []
    for dict_type in ("card_category", "card_color", "card_rarity"):
        items = post(
            "/xcx/dict/getDictList",
            {"pageNum": 1, "pageSize": 100, "type": dict_type},
        )
        result.extend(items)
    return result


def fetch_products() -> list:
    return post("/xcx/product/getProductList", {"pageNum": 1, "pageSize": 1000})


def fetch_all_cards() -> list:
    endpoint = "/xcx/card/searchCardCraftWeb"
    payload = {
        "pageNum": 1,
        "pageSize": PAGE_SIZE,
        "searchContent": "",
        "cardCategoryList": [],
        "cardColorList": [],
        "rarityList": [],
        "productCodeList": [],
    }

    first = post(endpoint, dict(payload))
    total = first["total"]
    cards = list(first["list"])

    while len(cards) < total:
        payload["pageNum"] += 1
        print(f"  分页拉取中: {len(cards)}/{total}")
        cards.extend(post(endpoint, dict(payload))["list"])

    return cards


def normalize_card(c: dict, color_name: dict) -> dict:
    """接口字段 -> 数据库记录（列表字段转逗号分隔文本）。"""
    color_codes = c.get("cardColorList") or []
    qa_list = c.get("cardQaList") or []

    def blank_to_none(v):
        return v if v not in ("", None) else None

    return {
        "id": c["id"],
        "card_no": c.get("cardNo"),
        "name": (c.get("cardName") or "").strip(),
        "sub_title": blank_to_none(c.get("subTitle")),
        "category_codes": ",".join(c.get("cardCategoryList") or []) or None,
        "categories": ",".join(c.get("cardCategoryNameList") or []) or None,
        "color_codes": ",".join(color_codes) or None,
        "colors": ",".join(
            color_name.get(code, code) for code in color_codes
        ) or None,
        "hero": blank_to_none(c.get("hero")),
        "region": blank_to_none(c.get("region")),
        "tag": blank_to_none(c.get("tag")),
        "artist": blank_to_none(c.get("artist")),
        "effect": blank_to_none(c.get("cardEffect")),
        "flavor_text": blank_to_none(c.get("flavorText")),
        "energy": c.get("energy"),
        "return_energy": c.get("returnEnergy"),
        "power": c.get("power"),
        "rarity_code": blank_to_none(c.get("rarity")),
        "rarity": blank_to_none(c.get("rarityName")),
        "extend_rarity_code": blank_to_none(c.get("extendRarity")),
        "extend_rarity": blank_to_none(c.get("extendRarityName")),
        "extend_type": blank_to_none(c.get("extendTypeName")),
        "product_codes": ",".join(c.get("productCodeList") or []) or None,
        "products": ",".join(c.get("productNameList") or []) or None,
        "errata": blank_to_none(c.get("errata")),
        "qa_json": json.dumps(qa_list, ensure_ascii=False) if qa_list else None,
        "is_preview": int(bool(c.get("isPreview"))),
        "card_group_limit": c.get("cardGroupLimit"),
        "list_sort": c.get("listSort"),
        "front_image": blank_to_none(c.get("frontImage")),
        "back_image": blank_to_none(c.get("backImage")),
        "image_path": None,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }


def save_to_db(dicts: list, products: list, cards: list, db_path: Path = DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # 颜色 code -> 中文名（接口只给 code，名字从字典映射）
    color_name = {
        d["code"]: d["name"] for d in dicts if d["type"] == "card_color"
    }

    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA)

        conn.executemany(
            "INSERT OR REPLACE INTO dicts (type, code, name, sort) "
            "VALUES (:type, :code, :name, :sort)",
            [
                {
                    "type": d["type"],
                    "code": d["code"],
                    "name": d["name"],
                    "sort": d.get("sort"),
                }
                for d in dicts
            ],
        )

        conn.executemany(
            "INSERT OR REPLACE INTO products "
            "(code, name, product_type, sale_time, image, buy_url) "
            "VALUES (:code, :name, :productType, :saleTime, :image, :buyUrl)",
            [
                {
                    "code": p["code"],
                    "name": p["name"],
                    "productType": p.get("productType"),
                    "saleTime": p.get("saleTime"),
                    "image": p.get("image"),
                    "buyUrl": p.get("buyUrl"),
                }
                for p in products
                if p.get("isRelatedCard")
            ],
        )

        rows = [normalize_card(c, color_name) for c in cards]
        conn.executemany(
            """
            INSERT OR REPLACE INTO cards (
                id, card_no, name, sub_title,
                category_codes, categories, color_codes, colors,
                hero, region, tag, artist,
                effect, flavor_text,
                energy, return_energy, power,
                rarity_code, rarity, extend_rarity_code, extend_rarity,
                extend_type, product_codes, products,
                errata, qa_json, is_preview, card_group_limit, list_sort,
                front_image, back_image, image_path, scraped_at
            ) VALUES (
                :id, :card_no, :name, :sub_title,
                :category_codes, :categories, :color_codes, :colors,
                :hero, :region, :tag, :artist,
                :effect, :flavor_text,
                :energy, :return_energy, :power,
                :rarity_code, :rarity, :extend_rarity_code, :extend_rarity,
                :extend_type, :product_codes, :products,
                :errata, :qa_json, :is_preview, :card_group_limit, :list_sort,
                :front_image, :back_image, :image_path, :scraped_at
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

    从数据库读取 front_image，保存到 cards_cn/images/ 目录
    （文件名如 VEN·001.png），成功后回写 cards.image_path。

    only_missing=True 时跳过已下载的；delay 为请求间隔秒数。
    """
    image_dir.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, card_no, front_image, image_path FROM cards "
            "WHERE front_image IS NOT NULL"
        ).fetchall()

    todo = []
    for row in rows:
        ext = Path(urlsplit(row["front_image"]).path).suffix or ".png"
        path = image_dir / f"{safe_name(row['card_no'])}{ext}"
        if only_missing and row["image_path"] and Path(row["image_path"]).exists():
            continue
        todo.append((row["id"], row["front_image"], path))

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
        description="符文战场（国服）卡牌爬虫（文字入库，图片可选下载）"
    )
    parser.add_argument(
        "--download-images",
        action="store_true",
        help="抓完文字后同时下载卡图（默认不下载）",
    )
    args = parser.parse_args()

    print("Fetching dicts & products...")
    dicts = fetch_dicts()
    products = fetch_products()
    print(f"  {len(dicts)} dict item(s), {len(products)} product(s)")

    print("Fetching cards...")
    cards = fetch_all_cards()
    print(f"  {len(cards)} card(s)")

    rows = save_to_db(dicts, products, cards)

    # 按种类统计
    from collections import Counter

    cnt = Counter(r["categories"] for r in rows)
    print("\nSaved to DB:")
    for name, n in sorted(cnt.items(), key=lambda x: -x[1]):
        print(f"  {name or '(无种类)':<10} {n} cards")

    print(f"\nDB: {DB_PATH.resolve()}")

    if args.download_images:
        print()
        download_images()
    else:
        print(
            "\n卡图未下载（预留接口 download_images()，"
            "或加 --download-images 启用）。"
        )


if __name__ == "__main__":
    main()
