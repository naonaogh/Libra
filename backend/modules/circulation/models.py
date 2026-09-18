from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


if TYPE_CHECKING:
    from backend.modules.catalog.models import Book, BookCopy
    from backend.modules.users.models import User


class ReservationStatus(str, Enum):
    WAITING = "WAITING"
    READY = "READY"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class LoanStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    book_id: Mapped[int] = mapped_column(
        ForeignKey(
            "books.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    status: Mapped[ReservationStatus] = mapped_column(
        SQLEnum(
            ReservationStatus,
            name="reservation_status",
        ),
        nullable=False,
        default=ReservationStatus.WAITING,
        server_default=ReservationStatus.WAITING.value,
    )

    queue_position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    reserved_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    fulfilled_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    book: Mapped["Book"] = relationship(
        "Book",
    )

    user: Mapped["User"] = relationship(
        "User",
    )

    __table_args__ = (
        CheckConstraint(
            "queue_position > 0",
            name="ck_reservations_queue_position_positive",
        ),
        CheckConstraint(
            "expires_at IS NULL OR expires_at >= reserved_at",
            name="ck_reservations_expires_after_reserved",
        ),
        CheckConstraint(
            "fulfilled_at IS NULL OR fulfilled_at >= reserved_at",
            name="ck_reservations_fulfilled_after_reserved",
        ),
        Index(
            "ix_reservations_book_id",
            "book_id",
        ),
        Index(
            "ix_reservations_user_id",
            "user_id",
        ),
        Index(
            "ix_reservations_status",
            "status",
        ),
        Index(
            "ix_reservations_book_status_queue",
            "book_id",
            "status",
            "queue_position",
        ),
    )


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    copy_id: Mapped[int] = mapped_column(
        ForeignKey(
            "book_copies.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    librarian_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    issued_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    due_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    returned_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    status: Mapped[LoanStatus] = mapped_column(
        SQLEnum(
            LoanStatus,
            name="loan_status",
        ),
        nullable=False,
        default=LoanStatus.ACTIVE,
        server_default=LoanStatus.ACTIVE.value,
    )

    copy: Mapped["BookCopy"] = relationship(
        "BookCopy",
    )

    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
    )

    librarian: Mapped["User"] = relationship(
        "User",
        foreign_keys=[librarian_id],
    )

    __table_args__ = (
        CheckConstraint(
            "due_at >= issued_at",
            name="ck_loans_due_after_issued",
        ),
        CheckConstraint(
            "returned_at IS NULL OR returned_at >= issued_at",
            name="ck_loans_returned_after_issued",
        ),
        CheckConstraint(
            """
            (
                status = 'RETURNED'
                AND returned_at IS NOT NULL
            )
            OR
            (
                status IN ('ACTIVE', 'OVERDUE')
                AND returned_at IS NULL
            )
            """,
            name="ck_loans_status_return_consistency",
        ),
        Index(
            "uq_loans_active_copy",
            "copy_id",
            unique=True,
            postgresql_where=text(
                "status IN ('ACTIVE', 'OVERDUE')"
            ),
        ),
        Index(
            "ix_loans_user_id",
            "user_id",
        ),
        Index(
            "ix_loans_copy_id",
            "copy_id",
        ),
        Index(
            "ix_loans_librarian_id",
            "librarian_id",
        ),
        Index(
            "ix_loans_status",
            "status",
        ),
        Index(
            "ix_loans_due_at",
            "due_at",
        ),
    )
