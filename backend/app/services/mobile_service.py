
import logging
import math
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.mobile import Mobile, MobileImage
from app.models.user import User
from app.utils.cloudinary_service import (
    delete_mobile_image,
    upload_mobile_image,
)

logger = logging.getLogger(__name__)

ALLOWED_CONDITIONS = {
    "Like New",
    "Excellent",
    "Good",
    "Fair",
}


def get_mobile_or_404(db: Session, mobile_id: int) -> Mobile:
    statement = (
        select(Mobile)
        .options(
            selectinload(Mobile.images),
            selectinload(Mobile.seller),
        )
        .where(Mobile.id == mobile_id)
    )

    mobile = db.scalar(statement)

    if not mobile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mobile listing not found",
        )

    return mobile


def validate_mobile_data(
    brand: str,
    model: str,
    price: Decimal,
    condition: str,
) -> None:
    if not brand.strip():
        raise HTTPException(status_code=400, detail="Brand is required")

    if not model.strip():
        raise HTTPException(status_code=400, detail="Model is required")

    if price <= 0:
        raise HTTPException(status_code=400, detail="Price must be greater than zero")

    if condition not in ALLOWED_CONDITIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid condition. Choose Like New, Excellent, Good or Fair",
        )


def create_mobile(
    db: Session,
    seller: User,
    brand: str,
    model: str,
    price: Decimal,
    condition: str,
    description: str | None,
    images: list[bytes],
) -> Mobile:

    validate_mobile_data(brand, model, price, condition)

    if not images:
        raise HTTPException(
            status_code=400,
            detail="At least one mobile image is required",
        )

    uploaded_images = []

    try:
        mobile = Mobile(
            seller_id=seller.id,
            brand=brand.strip(),
            model=model.strip(),
            price=price,
            condition=condition,
            description=description,
            status="available",
        )

        db.add(mobile)
        db.flush()

        for image_content in images:
            image_data = upload_mobile_image(image_content)
            uploaded_images.append(image_data["public_id"])

            mobile_image = MobileImage(
                mobile_id=mobile.id,
                image_url=image_data["image_url"],
                public_id=image_data["public_id"],
            )

            db.add(mobile_image)

        db.commit()

        logger.info("Mobile listing created: %s", mobile.id)

        return get_mobile_or_404(db, mobile.id)

    except HTTPException:
        db.rollback()

        for public_id in uploaded_images:
            delete_mobile_image(public_id)

        raise

    except Exception:
        db.rollback()

        for public_id in uploaded_images:
            delete_mobile_image(public_id)

        logger.exception("Failed to create mobile listing")

        raise HTTPException(
            status_code=500,
            detail="Unable to create mobile listing",
        )


def get_mobiles(
    db: Session,
    search: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    condition: str | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "newest",
) -> dict:

    statement = (
        select(Mobile)
        .options(
            selectinload(Mobile.images),
            selectinload(Mobile.seller),
        )
        .where(Mobile.status == "available")
    )

    if search:
        search_term = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                Mobile.brand.ilike(search_term),
                Mobile.model.ilike(search_term),
            )
        )

    if min_price is not None:
        statement = statement.where(Mobile.price >= min_price)

    if max_price is not None:
        statement = statement.where(Mobile.price <= max_price)

    if condition:
        statement = statement.where(Mobile.condition == condition)

    if sort_by == "price_low":
        statement = statement.order_by(Mobile.price.asc())
    elif sort_by == "price_high":
        statement = statement.order_by(Mobile.price.desc())
    else:
        statement = statement.order_by(Mobile.created_at.desc())

    count_statement = (
        select(func.count())
        .select_from(statement.order_by(None).subquery())
    )

    total = db.scalar(count_statement) or 0

    total_pages = math.ceil(total / page_size) if total else 0

    statement = statement.offset(
        (page - 1) * page_size
    ).limit(page_size)

    mobiles = db.scalars(statement).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": mobiles,
    }

