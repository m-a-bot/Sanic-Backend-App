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
from app.models.payments import Payment
from app.models.users import User
from app.schemas.pyd import (
    AccountSchema,
    PaymentSchema,
    PublicUserSchema,
    UserAccounts,
    UserCreateRequest,
    UserPayments,
    UserSchema,
    UserUpdateRequest,
)
from app.utils.utils import get_hash


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_user(self, email: str) -> UserSchema:
        query = select(User).where(User.email == email)
        result = await self._session.execute(query)
        user = result.scalar_one_or_none()
        return UserSchema.model_validate(user)

    async def create(self, user: UserCreateRequest) -> PublicUserSchema:
        user_model_dumped = user.model_dump()
        password = user_model_dumped.pop("password")
        user_orm = User(**user_model_dumped)
        insert_values = {
            "fullname": user_orm.fullname,
            "email": user_orm.email,
        }
        if password:
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

    async def update(
        self, user: UserUpdateRequest, user_id: int
    ) -> PublicUserSchema:
        user_model_dumped = user.model_dump()
        password = user_model_dumped.pop("password")
        user_orm = User(**user_model_dumped)
        update_values = {
            "fullname": user_orm.fullname,
            "email": user_orm.email,
        }
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

    async def delete(self, user_id: int) -> None:
        query = delete(User).where(User.user_id == user_id)
        try:
            await self._session.execute(query)
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise UserNotDeletedError from exc

    async def get_info(self, user_id: int) -> PublicUserSchema:
        query = select(User).where(User.user_id == user_id)
        result = await self._session.execute(query)
        user = result.scalar()

        if user is None:
            raise UserNotFoundError

        return PublicUserSchema.model_validate(user)

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

    async def get_payments(self, user_id: int) -> UserPayments:
        query = select(User).where(User.user_id == user_id)
        result = await self._session.execute(query)
        user = result.scalar()

        if user is None:
            raise UserNotFoundError

        s_query = select(Payment).where(Payment.user_id == user_id)
        payments_result = await self._session.execute(s_query)
        payments = payments_result.scalars().all()

        user_schema = PublicUserSchema.model_validate(user)
        payments_schemas = [
            PaymentSchema.model_validate(payment) for payment in payments
        ]

        return UserPayments(user=user_schema, items=payments_schemas)
