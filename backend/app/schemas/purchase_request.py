
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PurchaseRequestCreate(BaseModel):
    message: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional message from the buyer to the seller",
    )


class PurchaseRequestStatusUpdate(BaseModel):
    status: Literal["accepted", "rejected"]


class PurchaseRequestResponse(BaseModel):
    id: int
    mobile_id: int
    buyer_id: int
    seller_id: int
    message: str | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
