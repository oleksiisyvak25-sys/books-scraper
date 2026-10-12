# books-scraper

A command-line web scraper that collects book data (title, price, rating, availability, link)
from [books.toscrape.com](https://books.toscrape.com), a sandbox site made for practising
web scraping. Exports to CSV or JSON, with optional filters.

Built with `requests` and `BeautifulSoup`.

## Features

- Follows "next page" links automatically (up to the number of pages you choose)
- Polite scraping: custom User-Agent, configurable delay between requests
- Automatic retries with growing pauses when a request fails
- Exports to **CSV** or **JSON** (chosen by the output file extension)
- Filters: minimum rating, maximum price
- Parsing is separated from downloading, so it is covered by tests that need no internet

## Installation

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
# first 3 pages to CSV
python main.py --pages 3 -o books.csv

# first 5 pages, only books rated 4+ and cheaper than 30, saved as JSON
python main.py --pages 5 --min-rating 4 --max-price 30 -o top_books.json

# slower, gentler scraping
python main.py --pages 10 --delay 2
```

| Option | Description | Default |
|---|---|---|
| `-p`, `--pages` | number of listing pages to scrape (the site has 50) | 1 |
| `-o`, `--output` | output file (`.csv` or `.json`) | `books.csv` |
| `--delay` | seconds between requests | 1.0 |
| `--min-rating` | keep books with at least this rating (1-5) | none |
| `--max-price` | keep books with price up to this value | none |

### Output example (CSV)

```
title,price,rating,in_stock,url
A Light in the Attic,51.77,3,True,https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
Tipping the Velvet,53.74,1,True,https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html
```

## Tests

```bash
python -m unittest discover -s tests -v
```

## Project structure

```
scraper.py   # downloading and HTML parsing
main.py      # command-line interface, filters, saving
tests/       # unit tests with saved HTML fixtures
```

## Notes

This project scrapes a site that is explicitly intended for scraping practice. When scraping
real websites, check their `robots.txt` and terms of service, and keep the request rate low.
