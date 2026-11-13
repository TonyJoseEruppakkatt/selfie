
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
    get_my_mobiles,
    update_mobile,
)
from sqlalchemy import func, select

from app.models.mobile import Mobile
from app.models.purchase_request import PurchaseRequest

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

        if not validate_image_signature(
            content,
            image.content_type,
            ):
            raise HTTPException(
                status_code=400,
                detail="Invalid image file. The file content does not match its image type.",
            )
        
        image_contents.append(content)

    return image_contents


def validate_image_signature(
    content: bytes,
    content_type: str,
) -> bool:
    """Check whether the uploaded file matches its claimed image type."""

    if content_type == "image/jpeg":
        return content.startswith(b"\xff\xd8\xff")

    if content_type == "image/png":
        return content.startswith(
            b"\x89PNG\r\n\x1a\n"
        )

    if content_type == "image/webp":
        return (
            len(content) >= 12
            and content.startswith(b"RIFF")
            and content[8:12] == b"WEBP"
        )

    return False


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
    "/my-listings",
    response_model=MobileListResponse,
)
def list_my_mobile_listings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_my_mobiles(
        db=db,
        seller=current_user,
        page=page,
        page_size=page_size,
    )


@router.get("/dashboard/summary")
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Seller listing statistics
    total_listings = db.scalar(
        select(func.count())
        .select_from(Mobile)
        .where(
            Mobile.seller_id == current_user.id,
            Mobile.status != "removed",
        )
    ) or 0

    available_listings = db.scalar(
        select(func.count())
        .select_from(Mobile)
        .where(
            Mobile.seller_id == current_user.id,
            Mobile.status == "available",
        )
    ) or 0

    sold_listings = db.scalar(
        select(func.count())
        .select_from(Mobile)
        .where(
            Mobile.seller_id == current_user.id,
            Mobile.status == "sold",
        )
    ) or 0

    # Incoming requests for this seller
    incoming_requests = db.scalar(
        select(func.count())
        .select_from(PurchaseRequest)
        .where(PurchaseRequest.seller_id == current_user.id)
    ) or 0

    pending_requests = db.scalar(
        select(func.count())
        .select_from(PurchaseRequest)
        .where(
            PurchaseRequest.seller_id == current_user.id,
            PurchaseRequest.status == "pending",
        )
    ) or 0

    # Requests submitted by this buyer
    my_purchase_requests = db.scalar(
        select(func.count())
        .select_from(PurchaseRequest)
        .where(PurchaseRequest.buyer_id == current_user.id)
    ) or 0

    return {
        "total_listings": total_listings,
        "available_listings": available_listings,
        "sold_listings": sold_listings,
        "incoming_requests": incoming_requests,
        "pending_requests": pending_requests,
        "my_purchase_requests": my_purchase_requests,
    }


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
