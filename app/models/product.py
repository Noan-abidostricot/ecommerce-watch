from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    competitor_id: Mapped[int] = mapped_column(ForeignKey("competitors.id"))
    name: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(String(1000))
    external_ref: Mapped[str | None] = mapped_column(String(255))
    competitor: Mapped["Competitor"] = relationship(back_populates="products")
    snapshots: Mapped[list["PriceSnapshot"]] = relationship(back_populates="product")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="product")
