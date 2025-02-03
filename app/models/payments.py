import uuid

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.models.common import Base


class Payment(Base):
    __tablename__ = "payments"

    transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
    amount: Mapped[float]
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.account_id"))
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"), index=True
    )
