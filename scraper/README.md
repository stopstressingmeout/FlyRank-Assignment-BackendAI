# The Polite Scraper

Week 5 – Assignment A9

A Python scraping pipeline that downloads the first three catalogue pages of Books to Scrape, discovers the 60 book pages, extracts book information, normalizes and validates the data, stores valid records as JSON, handles failed pages, and generates a run report.

## Target Classification

### Target

The target website is:

**Books to Scrape**

https://books.toscrape.com/

Books to Scrape is a public practice sandbox designed for learning and practicing web scraping.

### Scope

This scraper will process only the **first three catalogue pages** of Books to Scrape.

The expected scope is:

- 3 catalogue pages
- 60 unique book pages

The scraper will not hardcode the 60 book URLs. It will discover the book URLs from the catalogue pages and follow the site's own pagination.

### Data Collected

The scraper will collect the following information from each book page:

- `title`
- `product_url`
- `price_text`
- `availability_text`
- `rating_text`
- `description`
- `source_page`
- `fetched_at`

A normalized `price_gbp` value will also be produced during processing.

### Robots.txt Check

## Stage 1 — Fetch and Cache

The scraper fetches the first catalogue page and stores the returned HTML locally.

The first execution downloads the page:

```text
FETCH https://books.toscrape.com/catalogue/page-1.html
SAVED F:\Projects\Flyrank_Api\scraper\cache\catalogue-page-1.html

The site's `robots.txt` was checked before implementing the scraper.

**Result:** [WRITE YOUR ACTUAL RESULT HERE]

### Why This Target Is Appropriate

Books to Scrape is a public practice sandbox intended for scraping practice, making it appropriate for this assignment.

I will not reuse this code on another site without checking its rules and terms first.