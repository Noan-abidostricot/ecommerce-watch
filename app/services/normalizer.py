from app.schemas.product import ProductData


def normalize(raw: dict) -> ProductData:
    return ProductData(
        title=raw["title"],
        price_cents=raw["price_cents"],
        available=raw["available"],
        url=raw["link"],
        external_ref=raw.get("external_ref"),
    )
