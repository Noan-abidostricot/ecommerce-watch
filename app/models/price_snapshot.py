from app.db.base import Base
from datetime import datetime
from sqlalchemy import  DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    price: Mapped[int] = mapped_column()
    in_stock: Mapped[bool] = mapped_column()
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    product: Mapped["Product"] = relationship(back_populates="snapshots")
