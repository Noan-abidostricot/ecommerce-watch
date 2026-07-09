import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings

# from app.db.session import async_session
from app.models.competitor import Competitor
from app.models.price_snapshot import PriceSnapshot
from app.models.product import Product
from app.scrapers.source_a import BooksToScrapeScraper
from app.services.detector import run_detection
from app.services.normalizer import normalize
from app.services.notifier import send_notifications
from app.workers.celery_app import celery_app


async def get_or_create_competitor(session) -> Competitor:
    result = await session.execute(select(Competitor).where(Competitor.source == "source_a"))
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
    # 1. On crée l'engine (pense bien à importer 'settings' en haut du fichier)
    engine = create_async_engine(str(settings.database_url))
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with session_factory() as session:
            # Récupérer ou créer le compétiteur
            competitor = await get_or_create_competitor(session)

            # Initialiser le scraper
            scraper = BooksToScrapeScraper()

            # Suppression du 'fetch' inutile ici car scrape_all() s'en occupe
            raw_products = await scraper.scrape_all()

            # Boucle de traitement et d'enregistrement
            for raw in raw_products:
                data = normalize(raw)
                product = await get_or_create_product(session, competitor, data)
                create_snapshot(session, product, data)

            # Business logic post-scraping
            await run_detection(session)
            await send_notifications(session)

            # On valide tout en base de données d'un coup
            await session.commit()

    finally:
        # On ferme proprement l'engine pour libérer les connexions
        await engine.dispose()


@celery_app.task
def scrape_task() -> None:
    asyncio.run(run_scrape_cycle())
