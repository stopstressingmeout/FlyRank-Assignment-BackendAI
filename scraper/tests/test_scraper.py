from scraper.src.main import (
    discover_book_urls,
    parse_description,
    parse_price_gbp,
)


def test_price_normalization():
    assert parse_price_gbp("£51.77") == 51.77


def test_relative_urls_become_absolute():
    html = """
    <article class="product_pod">
        <h3>
            <a href="../../../catalogue/test-book_123/index.html">
                Test Book
            </a>
        </h3>
    </article>
    """

    urls = discover_book_urls(
        html,
        "https://books.toscrape.com/catalogue/page-1.html",
    )

    assert urls == [
        "https://books.toscrape.com/catalogue/test-book_123/index.html"
    ]


def test_missing_description_returns_none():
    html = """
    <html>
        <body>
            <div id="product_description">
                <h2>Product Description</h2>
            </div>
        </body>
    </html>
    """

    assert parse_description(html) is None


def test_duplicate_urls_can_be_removed():
    urls = [
        "https://books.toscrape.com/book-a/index.html",
        "https://books.toscrape.com/book-a/index.html",
        "https://books.toscrape.com/book-b/index.html",
    ]

    unique_urls = list(dict.fromkeys(urls))

    assert unique_urls == [
        "https://books.toscrape.com/book-a/index.html",
        "https://books.toscrape.com/book-b/index.html",
    ]


def test_malformed_price_raises_error():
    try:
        parse_price_gbp("not-a-price")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for malformed price")