from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    UserNotFoundError,
)
from app.models.accounts import Account
from app.models.payments import Payment
from app.models.users import User
from app.schemas.pyd import (
    AccountSchema,
    PaymentSchema,
    PublicUserSchema,
    UserAccounts,
    UserPayments,
    UserSchema,
)


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_user(self, email: str) -> UserSchema:
        query = select(User).where(User.email == email)
        result = await self._session.execute(query)
        user = result.scalar_one_or_none()
        return UserSchema.model_validate(user)

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
