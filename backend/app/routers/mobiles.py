
import logging
from decimal import Decimal

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.mobile import (
    MobileDetailResponse,
    MobileListResponse,
)
from app.services.mobile_service import (
    create_mobile,
    delete_mobile,
    get_mobile_details,
    get_mobiles,
    update_mobile,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/mobiles",
    tags=["Mobile Listings"],
)

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_IMAGES = 5


async def read_valid_images(
    images: list[UploadFile] | None,
) -> list[bytes]:

    if not images:
        return []

    if len(images) > MAX_IMAGES:
        raise HTTPException(
            status_code=400,
            detail=f"You can upload a maximum of {MAX_IMAGES} images",
        )

    image_contents = []

    for image in images:

        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Only JPEG, PNG and WEBP images are allowed",
            )

        content = await image.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded image cannot be empty",
            )

        if len(content) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="Each image must be smaller than 5 MB",
            )

        image_contents.append(content)

    return image_contents


@router.post(
    "",
    response_model=MobileDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_mobile_listing(
    brand: str = Form(..., min_length=1, max_length=100),
    model: str = Form(..., min_length=1, max_length=100),
    price: Decimal = Form(..., gt=0),
    condition: str = Form(...),
    description: str | None = Form(None, max_length=2000),
    images: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    image_contents = await read_valid_images(images)

    return create_mobile(
        db=db,
        seller=current_user,
        brand=brand,
        model=model,
        price=price,
        condition=condition,
        description=description,
        images=image_contents,
    )


@router.get(
    "",
    response_model=MobileListResponse,
)
def list_mobile_listings(
    search: str | None = Query(None, max_length=100),
    min_price: Decimal | None = Query(None, ge=0),
    max_price: Decimal | None = Query(None, ge=0),
    condition: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("newest"),
    db: Session = Depends(get_db),
):

    if min_price is not None and max_price is not None:
        if min_price > max_price:
            raise HTTPException(
                status_code=400,
                detail="Minimum price cannot exceed maximum price",
            )

    if condition is not None and condition not in {
        "Like New", "Excellent", "Good", "Fair"
    }:
        raise HTTPException(
            status_code=400,
            detail="Invalid mobile condition",
        )

    if sort_by not in {"newest", "price_low", "price_high"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort option",
        )

    return get_mobiles(
        db=db,
        search=search,
        min_price=min_price,
        max_price=max_price,
        condition=condition,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
    )


@router.get(
    "/{mobile_id}",
    response_model=MobileDetailResponse,
)
def mobile_listing_details(
    mobile_id: int,
    db: Session = Depends(get_db),
):

    return get_mobile_details(
        db=db,
        mobile_id=mobile_id,
    )


@router.put(
    "/{mobile_id}",
    response_model=MobileDetailResponse,
)
async def update_mobile_listing(
    mobile_id: int,
    brand: str | None = Form(None, min_length=1, max_length=100),
    model: str | None = Form(None, min_length=1, max_length=100),
    price: Decimal | None = Form(None, gt=0),
    condition: str | None = Form(None),
    description: str | None = Form(None, max_length=2000),
    images: list[UploadFile] | None = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    image_contents = await read_valid_images(images)

    return update_mobile(
        db=db,
        mobile_id=mobile_id,
        seller=current_user,
        brand=brand,
        model=model,
        price=price,
        condition=condition,
        description=description,
        images=image_contents,
    )


@router.delete(
    "/{mobile_id}",
)
def remove_mobile_listing(
    mobile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    return delete_mobile(
        db=db,
        mobile_id=mobile_id,
        seller=current_user,
    )
