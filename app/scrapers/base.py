from abc import ABC, abstractmethod

import httpx


class BaseScraper(ABC):
    async def fetch(self, url: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    @abstractmethod
    def parse(self, html: str) -> list[dict]:
        pass
