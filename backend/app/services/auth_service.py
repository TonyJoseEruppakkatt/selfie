
import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

logger = logging.getLogger(__name__)


def register_user(
    db: Session,
    user_data: UserCreate
) -> User:

    try:

        # Check whether email already exists
        existing_user = db.scalar(
            select(User).where(
                User.email == str(user_data.email).lower()
            )
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # Hash password
        hashed_password = hash_password(
            user_data.password
        )

        # Create user object
        new_user = User(
            full_name=user_data.full_name.strip(),
            email=str(user_data.email).lower(),
            phone_number=user_data.phone_number,
            password_hash=hashed_password
        )

        # Save user
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(
            "New user registered. User ID: %s",
            new_user.id
        )

        return new_user

    except HTTPException:
        raise

    except IntegrityError:
        db.rollback()

        logger.warning("Duplicate user registration attempt")

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    except Exception:
        db.rollback()

        logger.exception("User registration failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to register user"
        )


def authenticate_user(
    db: Session,
    login_data: UserLogin
):

    try:

        # Find user by email
        user = db.scalar(
            select(User).where(
                User.email == str(login_data.email).lower()
            )
        )

        # Check user and password
        if (
            user is None
            or not verify_password(
                login_data.password,
                user.password_hash
            )
        ):

            logger.warning("Invalid login attempt")

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not user.is_active:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        # Generate JWT
        access_token = create_access_token(user.id)

        logger.info(
            "User login successful. User ID: %s",
            user.id
        )

        return access_token

    except HTTPException:
        raise

    except Exception:

        logger.exception("Authentication failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process login"
        )
