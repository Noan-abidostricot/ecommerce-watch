from urllib.parse import urljoin

from app.schemas.product import ProductData

BASE_URL = "https://books.toscrape.com/"


def clean_price(raw_price: str) -> int:
    raw_price = raw_price.replace("£", "")
    raw_price = float(raw_price)
    raw_price = int(raw_price * 100)
    return raw_price


def normalize(raw: dict) -> ProductData:
    return ProductData(
        title=raw["title"],
        price_cents=clean_price(raw["price"]),
        available=raw["available"],
        url=urljoin(BASE_URL, raw["link"]),
    )