def get_my_mobiles(
    db: Session,
    seller: User,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """
    Return the logged-in seller's listings.

    Available and sold listings are included.
    Removed listings are excluded.
    """

    statement = (
        select(Mobile)
        .options(
            selectinload(Mobile.images),
            selectinload(Mobile.seller),
        )
        .where(
            Mobile.seller_id == seller.id,
            Mobile.status != "removed",
        )
        .order_by(Mobile.created_at.desc())
    )

    count_statement = (
        select(func.count())
        .select_from(statement.order_by(None).subquery())
    )

    total = db.scalar(count_statement) or 0

    total_pages = math.ceil(total / page_size) if total else 0

    statement = statement.offset(
        (page - 1) * page_size
    ).limit(page_size)

    mobiles = db.scalars(statement).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": mobiles,
    }


def get_mobile_details(
    db: Session,
    mobile_id: int,
) -> Mobile:

    return get_mobile_or_404(db, mobile_id)


def update_mobile(
    db: Session,
    mobile_id: int,
    seller: User,
    brand: str | None = None,
    model: str | None = None,
    price: Decimal | None = None,
    condition: str | None = None,
    description: str | None = None,
    images: list[bytes] | None = None,
) -> Mobile:

    mobile = get_mobile_or_404(db, mobile_id)

    if mobile.seller_id != seller.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot update another seller's listing",
        )

    if mobile.status != "available":
        raise HTTPException(
            status_code=400,
            detail="Only available listings can be updated",
        )

    new_brand = brand if brand is not None else mobile.brand
    new_model = model if model is not None else mobile.model
    new_price = price if price is not None else mobile.price
    new_condition = condition if condition is not None else mobile.condition

    validate_mobile_data(
        new_brand,
        new_model,
        new_price,
        new_condition,
    )

    uploaded_images = []

    try:
        if brand is not None:
            mobile.brand = brand.strip()

        if model is not None:
            mobile.model = model.strip()

        if price is not None:
            mobile.price = price

        if condition is not None:
            mobile.condition = condition

        if description is not None:
            mobile.description = description

        for image_content in images or []:
            image_data = upload_mobile_image(image_content)
            uploaded_images.append(image_data["public_id"])

            db.add(
                MobileImage(
                    mobile_id=mobile.id,
                    image_url=image_data["image_url"],
                    public_id=image_data["public_id"],
                )
            )

        db.commit()

        logger.info("Mobile listing updated: %s", mobile.id)

        return get_mobile_or_404(db, mobile.id)

    except HTTPException:
        db.rollback()

        for public_id in uploaded_images:
            delete_mobile_image(public_id)

        raise

    except Exception:
        db.rollback()

        for public_id in uploaded_images:
            delete_mobile_image(public_id)

        logger.exception("Failed to update mobile listing")

        raise HTTPException(
            status_code=500,
            detail="Unable to update mobile listing",
        )


def delete_mobile(
    db: Session,
    mobile_id: int,
    seller: User,
) -> dict:

    mobile = get_mobile_or_404(db, mobile_id)

    if mobile.seller_id != seller.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot delete another seller's listing",
        )

    if mobile.status != "available":
        raise HTTPException(
            status_code=400,
            detail="Only available listings can be deleted",
        )

    image_public_ids = [
        image.public_id
        for image in mobile.images
        if image.public_id
    ]

    try:
        mobile.status = "removed"
        db.commit()

        logger.info("Mobile listing removed: %s", mobile_id)

    except Exception:
        db.rollback()
        logger.exception("Failed to remove mobile listing")

        raise HTTPException(
            status_code=500,
            detail="Unable to remove mobile listing",
        )

    for public_id in image_public_ids:
        delete_mobile_image(public_id)

    return {
        "message": "Mobile listing removed successfully",
        "mobile_id": mobile_id,
    }
