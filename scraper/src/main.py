from pathlib import Path

import requests


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


def main():
    url = f"{BASE_URL}/catalogue/page-1.html"

    cache_file = CACHE_DIR / "catalogue-page-1.html"

    fetch_page(url, cache_file)


if __name__ == "__main__":
    main()