from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.price_snapshot import PriceSnapshot
from app.models.product import Product
from app.schemas.price_snapshot import SnapshotOut
from app.schemas.product import ProductOut

router = APIRouter()


@router.get("/products", response_model=list[ProductOut])
async def list_products(
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Product).order_by(Product.id).limit(limit).offset(offset)
    )
    return result.scalars().all()


@router.get("/products/{product_id}/history", response_model=list[SnapshotOut])
async def product_history(
    product_id: int,
    session: AsyncSession = Depends(get_session),
):
    product = await session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    result = await session.execute(
        select(PriceSnapshot)
        .where(PriceSnapshot.product_id == product_id)
        .order_by(PriceSnapshot.scraped_at)
    )
    return result.scalars().all()
