from pydantic import BaseModel


class ProductData(BaseModel):
    title: str
    price_cents: int
    available: bool
    url: str
    external_ref: str | None = None


class ProductOut(BaseModel):
    id: int
    name: str
    url: str

    model_config = {"from_attributes": True}
