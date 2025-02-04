from sanic import exceptions
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.exceptions import UserNotFoundError
from app.repositories.user_repository import UserRepository
from app.schemas.pyd import (
    Payload,
    PublicUserSchema,
    UserAccounts,
    UserPayments,
)
from app.services.token_service import TokenService
from app.utils.utils import get_hash_password


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repository = UserRepository(self._session)

    async def login_user(self, email: str, password: str) -> str:
        data = await self._repository.get_user(email)

        if not data:
            raise exceptions.NotFound

        hashed_password = get_hash_password(password)

        if hashed_password != data.password:
            raise exceptions.Forbidden

        payload = Payload(
            user_id=data.user_id,
            email=data.email,
            fullname=data.fullname,
            type="user",
        )

        return await TokenService().generate_jwt_token(
            payload, settings.SECRET_KEY
        )

    async def get_info(self, user_id: int) -> PublicUserSchema:
        try:
            return await self._repository.get_info(user_id)
        except UserNotFoundError as exc:
            raise exceptions.NotFound from exc

    async def get_accounts(self, user_id: int) -> UserAccounts:
        try:
            return await self._repository.get_accounts(user_id)
        except UserNotFoundError as exc:
            raise exceptions.NotFound from exc

    async def get_payments(self, user_id: int) -> UserPayments:
        try:
            return await self._repository.get_payments(user_id)
        except UserNotFoundError as exc:
            raise exceptions.NotFound from exc
