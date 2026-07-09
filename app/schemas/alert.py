from pydantic import BaseModel


class AlertOut(BaseModel):
    id: int
    product_id: int
    alert_type: str
    message: str
    sent: bool
    model_config = {"from_attributes": True}
