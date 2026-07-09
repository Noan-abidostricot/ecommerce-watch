from urllib.parse import urljoin
from decimal import Decimal
from app.schemas.product import ProductData

BASE_URL = "https://books.toscrape.com/"


def clean_price(raw_price: str) -> int:
    cleaned = raw_price.replace("£", "").replace("€", "").strip()
    return int(Decimal(cleaned) * 100)


def normalize(raw: dict) -> ProductData:
    return ProductData(
        title=raw["title"],
        price_cents=clean_price(raw["price"]),
        available=raw["available"],
        url=urljoin(BASE_URL, raw["link"]),
    )
