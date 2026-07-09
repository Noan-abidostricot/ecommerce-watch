from datetime import datetime

from pydantic import BaseModel


class SnapshotOut(BaseModel):
    id: int
    price: int
    in_stock: bool
    scraped_at: datetime

    model_config = {"from_attributes": True}
