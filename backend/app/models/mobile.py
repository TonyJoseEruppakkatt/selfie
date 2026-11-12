
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    Numeric
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Mobile(Base):

    __tablename__ = "mobiles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    brand: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    condition: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="available",
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    seller = relationship(
        "User",
        back_populates="mobiles"
    )

    images = relationship(
        "MobileImage",
        back_populates="mobile",
        cascade="all, delete-orphan"
    )

    purchase_requests = relationship(
        "PurchaseRequest",
        back_populates="mobile"
    )


class MobileImage(Base):

    __tablename__ = "mobile_images"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    mobile_id: Mapped[int] = mapped_column(
        ForeignKey("mobiles.id"),
        nullable=False,
        index=True
    )

    image_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    public_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    mobile = relationship(
        "Mobile",
        back_populates="images"
    )
