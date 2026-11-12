
import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.mobile import Mobile
from app.models.purchase_request import PurchaseRequest
from app.models.user import User

logger = logging.getLogger(__name__)


def create_purchase_request(
    db: Session,
    buyer: User,
    mobile_id: int,
    message: str | None = None,
) -> PurchaseRequest:
    try:
        # Find the requested mobile
        mobile = db.scalar(
            select(Mobile).where(Mobile.id == mobile_id)
        )

        if not mobile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mobile listing not found",
            )

        # Check whether the mobile is available
        if mobile.status != "available":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This mobile is not available",
            )

        # A seller cannot request their own mobile
        if mobile.seller_id == buyer.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot send a request for your own listing",
            )

        # Prevent duplicate pending or accepted requests
        existing_request = db.scalar(
            select(PurchaseRequest).where(
                PurchaseRequest.mobile_id == mobile_id,
                PurchaseRequest.buyer_id == buyer.id,
                PurchaseRequest.status.in_(["pending", "accepted"]),
            )
        )

        if existing_request:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already have an active request for this mobile",
            )

        purchase_request = PurchaseRequest(
            mobile_id=mobile.id,
            buyer_id=buyer.id,
            seller_id=mobile.seller_id,
            message=message,
            status="pending",
        )

        db.add(purchase_request)
        db.commit()
        db.refresh(purchase_request)

        logger.info(
            "Purchase request created. Request ID: %s, Buyer ID: %s",
            purchase_request.id,
            buyer.id,
        )

        return purchase_request

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        logger.exception("Failed to create purchase request")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create purchase request",
        )


def get_buyer_requests(
    db: Session,
    buyer: User,
) -> list[PurchaseRequest]:

    statement = (
        select(PurchaseRequest)
        .where(PurchaseRequest.buyer_id == buyer.id)
        .order_by(PurchaseRequest.created_at.desc())
    )

    return list(db.scalars(statement).all())


def get_seller_requests(
    db: Session,
    seller: User,
) -> list[PurchaseRequest]:

    statement = (
        select(PurchaseRequest)
        .where(PurchaseRequest.seller_id == seller.id)
        .order_by(PurchaseRequest.created_at.desc())
    )

    return list(db.scalars(statement).all())


def get_purchase_request_details(
    db: Session,
    request_id: int,
    current_user: User,
) -> PurchaseRequest:

    purchase_request = db.scalar(
        select(PurchaseRequest).where(
            PurchaseRequest.id == request_id
        )
    )

    if not purchase_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase request not found",
        )

    # Only the buyer or seller can view the request
    if current_user.id not in {
        purchase_request.buyer_id,
        purchase_request.seller_id,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view this request",
        )

    return purchase_request


def update_purchase_request_status(
    db: Session,
    request_id: int,
    seller: User,
    new_status: str,
) -> PurchaseRequest:

    purchase_request = db.scalar(
        select(PurchaseRequest).where(
            PurchaseRequest.id == request_id
        )
    )

    if not purchase_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase request not found",
        )

    # Only the seller can accept or reject
    if purchase_request.seller_id != seller.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the seller can update this request",
        )

    # Only pending requests can be updated
    if purchase_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending requests can be accepted or rejected",
        )

    if new_status not in {"accepted", "rejected"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request status",
        )

    try:
        purchase_request.status = new_status

        db.commit()
        db.refresh(purchase_request)

        logger.info(
            "Purchase request %s updated to %s",
            request_id,
            new_status,
        )

        return purchase_request

    except Exception:
        db.rollback()
        logger.exception("Failed to update purchase request")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update purchase request",
        )
