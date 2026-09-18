from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


if TYPE_CHECKING:
    from backend.modules.users.models import User


class NotificationType(str, Enum):
    DUE_DATE_APPROACHING = "DUE_DATE_APPROACHING"
    BOOK_READY = "BOOK_READY"
    RESERVATION_EXPIRED = "RESERVATION_EXPIRED"
    OVERDUE = "OVERDUE"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(
            NotificationType,
            name="notification_type",
        ),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship(
        "User",
    )

    __table_args__ = (
        Index(
            "ix_notifications_user_id",
            "user_id",
        ),
        Index(
            "ix_notifications_user_is_read",
            "user_id",
            "is_read",
        ),
        Index(
            "ix_notifications_created_at",
            "created_at",
        ),
    )