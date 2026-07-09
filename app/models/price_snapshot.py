from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.price_snapshot import PriceSnapshot
    from app.models.product import Product


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"
    __table_args__ = (Index("ix_price_snapshots_product_scraped", "product_id", "scraped_at"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    price: Mapped[int] = mapped_column()
    in_stock: Mapped[bool] = mapped_column()
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    product: Mapped["Product"] = relationship(back_populates="snapshots")
