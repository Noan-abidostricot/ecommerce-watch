import traceback

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.db.base import get_session  # Ajuste l'import selon ton projet si besoin
from app.models.product import Product
from app.schemas.product import ProductOut  # Ajuste l'import selon ton schéma

router = APIRouter()


@router.get("/products", response_model=list[ProductOut])
async def list_products(
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    try:
        print("---> Tentative de récupération des produits en BDD...", flush=True)
        result = await session.execute(
            select(Product)
            .options(joinedload(Product.competitor))
            .order_by(Product.id)
            .limit(limit)
            .offset(offset)
        )
        products = result.scalars().all()
        print(f"---> Succès ! {len(products)} produits trouvés.", flush=True)
        return products
    except Exception as e:
        print(f"!!! LE CRASH EST ICI : {str(e)} !!!", flush=True)
        traceback.print_exc()
        # Le 'from e' règle l'erreur B904 de Ruff
        raise HTTPException(status_code=500, detail=str(e)) from e
