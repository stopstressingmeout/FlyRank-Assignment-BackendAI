import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"

HEADERS = {
    "User-Agent": "FlyrankA9Scraper/1.0"
}


def fetch_page(url: str, cache_file: Path) -> str:
    """Fetch a page once and reuse the cached copy on later runs."""

    if cache_file.exists():
        print(f"CACHE HIT {cache_file}")
        return cache_file.read_text(encoding="utf-8")

    print(f"FETCH {url}")

    time.sleep(0.5)

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=10,
    )

    response.raise_for_status()

    html = response.text

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(html, encoding="utf-8")

    print(f"SAVED {cache_file}")

    return html


def discover_book_urls(html: str, page_url: str) -> list[str]:
    """Extract and normalize book URLs from one catalogue page."""

    soup = BeautifulSoup(html, "html.parser")

    book_urls = []

    for link in soup.select("article.product_pod h3 a"):
        href = link.get("href")

        if href:
            absolute_url = urljoin(page_url, href)
            book_urls.append(absolute_url)

    return book_urls


def discover_next_page(html: str, page_url: str) -> str | None:
    """Find and normalize the catalogue's next-page URL."""

    soup = BeautifulSoup(html, "html.parser")

    next_link = soup.select_one("li.next a")

    if next_link is None:
        return None

    href = next_link.get("href")

    if not href:
        return None

    return urljoin(page_url, href)


def main():
    current_url = f"{BASE_URL}/catalogue/page-1.html"

    all_book_urls = []
    catalogue_pages = 0

    while current_url and catalogue_pages < 3:
        page_number = catalogue_pages + 1

        cache_file = CACHE_DIR / f"catalogue-page-{page_number}.html"

        html = fetch_page(current_url, cache_file)

        book_urls = discover_book_urls(html, current_url)

        all_book_urls.extend(book_urls)

        catalogue_pages += 1

        print(
            f"PAGE {catalogue_pages}: "
            f"found {len(book_urls)} book URLs"
        )

        current_url = discover_next_page(html, current_url)

    unique_urls = list(dict.fromkeys(all_book_urls))

    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(all_book_urls)}")
    print(f"unique_urls={len(unique_urls)}")

if __name__ == "__main__":
    main()