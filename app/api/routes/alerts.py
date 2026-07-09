from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.alert import Alert
from app.schemas.alert import AlertOut

router = APIRouter()


@router.get("/alerts", response_model=list[AlertOut])
async def list_alerts(
    sent: bool | None = None,
    session: AsyncSession = Depends(get_session),
):
    query = select(Alert).order_by(Alert.created_at.desc())
    if sent is not None:
        query = query.where(Alert.sent == sent)
    result = await session.execute(query)
    return result.scalars().all()
