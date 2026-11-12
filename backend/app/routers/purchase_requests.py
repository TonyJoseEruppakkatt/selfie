
import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.purchase_request import (
    PurchaseRequestCreate,
    PurchaseRequestResponse,
    PurchaseRequestStatusUpdate,
)
from app.services.purchase_request_service import (
    create_purchase_request,
    get_buyer_requests,
    get_seller_requests,
    get_purchase_request_details,
    update_purchase_request_status,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/purchase-requests",
    tags=["Purchase Requests"],
)


@router.post(
    "/{mobile_id}",
    response_model=PurchaseRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_purchase_request(
    mobile_id: int,
    request_data: PurchaseRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_purchase_request(
        db=db,
        buyer=current_user,
        mobile_id=mobile_id,
        message=request_data.message,
    )


@router.get(
    "/buyer",
    response_model=list[PurchaseRequestResponse],
)
def view_buyer_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_buyer_requests(
        db=db,
        buyer=current_user,
    )


@router.get(
    "/seller",
    response_model=list[PurchaseRequestResponse],
)
def view_seller_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_seller_requests(
        db=db,
        seller=current_user,
    )


@router.get(
    "/{request_id}",
    response_model=PurchaseRequestResponse,
)
def view_purchase_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_purchase_request_details(
        db=db,
        request_id=request_id,
        current_user=current_user,
    )


@router.patch(
    "/{request_id}/status",
    response_model=PurchaseRequestResponse,
)
def change_purchase_request_status(
    request_id: int,
    request_data: PurchaseRequestStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_purchase_request_status(
        db=db,
        request_id=request_id,
        seller=current_user,
        new_status=request_data.status,
    )
