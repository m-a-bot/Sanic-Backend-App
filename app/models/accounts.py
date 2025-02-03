from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.common import Base


class Account(Base):
    __tablename__ = "accounts"

    account_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    balance: Mapped[float]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"), index=True
    )
