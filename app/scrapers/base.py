from abc import ABC, abstractmethod

import httpx


class BaseScraper(ABC):
    HEADERS = {"User-Agent": "EcommerceWatch/0.1 (projet de demonstration)"}
    REQUEST_DELAY = 1.0  # secondes entre deux pages

    async def fetch(self, url: str) -> str:
        async with httpx.AsyncClient(
            timeout=10.0, headers=self.HEADERS, follow_redirects=True
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    @abstractmethod
    def parse(self, html: str, page_url: str) -> list[dict]: pass
