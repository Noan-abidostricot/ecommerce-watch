import asyncio
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper


class BooksToScrapeScraper(BaseScraper):
    START_URL = "https://books.toscrape.com/catalogue/page-1.html"

    async def scrape_all(self) -> list[dict]:
        url: str | None = self.START_URL
        products: list[dict] = []
        while url:
            html = await self.fetch(url)
            products.extend(self.parse(html, url))
            url = self._next_page(html, url)
            if url:
                await asyncio.sleep(self.REQUEST_DELAY)
        return products

    def parse(self, html: str, page_url: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        products = []
        for book in soup.find_all("article", class_="product_pod"):
            products.append({
                "title": book.find("h3").find("a")["title"],
                "price": book.find("p", class_="price_color").text,
                "available": "In stock" in book.find("p", class_="availability").text,
                "link": urljoin(page_url, book.find("h3").find("a")["href"]),
            })
        return products

    def _next_page(self, html: str, current_url: str) -> str | None:
        soup = BeautifulSoup(html, "html.parser")
        link = soup.select_one("li.next > a")
        if link is None:
            return None
        return urljoin(current_url, link["href"])
