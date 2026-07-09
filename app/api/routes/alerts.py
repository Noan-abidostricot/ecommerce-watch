from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.alert import Alert
from app.schemas.alert import AlertOut

router = APIRouter()


@router.get("/alerts", response_model=list[AlertOut])
async def list_products(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Alert))
    return result.scalars().all()
