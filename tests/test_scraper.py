import unittest
from pathlib import Path

from main import apply_filters
from scraper import find_next_page, parse_books, parse_price

FIXTURES = Path(__file__).parent / "fixtures"
BASE = "https://books.toscrape.com/"


def load(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


class TestParsePrice(unittest.TestCase):
    def test_pound_price(self):
        self.assertEqual(parse_price("£51.77"), 51.77)

    def test_no_number(self):
        self.assertIsNone(parse_price("free"))
        self.assertIsNone(parse_price(None))


class TestParseBooks(unittest.TestCase):
    def setUp(self):
        self.books = parse_books(load("page.html"), BASE)

    def test_finds_all_books(self):
        self.assertEqual(len(self.books), 3)

    def test_first_book_fields(self):
        book = self.books[0]
        self.assertEqual(book["title"], "A Light in the Attic")
        self.assertEqual(book["price"], 51.77)
        self.assertEqual(book["rating"], 3)
        self.assertTrue(book["in_stock"])
        self.assertEqual(book["url"], BASE + "catalogue/a-light-in-the-attic_1000/index.html")

    def test_out_of_stock_detected(self):
        self.assertFalse(self.books[2]["in_stock"])

    def test_relative_links_resolve_from_catalogue_pages(self):
        books = parse_books(load("last_page.html"), BASE + "catalogue/page-50.html")
        self.assertEqual(books[0]["url"], BASE + "catalogue/a-book_1/index.html")


class TestNextPage(unittest.TestCase):
    def test_next_link_found(self):
        self.assertEqual(find_next_page(load("page.html"), BASE), BASE + "catalogue/page-2.html")

    def test_last_page_returns_none(self):
        self.assertIsNone(find_next_page(load("last_page.html"), BASE + "catalogue/page-50.html"))


class TestFilters(unittest.TestCase):
    def setUp(self):
        self.books = parse_books(load("page.html"), BASE)

    def test_min_rating(self):
        result = apply_filters(self.books, min_rating=3)
        self.assertEqual([b["title"] for b in result], ["A Light in the Attic", "Soumission"])

    def test_max_price(self):
        result = apply_filters(self.books, max_price=51)
        self.assertEqual([b["title"] for b in result], ["Soumission"])

    def test_no_filters_keeps_everything(self):
        self.assertEqual(len(apply_filters(self.books)), 3)


if __name__ == "__main__":
    unittest.main()