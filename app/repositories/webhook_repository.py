from typing import Any

from sqlalchemy import and_, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AccountNotCreatedError
from app.models.accounts import Account
from app.models.payments import Payment


class WebhookRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def check_user_account(self, user_id: int, account_id: int) -> bool:
        query = select(Account.account_id).where(
            and_(Account.user_id == user_id, Account.account_id == account_id)
        )
        result = await self._session.execute(query)
        bd_account_id = result.scalar()
        return bd_account_id is not None

    async def create_account(self, user_id: int, account_id: int) -> int:
        insert_values = {
            "account_id": account_id,
            "balance": 0.0,
            "user_id": user_id,
        }

        query = (
            insert(Account).values(insert_values).returning(Account.account_id)
        )
        try:
            result = await self._session.execute(query)
            await self._session.commit()

            new_account_id = result.scalar()

            if new_account_id is None:
                raise AccountNotCreatedError
        except IntegrityError as exc:
            await self._session.rollback()
            raise AccountNotCreatedError from exc
        else:
            return new_account_id

    async def save_transaction(self, transaction_data: dict[str, Any]) -> bool:
        amount = transaction_data["amount"]
        user_id = transaction_data["user_id"]
        account_id = transaction_data["account_id"]
        query = insert(Payment).values(transaction_data)
        update_query = (
            update(Account)
            .where(
                and_(
                    Account.account_id == account_id,
                    Account.user_id == user_id,
                )
            )
            .values(balance=Account.balance + amount)
            .returning(Account.balance)
        )

        try:
            await self._session.execute(query)
            result = await self._session.execute(update_query)

            await self._session.commit()

            new_balance = result.scalar()

        except IntegrityError as exc:
            await self._session.rollback()
            raise AccountNotCreatedError from exc
        else:
            return new_balance is not None
