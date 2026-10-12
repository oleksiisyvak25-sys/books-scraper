import argparse
import csv
import json
import sys
from pathlib import Path

from scraper import BASE_URL, scrape

FIELDS = ["title", "price", "rating", "in_stock", "url"]


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Scrape book data from books.toscrape.com")
    parser.add_argument("-p", "--pages", type=int, default=1,
                        help="how many listing pages to scrape (default: 1, the site has 50)")
    parser.add_argument("-o", "--output", type=Path, default=Path("books.csv"),
                        help="output file; format is chosen by extension: .csv or .json")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="seconds to wait between requests (default: 1.0)")
    parser.add_argument("--min-rating", type=int, choices=range(1, 6), default=None,
                        help="keep only books with at least this rating (1-5)")
    parser.add_argument("--max-price", type=float, default=None,
                        help="keep only books cheaper than or equal to this price")
    return parser.parse_args(argv)


def save(books, path):
    if path.suffix.lower() == ".json":
        with open(path, "w", encoding="utf-8") as f:
            json.dump(books, f, ensure_ascii=False, indent=2)
    else:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(books)


def apply_filters(books, min_rating=None, max_price=None):
    result = books
    if min_rating is not None:
        result = [b for b in result if b["rating"] and b["rating"] >= min_rating]
    if max_price is not None:
        result = [b for b in result if b["price"] is not None and b["price"] <= max_price]
    return result


def main(argv=None):
    args = parse_args(argv)
    if args.pages < 1:
        print("Error: --pages must be at least 1", file=sys.stderr)
        return 1

    def report(page_number, url, count):
        print(f"Page {page_number}: {count} books  ({url})")

    try:
        books = scrape(BASE_URL, max_pages=args.pages, delay=args.delay, on_page=report)
    except Exception as error:
        print(f"Error: could not download data: {error}", file=sys.stderr)
        return 1

    filtered = apply_filters(books, args.min_rating, args.max_price)
    save(filtered, args.output)
    print(f"Scraped {len(books)} books, saved {len(filtered)} to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())