from sqlalchemy.orm import Mapped, mapped_column

from app.models.common import Base


class AdminUser(Base):
    __tablename__ = "admin_users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fullname: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str]
