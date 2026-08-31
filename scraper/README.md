# The Polite Scraper

Week 5 – Assignment A9

A Python scraping pipeline for Books to Scrape. It discovers book pages from the first three catalogue pages, extracts book information, normalizes and validates the data, stores valid records as JSON, handles failed pages, and generates a run report.

## Target Classification

### Target

The target website is:

**Books to Scrape**

https://books.toscrape.com/

Books to Scrape is a public practice sandbox designed for learning and practicing web scraping.

### Scope

This scraper processes only the **first three catalogue pages** of Books to Scrape.

Expected scope:

- 3 catalogue pages
- 60 valid book records
- book URLs are discovered from the catalogue pages
- pagination is followed from the site's own `next` link
- book URLs are not hardcoded

## Data Collected

Each valid book record contains:

- `title`
- `product_url`
- `upc`
- `price_text`
- `price_gbp`
- `availability_text`
- `rating_text`
- `description`
- `source_page`
- `fetched_at`

The raw `price_text` is retained alongside the normalized numeric `price_gbp` value.

## Record Schema

Records are validated with Pydantic before being written to `books.json`.

```text
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