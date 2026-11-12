
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Registration request
class UserCreate(BaseModel):

    full_name: str = Field(
        min_length=3,
        max_length=100
    )

    email: EmailStr

    phone_number: str = Field(
        min_length=7,
        max_length=20
    )

    password: str = Field(
        min_length=8,
        max_length=128
    )


# Login request
class UserLogin(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=1,
        max_length=128
    )


# User response
class UserResponse(BaseModel):

    id: int
    full_name: str
    email: EmailStr
    phone_number: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# JWT response
class TokenResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"
