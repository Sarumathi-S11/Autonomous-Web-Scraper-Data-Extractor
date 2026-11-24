"""
Autonomous Web Scraper & Data Extractor
Demo target: https://books.toscrape.com/ (a website intended for scraper practice)

Usage:
    pip install -r requirements.txt
    python scraper.py
    python scraper.py --max-pages 5 --delay 1.0
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import time
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://books.toscrape.com/"
OUTPUT_DIR = Path("data")
FIELDS = [
    "title", "price", "availability", "rating", "category",
    "product_url", "source_page"
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("web_scraper")


def create_session() -> requests.Session:
    """Create a session with a descriptive User-Agent and retry handling."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (compatible; EducationalDataExtractor/1.0; "
            "+https://books.toscrape.com/)"
        ),
        "Accept": "text/html,application/xhtml+xml",
    })
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_html(session: requests.Session, url: str, timeout: int = 20) -> str | None:
    """Fetch one page. Return None for a page that cannot be retrieved."""
    try:
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as exc:
        logger.error("Could not fetch %s: %s", url, exc)
        return None


def rating_from_class(classes: list[str]) -> str:
    """Convert the site's star-rating CSS class into a readable label."""
    ratings = {"One": "1", "Two": "2", "Three": "3", "Four": "4", "Five": "5"}
    for class_name in classes:
        if class_name in ratings:
            return ratings[class_name]
    return "Unknown"


def parse_listing_page(html: str, page_url: str) -> tuple[list[dict[str, Any]], str | None]:
    """Extract book records and the next pagination URL from a listing page."""
    soup = BeautifulSoup(html, "html.parser")
    records: list[dict[str, Any]] = []

    for card in soup.select("article.product_pod"):
        title_link = card.select_one("h3 a")
        price_tag = card.select_one(".price_color")
        availability_tag = card.select_one(".availability")
        rating_tag = card.select_one("p.star-rating")

        if not title_link or not price_tag:
            logger.warning("Skipping a product card with missing title/price")
            continue

        product_url = urljoin(page_url, title_link.get("href", ""))
        records.append({
            "title": title_link.get("title") or title_link.get_text(strip=True),
            "price": price_tag.get_text(strip=True),
            "availability": availability_tag.get_text(" ", strip=True)
                if availability_tag else "Unknown",
            "rating": rating_from_class(rating_tag.get("class", []))
                if rating_tag else "Unknown",
            "category": "Books",
            "product_url": product_url,
            "source_page": page_url,
        })

    next_link = soup.select_one("li.next a")
    next_url = urljoin(page_url, next_link.get("href")) if next_link else None
    return records, next_url


def scrape(max_pages: int | None = None, delay: float = 0.8) -> list[dict[str, Any]]:
    """Visit listing pages until there is no next page or max_pages is reached."""
    session = create_session()
    current_url: str | None = BASE_URL
    all_records: list[dict[str, Any]] = []
    visited: set[str] = set()
    page_count = 0

    while current_url and current_url not in visited:
        if max_pages is not None and page_count >= max_pages:
            break

        visited.add(current_url)
        logger.info("Scraping page %d: %s", page_count + 1, current_url)
        html = fetch_html(session, current_url)
        if html is None:
            break

        page_records, next_url = parse_listing_page(html, current_url)
        all_records.extend(page_records)
        page_count += 1
        logger.info("Extracted %d records (total: %d)", len(page_records), len(all_records))

        current_url = next_url
        if current_url:
            time.sleep(max(0.0, delay))

    # Remove accidental duplicate product URLs while preserving order.
    unique: dict[str, dict[str, Any]] = {}
    for record in all_records:
        unique[record["product_url"]] = record

    session.close()
    return list(unique.values())


def export_records(records: list[dict[str, Any]], output_dir: Path = OUTPUT_DIR) -> None:
    """Export the same clean records to UTF-8 JSON and CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "scraped_books.json"
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)

    csv_path = output_dir / "scraped_books.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)

    logger.info("Saved %d records to %s and %s", len(records), json_path, csv_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Paginated book listing scraper")
    parser.add_argument("--max-pages", type=int, default=None,
                        help="Maximum listing pages; default scrapes all available pages")
    parser.add_argument("--delay", type=float, default=0.8,
                        help="Delay between page requests in seconds (default: 0.8)")
    parser.add_argument("--minimum-records", type=int, default=100,
                        help="Warn if fewer than this number of records are extracted")
    args = parser.parse_args()

    records = scrape(max_pages=args.max_pages, delay=args.delay)
    export_records(records)

    if len(records) < args.minimum_records:
        logger.warning(
            "Only %d records extracted; expected at least %d. "
            "Check site availability or increase --max-pages.",
            len(records), args.minimum_records
        )
    else:
        logger.info("Success: extracted at least %d records.", args.minimum_records)


if __name__ == "__main__":
    main()
