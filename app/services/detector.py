from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.price_snapshot import PriceSnapshot
from app.models.product import Product


async def detect_for_product(session: AsyncSession, product: Product) -> None:
    result = await session.execute(
        select(PriceSnapshot)
        .where(PriceSnapshot.product_id == product.id)
        .order_by(PriceSnapshot.scraped_at.desc(), PriceSnapshot.id.desc())
        .limit(2)
    )
    snapshots = result.scalars().all()

    if len(snapshots) < 2:
        return

    new = snapshots[0]
    old = snapshots[1]
    detect_changes(session, product, old, new)


def detect_changes(session, product, old, new) -> None:
    # bloc prix
    if new.price < old.price:
        alert = Alert(
            product_id=product.id,
            alert_type="price_drop",
            message=f"Prix passé de {old.price} à {new.price} centimes",
        )
        session.add(alert)
    elif new.price > old.price:
        alert = Alert(
            product_id=product.id,
            alert_type="price_increase",
            message=f"Prix passé de {old.price} à {new.price} centimes",
        )
        session.add(alert)

    # bloc stock
    if old.in_stock and not new.in_stock:
        alert = Alert(
            product_id=product.id,
            alert_type="out_of_stock",
            message="Le produit n'est plus en stock",
        )
        session.add(alert)
    elif not old.in_stock and new.in_stock:
        alert = Alert(
            product_id=product.id,
            alert_type="back_in_stock",
            message="Le produit est de retour en stock",
        )
        session.add(alert)


async def run_detection(session) -> None:
    result = await session.execute(select(Product))
    products = result.scalars().all()
    for product in products:
        await detect_for_product(session, product)
