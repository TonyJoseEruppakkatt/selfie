
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


MobileCondition = Literal[
    "Like New",
    "Excellent",
    "Good",
    "Fair",
]


class MobileResponse(BaseModel):
    id: int
    seller_id: int
    brand: str
    model: str
    price: Decimal
    condition: MobileCondition
    description: str | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MobileImageResponse(BaseModel):
    id: int
    image_url: HttpUrl

    model_config = ConfigDict(from_attributes=True)


class SellerResponse(BaseModel):
    id: int
    full_name: str
    phone_number: str

    model_config = ConfigDict(from_attributes=True)


class MobileDetailResponse(MobileResponse):
    images: list[MobileImageResponse]
    seller: SellerResponse


class MobileListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[MobileDetailResponse]
