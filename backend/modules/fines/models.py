from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


if TYPE_CHECKING:
    from backend.modules.circulation.models import Loan
    from backend.modules.users.models import User


class FineStatus(str, Enum):
    UNPAID = "UNPAID"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class Fine(Base):
    __tablename__ = "fines"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    loan_id: Mapped[int] = mapped_column(
        ForeignKey(
            "loans.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[FineStatus] = mapped_column(
        SQLEnum(
            FineStatus,
            name="fine_status",
        ),
        nullable=False,
        default=FineStatus.UNPAID,
        server_default=FineStatus.UNPAID.value,
    )

    issued_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        "User",
    )

    loan: Mapped["Loan"] = relationship(
        "Loan",
    )

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_fines_amount_positive",
        ),
        CheckConstraint(
            "paid_at IS NULL OR paid_at >= issued_at",
            name="ck_fines_paid_after_issued",
        ),
        CheckConstraint(
            """
            (
                status = 'PAID'
                AND paid_at IS NOT NULL
            )
            OR
            (
                status IN ('UNPAID', 'CANCELLED')
                AND paid_at IS NULL
            )
            """,
            name="ck_fines_status_paid_consistency",
        ),
        Index(
            "ix_fines_user_id",
            "user_id",
        ),
        Index(
            "ix_fines_loan_id",
            "loan_id",
        ),
        Index(
            "ix_fines_status",
            "status",
        ),
    )