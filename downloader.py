import re
import os
import zipfile
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


HUB_URL = "https://playriftbound.com/en-us/rules-hub/"

OUT_DIR = Path("riftbound_en_rules")
ZIP_PATH = Path("riftbound_en_rules.zip")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/152.0 Safari/537.36"
    )
}

# 官网日期提取失败时使用这些 fallback
FALLBACK_DATES = {
    "Core Rules": "2026-07-16",

    "Core Rules Patch Notes": "2025-10-24",
    "Spiritforged Patch Notes": "2025-12-05",
    "Unleashed Patch Notes": "2026-03-30",
    "Vendetta Patch Notes": "2026-07-17",

    "Origins Errata": "2025-10-28",
    "Spiritforged Errata": "2026-01-14",
    "Unleashed Errata": "2026-04-03",
    "Vendetta Errata": "2026-07-23",
}


def safe_name(s: str) -> str:
    """Make a Windows-safe filename."""
    s = re.sub(r'[<>:"/\\|?*]', "_", s)
    s = re.sub(r"\s+", "_", s.strip())
    return s


def download_file(url: str, path: Path):
    print(f"  Downloading PDF:")
    print(f"    {url}")

    with requests.get(
        url,
        headers=HEADERS,
        stream=True,
        timeout=120,
        allow_redirects=True,
    ) as r:
        r.raise_for_status()

        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    # 确认不是 HTML 错误页面
    with open(path, "rb") as f:
        header = f.read(5)

    if header != b"%PDF-":
        path.unlink(missing_ok=True)
        raise RuntimeError(f"Downloaded file is not a PDF: {url}")


def get_html(url: str) -> str:
    r = requests.get(
        url,
        headers=HEADERS,
        timeout=60,
        allow_redirects=True,
    )
    r.raise_for_status()
    return r.text


def get_hub_links():
    html = get_html(HUB_URL)
    soup = BeautifulSoup(html, "html.parser")

    wanted = {
        "Core Rules",

        "Core Rules Patch Notes",
        "Spiritforged Patch Notes",
        "Unleashed Patch Notes",
        "Vendetta Patch Notes",

        "Origins Errata",
        "Spiritforged Errata",
        "Unleashed Errata",
        "Vendetta Errata",
    }

    result = {}

    for a in soup.find_all("a", href=True):
        text = " ".join(a.stripped_strings)
        href = urljoin(HUB_URL, a["href"])

        for name in wanted:
            if text == name:
                result[name] = href

    return result


