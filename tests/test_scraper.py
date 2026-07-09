from app.scrapers.source_a import BooksToScrapeScraper, clean_price

PAGE_URL = "https://books.toscrape.com/catalogue/page-1.html"

SAMPLE_HTML = """
<html><body>
<article class="product_pod">
  <h3><a href="livre-test_1/index.html" title="Livre Test"></a></h3>
  <p class="price_color">£13.99</p>
  <p class="availability">In stock</p>
</article>
<ul class="pager"><li class="next"><a href="page-2.html">next</a></li></ul>
</body></html>
"""


def test_parse_extrait_les_champs():
    products = BooksToScrapeScraper().parse(SAMPLE_HTML, PAGE_URL)
    assert products == [
        {
            "title": "Livre Test",
            "price_cents": 1399,
            "available": True,
            "link": "https://books.toscrape.com/catalogue/livre-test_1/index.html",
            "external_ref": None,
        }
    ]


def test_next_page_resout_l_url():
    url = BooksToScrapeScraper()._next_page(SAMPLE_HTML, PAGE_URL)
    assert url == "https://books.toscrape.com/catalogue/page-2.html"


def test_clean_price_cas_simple():
    assert clean_price("£51.77") == 5177


def test_clean_price_cas_qui_tronquait():
    assert clean_price("£4.35") == 435


def test_clean_price_euros_et_espaces():
    assert clean_price(" 12.99€ ") == 1299
