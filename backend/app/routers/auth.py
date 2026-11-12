
import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse
)

from app.services.auth_service import (
    register_user,
    authenticate_user
)

from app.dependencies.auth import get_current_user
from app.models.user import User


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


# User registration
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):

    user = register_user(
        db,
        user_data
    )

    return user


# User login
@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):

    access_token = authenticate_user(
        db,
        login_data
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# Get logged-in user profile
@router.get(
    "/me",
    response_model=UserResponse
)
def get_profile(
    current_user: User = Depends(get_current_user)
):

    return current_user
