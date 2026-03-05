import json
import os
from typing import List, Dict

try:
    import requests
    from bs4 import BeautifulSoup  # type: ignore
except ImportError:
    print("Установите зависимости: pip install requests beautifulsoup4")
    raise


BASE_URL = "https://fancy-group.pro"
NOVELTIES_URL = BASE_URL
BASE_DIR = os.path.dirname(__file__)
CATALOG_PATH = os.path.join(BASE_DIR, "catalog.json")


def fetch_html(url: str) -> str:
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"
    return resp.text


def parse_products(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")

    products: List[Dict] = []

    # Попробуем найти типичные карточки товаров.
    candidates = soup.select(
        "[data-product-id], .product, .product-item, .catalog-item, .goods-item"
    )
    if not candidates:
        # Fallback: берём ссылки в основном контенте страницы.
        main = soup.find("main") or soup.find("div", id="content") or soup
        links = main.find_all("a", href=True)
        for a in links:
            title = (a.get_text(strip=True) or "").strip()
            href = a["href"]
            if not title or href.startswith("#"):
                continue
            url = href if href.startswith("http") else BASE_URL + href
            products.append(
                {
                    "title": title,
                    "url": url,
                    "category": "Новинки",
                }
            )
        return products

    for block in candidates:
        title = ""
        url = ""
        article = ""

        # Заголовок.
        title_el = (
            block.find("a", class_="title")
            or block.find("a")
            or block.find("h3")
            or block.find("h2")
        )
        if title_el:
            title = title_el.get_text(strip=True)
            if getattr(title_el, "has_attr", lambda *_: False)("href"):
                href = title_el["href"]
                url = href if href.startswith("http") else BASE_URL + href

        # Артикул, если есть.
        text_block = block.get_text(" ", strip=True)
        if "Артикул" in text_block:
            try:
                part = text_block.split("Артикул", 1)[1]
                article = part.split()[0].strip(" :#")
            except Exception:
                pass

        if not title:
            continue

        products.append(
            {
                "title": title,
                "url": url or NOVELTIES_URL,
                "article": article or "",
                "category": "Новинки",
            }
        )

    return products


def main() -> None:
    print(f"Загружаю новинки с {NOVELTIES_URL} ...")
    html = fetch_html(NOVELTIES_URL)
    products = parse_products(html)

    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print(f"Сохранено {len(products)} товаров в {CATALOG_PATH}")


if __name__ == "__main__":
    main()

