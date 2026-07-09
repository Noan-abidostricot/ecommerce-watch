from app.services.detector import run_detection

import asyncio

from sqlalchemy import select

from app.db.session import async_session
from app.models.competitor import Competitor
from app.models.price_snapshot import PriceSnapshot
from app.models.product import Product
from app.scrapers.source_a import BooksToScrapeScraper
from app.services.normalizer import normalize


async def get_or_create_competitor(session) -> Competitor:
    result = await session.execute(
        select(Competitor).where(Competitor.source == "source_a")
    )
    competitor = result.scalar_one_or_none()

    if competitor is None:
        competitor = Competitor(name="Books to Scrape", source="source_a")
        session.add(competitor)
        await session.flush()

    return competitor


async def get_or_create_product(session, competitor, data) -> Product:
    result = await session.execute(select(Product).where(Product.url == data.url))
    product = result.scalar_one_or_none()
    if product is None:
        product = Product(
            name=data.title,
            url=data.url,
            competitor_id=competitor.id,
        )
        session.add(product)
        await session.flush()
    return product


def create_snapshot(session, product, data) -> None:
    snapshot = PriceSnapshot(
        product_id=product.id,
        price=data.price_cents,
        in_stock=data.available,
    )
    session.add(snapshot)


async def main():
    async with async_session() as session:
        competitor = await get_or_create_competitor(session)

        scraper = BooksToScrapeScraper()
        html = await scraper.fetch(scraper.BASE_URL)
        raw_products = scraper.parse(html)

        for raw in raw_products:
            data = normalize(raw)
            product = await get_or_create_product(session, competitor, data)
            create_snapshot(session, product, data)

        await run_detection(session)      # ← nouvelle ligne

        await session.commit()
        print(f"{len(raw_products)} produits traités et enregistrés.")


asyncio.run(main())
