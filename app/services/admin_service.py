from typing import Any

from sanic import exceptions
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.repositories.admin_repository import AdminRepository
from app.schemas.pyd import (
    Payload,
    PublicUserSchema,
    UserAccounts,
    UserCreateRequest,
    UserUpdateRequest,
)
from app.services.token_service import TokenService
from app.utils.utils import get_hash


class AdminService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repository = AdminRepository(self._session)

    async def login_user(self, email: str, password: str) -> str:
        data = await self._repository.get_user(email)

        if not data:
            raise exceptions.NotFound

        hashed_password = get_hash(password)

        if hashed_password != data.password:
            raise exceptions.Forbidden

        payload = Payload(
            user_id=data.user_id,
            email=data.email,
            fullname=data.fullname,
            type="admin",
        )

        return await TokenService().generate_jwt_token(
            payload, settings.SECRET_KEY
        )

    async def get_info(self, user_id: int) -> PublicUserSchema:
        return await self._repository.get_info(user_id)

    async def create_user(
        self, user_create_request: UserCreateRequest
    ) -> PublicUserSchema:
        return await self._repository.create_user(user_create_request)

    async def update_user(
        self, user_update_request: UserUpdateRequest, user_id: int
    ) -> PublicUserSchema:
        return await self._repository.update_user(user_update_request, user_id)

    async def delete_user(self, user_id: int) -> None:
        return await self._repository.delete_user(user_id)

    async def get_users_balances(self, user_id: int) -> UserAccounts:
        return await self._repository.get_accounts(user_id)

    async def get_users(self) -> list[dict[str, Any]]:
        return await self._repository.get_users()
