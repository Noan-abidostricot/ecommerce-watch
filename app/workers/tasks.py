import asyncio

from sqlalchemy import select

from app.db.session import async_session
from app.models.competitor import Competitor
from app.models.price_snapshot import PriceSnapshot
from app.models.product import Product
from app.scrapers.source_a import BooksToScrapeScraper
from app.services.detector import run_detection
from app.services.normalizer import normalize
from app.services.notifier import send_notifications
from app.workers.celery_app import celery_app


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


async def run_scrape_cycle() -> None:
    async with async_session() as session:
        competitor = await get_or_create_competitor(session)

        scraper = BooksToScrapeScraper()
        html = await scraper.fetch(scraper.BASE_URL)
        raw_products = scraper.parse(html)

        for raw in raw_products:
            data = normalize(raw)
            product = await get_or_create_product(session, competitor, data)
            create_snapshot(session, product, data)

        await run_detection(session)
        await send_notifications(session)
        await session.commit()


@celery_app.task
def scrape_task() -> None:
    asyncio.run(run_scrape_cycle())