def extract_article_date(html: str, fallback: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # 1. OpenGraph / article metadata
    candidates = [
        ("meta", {"property": "article:published_time"}, "content"),
        ("meta", {"name": "article:published_time"}, "content"),
        ("meta", {"property": "og:published_time"}, "content"),
    ]

    for tag, attrs, field in candidates:
        element = soup.find(tag, attrs=attrs)
        if element and element.get(field):
            value = element.get(field)

            m = re.search(r"(\d{4}-\d{2}-\d{2})", value)
            if m:
                return m.group(1)

    # 2. <time datetime>
    for time_tag in soup.find_all("time"):
        value = time_tag.get("datetime", "")
        m = re.search(r"(\d{4}-\d{2}-\d{2})", value)
        if m:
            return m.group(1)

    # 3. 页面文本 ISO 日期
    text = soup.get_text(" ", strip=True)
    m = re.search(r"(20\d{2}-\d{2}-\d{2})", text)
    if m:
        return m.group(1)

    return fallback


def find_pdf_links(article_url: str):
    """
    找文章中的官方 PDF。
    Errata 通常会在正文里放 cmsassets.rgpub.io PDF。
    """
    html = get_html(article_url)
    soup = BeautifulSoup(html, "html.parser")

    pdfs = []

    for a in soup.find_all("a", href=True):
        href = urljoin(article_url, a["href"])

        clean_url = href.lower().split("?")[0]

        if clean_url.endswith(".pdf"):
            pdfs.append(href)

    # 去重但保留顺序
    seen = set()
    result = []

    for url in pdfs:
        if url not in seen:
            seen.add(url)
            result.append(url)

    return result


def print_page_to_pdf(page, url: str, output: Path):
    print(f"  Printing webpage to PDF:")
    print(f"    {url}")

    page.goto(
        url,
        wait_until="networkidle",
        timeout=120_000,
    )

    # 等一下字体/图片
    page.wait_for_timeout(2000)

    # 尽量移除 cookie/banner/navigation 等网页 UI
    page.add_style_tag(
        content="""
        nav,
        footer,
        [role="banner"],
        [class*="cookie"],
        [class*="Cookie"],
        [class*="navbar"],
        [class*="Navbar"] {
            display: none !important;
        }

        body {
            background: white !important;
        }
        """
    )

    page.emulate_media(media="screen")

    page.pdf(
        path=str(output),
        format="A4",
        print_background=True,
        margin={
            "top": "15mm",
            "bottom": "15mm",
            "left": "12mm",
            "right": "12mm",
        },
    )


def main():
    OUT_DIR.mkdir(exist_ok=True)

    print("Fetching Riftbound Rules Hub...")
    links = get_hub_links()

    expected = [
        "Core Rules",
        "Core Rules Patch Notes",
        "Origins Errata",
        "Spiritforged Patch Notes",
        "Spiritforged Errata",
        "Unleashed Patch Notes",
        "Unleashed Errata",
        "Vendetta Patch Notes",
        "Vendetta Errata",
    ]

    print("\nFound:")
    for name in expected:
        if name in links:
            print(f"  [OK] {name}")
        else:
            print(f"  [MISSING] {name}")

    downloaded = []

    #
    # Core Rules
    #
    if "Core Rules" in links:
        url = links["Core Rules"]

        date = FALLBACK_DATES["Core Rules"]
        temp = OUT_DIR / f"{date}_Core_Rules.pdf"

        download_file(url, temp)

        downloaded.append(
            {
                "date": date,
                "name": "Core_Rules",
                "path": temp,
            }
        )

    #
    # Patch Notes + Errata
    #
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            user_agent=HEADERS["User-Agent"],
            viewport={"width": 1440, "height": 1200},
        )

        page = context.new_page()

        for name in expected:
            if name == "Core Rules":
                continue

            if name not in links:
                continue

            article_url = links[name]

            print(f"\nProcessing: {name}")

            try:
                html = get_html(article_url)
            except Exception as e:
                print(f"  Could not fetch HTML with requests: {e}")
                html = ""

            date = extract_article_date(
                html,
                FALLBACK_DATES[name],
            )

            clean_name = safe_name(name)

            temp = OUT_DIR / f"{date}_{clean_name}.pdf"

            #
            # Errata：
            # 优先找 Riot 提供的官方 PDF
            #
            if "Errata" in name:
                try:
                    pdf_links = find_pdf_links(article_url)
                except Exception:
                    pdf_links = []

                if pdf_links:
                    print(
                        f"  Found {len(pdf_links)} PDF link(s); "
                        f"using first official PDF."
                    )

                    try:
                        download_file(pdf_links[0], temp)

                    except Exception as e:
                        print(f"  PDF download failed: {e}")
                        print("  Falling back to webpage -> PDF")

                        print_page_to_pdf(
                            page,
                            article_url,
                            temp,
                        )

                else:
                    print(
                        "  No direct PDF found; "
                        "saving article as PDF."
                    )

                    print_page_to_pdf(
                        page,
                        article_url,
                        temp,
                    )

            #
            # Patch Notes：
            # 官网本身是文章，所以直接转 PDF
            #
            else:
                print_page_to_pdf(
                    page,
                    article_url,
                    temp,
                )

            downloaded.append(
                {
                    "date": date,
                    "name": clean_name,
                    "path": temp,
                }
            )

        browser.close()

    #
    # 按时间排序 + 重新编号
    #
    downloaded.sort(
        key=lambda x: (
            x["date"],
            x["name"],
        )
    )

    final_files = []

    print("\nRenaming files...")

    for i, item in enumerate(downloaded, start=1):
        filename = (
            f"{i:02d}_"
            f"{item['date']}_"
            f"{item['name']}.pdf"
        )

        final_path = OUT_DIR / filename

        item["path"].rename(final_path)

        final_files.append(final_path)

        print(f"  {filename}")

    #
    # ZIP
    #
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    print("\nCreating ZIP...")

    with zipfile.ZipFile(
        ZIP_PATH,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as z:
        for file in final_files:
            z.write(
                file,
                arcname=file.name,
            )

    print("\n====================================")
    print("Done!")
    print(f"PDF folder: {OUT_DIR.resolve()}")
    print(f"ZIP file:   {ZIP_PATH.resolve()}")
    print("====================================")


if __name__ == "__main__":
    main()