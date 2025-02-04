from typing import Any

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    UserNotCreatedError,
    UserNotDeletedError,
    UserNotFoundError,
    UserNotUpdatedError,
)
from app.models.accounts import Account
from app.models.admin_users import AdminUser
from app.models.users import User
from app.schemas.pyd import (
    AccountSchema,
    PublicUserSchema,
    UserAccounts,
    UserCreateRequest,
    UserSchema,
    UserUpdateRequest,
)
from app.utils.utils import get_hash


class AdminRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_user(self, email: str) -> UserSchema:
        query = select(AdminUser).where(AdminUser.email == email)
        result = await self._session.execute(query)
        user = result.scalar_one_or_none()
        return UserSchema.model_validate(user)

    async def create_user(self, user: UserCreateRequest) -> PublicUserSchema:
        insert_values = user.model_dump()
        password = insert_values["password"]
        insert_values["password"] = get_hash(password)

        query = insert(User).values(
            {
                key: value
                for key, value in insert_values.items()
                if value is not None
            }
        )
        try:
            await self._session.execute(query)
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise UserNotCreatedError from exc

        s_query = select(User).where(User.email == user.email)
        query_result = await self._session.execute(s_query)
        new_user = query_result.scalar_one_or_none()
        return PublicUserSchema.model_validate(new_user)

    async def update_user(
        self, user: UserUpdateRequest, user_id: int
    ) -> PublicUserSchema:
        update_values = user.model_dump()
        password = update_values.get("password")
        if password:
            update_values["password"] = get_hash(password)

        query = (
            update(User)
            .where(User.user_id == user_id)
            .values(
                {
                    key: value
                    for key, value in update_values.items()
                    if value is not None
                }
            )
        )
        try:
            await self._session.execute(query)
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise UserNotUpdatedError from exc

        s_query = select(User).where(User.user_id == user_id)
        result = await self._session.execute(s_query)
        user_updated = result.scalar_one_or_none()
        return PublicUserSchema.model_validate(user_updated)

    async def delete_user(self, user_id: int) -> None:
        query = (
            delete(User).where(User.user_id == user_id).returning(User.user_id)
        )
        try:
            result = await self._session.execute(query)
            await self._session.commit()

            deleted_user = result.scalar()

            if deleted_user is None:
                raise UserNotDeletedError

        except IntegrityError as exc:
            await self._session.rollback()
            raise UserNotDeletedError from exc

    async def get_info(self, user_id: int) -> PublicUserSchema:
        query = select(AdminUser).where(AdminUser.user_id == user_id)
        result = await self._session.execute(query)
        user = result.scalar()

        if user is None:
            raise UserNotFoundError

        return PublicUserSchema.model_validate(user)

    async def get_users(self) -> list[dict[str, Any]]:
        query = select(User)
        result = await self._session.execute(query)
        users = result.scalars().all()

        return [
            PublicUserSchema.model_validate(user).model_dump()
            for user in users
        ]

    async def get_accounts(self, user_id: int) -> UserAccounts:
        query = select(User).where(User.user_id == user_id)
        result = await self._session.execute(query)
        user = result.scalar()

        if user is None:
            raise UserNotFoundError

        s_query = select(Account).where(Account.user_id == user_id)
        accounts_result = await self._session.execute(s_query)
        accounts = accounts_result.scalars().all()

        user_schema = PublicUserSchema.model_validate(user)
        account_schemas = [
            AccountSchema.model_validate(account) for account in accounts
        ]

        return UserAccounts(user=user_schema, items=account_schemas)
