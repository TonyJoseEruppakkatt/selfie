from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class PurchaseRequest(Base):

    __tablename__ = "purchase_requests"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    mobile_id: Mapped[int] = mapped_column(
        ForeignKey("mobiles.id"),
        nullable=False
    )

    buyer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    mobile = relationship(
        "Mobile",
        back_populates="purchase_requests"
    )

    buyer = relationship(
        "User",
        back_populates="purchase_requests",
        foreign_keys=[buyer_id]
    )

    seller = relationship(
        "User",
        foreign_keys=[seller_id]
    )