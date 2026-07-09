import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings
from app.models.competitor import Competitor
from app.models.price_snapshot import PriceSnapshot
from app.models.product import Product
from app.scrapers.castel import CastelScraper
from app.scrapers.source_a import BooksToScrapeScraper
from app.services.detector import run_detection
from app.services.normalizer import normalize
from app.services.notifier import send_notifications
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)
SOURCES = [
    ("source_a", "Books to Scrape", BooksToScrapeScraper),
    ("castel", "La Brûlerie du Castel", CastelScraper),
]


async def get_or_create_competitor(session, source: str, name: str) -> Competitor:
    result = await session.execute(select(Competitor).where(Competitor.source == source))
    competitor = result.scalar_one_or_none()
    if competitor is None:
        competitor = Competitor(name=name, source=source)
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
            external_ref=data.external_ref,
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
    engine = create_async_engine(str(settings.database_url))
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with session_factory() as session:
            total_produits = 0
            for source, name, scraper_cls in SOURCES:
                competitor = await get_or_create_competitor(session, source, name)
                scraper = scraper_cls()
                raw_products = await scraper.scrape_all()
                total_produits += len(raw_products)
                logger.info("%s : %d produits récupérés", name, len(raw_products))

                for raw in raw_products:
                    data = normalize(raw)
                    product = await get_or_create_product(session, competitor, data)
                    create_snapshot(session, product, data)

            await run_detection(session)
            await send_notifications(session)
            await session.commit()
            logger.info("Cycle terminé : %d produits sur %d sources", total_produits, len(SOURCES))

    finally:
        await engine.dispose()


@celery_app.task
def scrape_task() -> None:
    asyncio.run(run_scrape_cycle())
