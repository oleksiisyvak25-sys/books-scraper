import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
USER_AGENT = "books-scraper/1.0 (learning project)"

RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def parse_price(text):
    match = re.search(r"\d+(?:\.\d+)?", text or "")
    return float(match.group()) if match else None


def parse_books(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    books = []
    for card in soup.select("article.product_pod"):
        link = card.select_one("h3 a")
        rating_tag = card.select_one("p.star-rating")
        rating_word = next((c for c in rating_tag.get("class", []) if c in RATINGS), None) \
            if rating_tag else None
        availability = card.select_one("p.availability")
        books.append({
            "title": link["title"],
            "price": parse_price(card.select_one("p.price_color").get_text()),
            "rating": RATINGS.get(rating_word),
            "in_stock": "in stock" in availability.get_text().lower() if availability else False,
            "url": urljoin(page_url, link["href"]),
        })
    return books


def find_next_page(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    link = soup.select_one("li.next a")
    return urljoin(page_url, link["href"]) if link else None


def fetch(session, url, retries=3, delay=1.0):
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response.text
        except requests.RequestException as error:
            last_error = error
            if attempt < retries:
                time.sleep(delay * attempt)
    raise last_error


def scrape(start_url=BASE_URL, max_pages=1, delay=1.0, on_page=None):
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    books = []
    url = start_url
    pages_done = 0
    while url and pages_done < max_pages:
        html = fetch(session, url, delay=delay)
        page_books = parse_books(html, url)
        books.extend(page_books)
        pages_done += 1
        if on_page:
            on_page(pages_done, url, len(page_books))
        url = find_next_page(html, url)
        if url and pages_done < max_pages:
            time.sleep(delay)
    return books