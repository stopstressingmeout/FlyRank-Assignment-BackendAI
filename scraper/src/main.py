import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, ConfigDict, HttpUrl


BASE_URL = "https://books.toscrape.com"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

HEADERS = {
    "User-Agent": "FlyrankA9Scraper/1.0"
}


class BookRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    product_url: HttpUrl
    upc: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: str | None
    source_page: HttpUrl
    fetched_at: datetime


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


def cache_file_for_book(url: str) -> Path:
    """Create a safe cache filename from a book URL."""

    slug = url.rstrip("/").split("/")[-2]

    return CACHE_DIR / "books" / f"{slug}.html"


def parse_book_title(html: str) -> str:
    """Extract the book title."""

    soup = BeautifulSoup(html, "html.parser")

    title = soup.select_one("div.product_main h1")

    if title is None:
        raise ValueError("Book title not found")

    return title.get_text(strip=True)


def parse_price_text(html: str) -> str:
    """Extract the raw price text."""

    soup = BeautifulSoup(html, "html.parser")

    price = soup.select_one("div.product_main p.price_color")

    if price is None:
        raise ValueError("Book price not found")

    return price.get_text(strip=True)


def parse_availability_text(html: str) -> str:
    """Extract the raw availability text."""

    soup = BeautifulSoup(html, "html.parser")

    availability = soup.select_one(
        "div.product_main p.instock.availability"
    )

    if availability is None:
        raise ValueError("Book availability not found")

    return availability.get_text(" ", strip=True)


def parse_rating_text(html: str) -> str:
    """Extract the raw rating text."""

    soup = BeautifulSoup(html, "html.parser")

    rating = soup.select_one("div.product_main p.star-rating")

    if rating is None:
        raise ValueError("Book rating not found")

    classes = rating.get("class", [])

    for class_name in classes:
        if class_name != "star-rating":
            return class_name

    raise ValueError("Book rating value not found")

def parse_description(html: str) -> str | None:
    """Extract the book description, if present."""
    soup = BeautifulSoup(html, "html.parser")

    description = soup.select_one("#product_description + p")

    if description is None:
        return None

    text = description.get_text(" ", strip=True)
    return text or None

def parse_upc(html: str) -> str:
    """Extract the book UPC from the product information table."""
    soup = BeautifulSoup(html, "html.parser")

    for row in soup.select("table.table.table-striped tr"):
        cells = row.find_all(["th", "td"])

        if len(cells) >= 2:
            label = cells[0].get_text(" ", strip=True)

            if label == "UPC":
                value = cells[1].get_text(" ", strip=True)

                if value:
                    return value

    raise ValueError("Book UPC not found")

def parse_price_gbp(price_text: str) -> float:
    """Convert raw price text such as £51.77 into a number."""
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", price_text)

    if match is None:
        raise ValueError(f"Could not parse price: {price_text!r}")

    return float(match.group(1))


def parse_book_record(
    html: str,
    product_url: str,
    source_page: str,
    fetched_at: datetime,
) -> dict:
    """Extract one raw book record and normalized price."""

    price_text = parse_price_text(html)

    return {
        "title": parse_book_title(html),
        "product_url": product_url,
        "upc": parse_upc(html),
        "price_text": price_text,
        "price_gbp": parse_price_gbp(price_text),
        "availability_text": parse_availability_text(html),
        "rating_text": parse_rating_text(html),
        "description": parse_description(html),
        "source_page": source_page,
        "fetched_at": fetched_at,
    }


def write_json(path: Path, data) -> None:
    """Write JSON with stable formatting."""

    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )


def discover_three_pages() -> tuple[list[str], list[str]]:
    """Discover the first three catalogue pages and their book URLs."""

    catalogue_url = f"{BASE_URL}/catalogue/page-1.html"

    current_url = catalogue_url

    catalogue_pages = []
    all_book_urls = []

    for page_number in range(1, 4):
        cache_file = CACHE_DIR / f"catalogue-page-{page_number}.html"

        html = fetch_page(current_url, cache_file)

        catalogue_pages.append(current_url)

        page_book_urls = discover_book_urls(html, current_url)

        print(
            f"PAGE {page_number}: found "
            f"{len(page_book_urls)} book URLs"
        )

        all_book_urls.extend(page_book_urls)

        next_url = discover_next_page(html, current_url)

        if next_url is None:
            break

        current_url = next_url

    unique_urls = list(dict.fromkeys(all_book_urls))

    print(f"catalogue_pages={len(catalogue_pages)}")
    print(f"discovered={len(all_book_urls)}")
    print(f"unique_urls={len(unique_urls)}")

    return catalogue_pages, unique_urls


def main():
    started_at = datetime.now(timezone.utc)

    catalogue_pages, book_urls = discover_three_pages()

    valid_records = []
    errors = []

    for index, book_url in enumerate(book_urls, start=1):
        print(f"BOOK {index}/{len(book_urls)}")

        book_cache = cache_file_for_book(book_url)

        try:
            before_fetch = book_cache.exists()

            book_html = fetch_page(
                book_url,
                book_cache,
            )

            fetched_at = datetime.now(timezone.utc)

            source_page = catalogue_pages[
                min(
                    (index - 1) // 20,
                    len(catalogue_pages) - 1,
                )
            ]

            raw_record = parse_book_record(
                html=book_html,
                product_url=book_url,
                source_page=source_page,
                fetched_at=fetched_at,
            )

            record = BookRecord.model_validate(raw_record)

            valid_records.append(
                record.model_dump(mode="json")
            )

        except Exception as exc:
            errors.append(
                {
                    "product_url": book_url,
                    "reason": str(exc),
                }
            )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    write_json(
        OUTPUT_DIR / "books.json",
        valid_records,
    )

    write_json(
        OUTPUT_DIR / "errors.json",
        errors,
    )

    finished_at = datetime.now(timezone.utc)

    duration = (
        finished_at - started_at
    ).total_seconds()

    report = {
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "duration_seconds": duration,
        "catalogue_pages": len(catalogue_pages),
        "discovered_urls": len(book_urls),
        "unique_urls": len(book_urls),
        "valid_records": len(valid_records),
        "invalid_records": len(errors),
        "failed_pages": len(errors),
    }

    write_json(
        OUTPUT_DIR / "run-report.json",
        report,
    )

    print()
    print(f"valid_records={len(valid_records)}")
    print(f"invalid_records={len(errors)}")
    print(f"books.json={OUTPUT_DIR / 'books.json'}")
    print(f"errors.json={OUTPUT_DIR / 'errors.json'}")
    print(f"run-report.json={OUTPUT_DIR / 'run-report.json'}")


if __name__ == "__main__":
    main()