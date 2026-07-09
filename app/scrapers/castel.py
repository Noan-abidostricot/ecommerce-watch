import asyncio
import json

from app.scrapers.base import BaseScraper


class CastelScraper(BaseScraper):
    BASE_URL = "https://labrulerieducastel.com"
    API_URL = BASE_URL + "/wp-json/wc/store/v1/products"
    REQUEST_DELAY = 10.0  # robots.txt : Crawl-delay: 10
    PER_PAGE = 100

    async def scrape_all(self) -> list[dict]:
        products: list[dict] = []
        page = 1
        while True:
            url = f"{self.API_URL}?per_page={self.PER_PAGE}&page={page}"
            body = await self.fetch(url)
            batch = self.parse(body, url)
            products.extend(batch)
            if len(batch) < self.PER_PAGE:
                break
            page += 1
            await asyncio.sleep(self.REQUEST_DELAY)
        return products

    def parse(self, body: str, page_url: str) -> list[dict]:
        items = json.loads(body)
        products = []
        for item in items:
            price = item["prices"]["price"]
            if not price:
                continue
            products.append(
                {
                    "title": item["name"],
                    "price_cents": int(price),
                    "available": item["is_in_stock"],
                    "link": item["permalink"],
                    "external_ref": str(item["id"]),
                }
            )
        return products
