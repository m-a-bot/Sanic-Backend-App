from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.webhook_repository import WebhookRepository
from app.schemas.pyd import WebhookData


class WebhookService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repository = WebhookRepository(self._session)

    async def pipeline(self, webhook: WebhookData) -> bool:
        user_id = webhook.user_id
        account_id = webhook.account_id

        exists = await self._check_user_account(user_id, account_id)

        if not exists:
            await self._create_user_account(user_id, account_id)

        return await self._save_transaction(webhook)

    async def _check_user_account(self, user_id: int, account_id: int) -> bool:
        return await self._repository.check_user_account(user_id, account_id)

    async def _create_user_account(self, user_id: int, account_id: int) -> int:
        return await self._repository.create_account(user_id, account_id)

    async def _save_transaction(self, webhook: WebhookData) -> bool:
        transaction_data = webhook.model_dump()
        transaction_data.pop("signature")
        return await self._repository.save_transaction(transaction_data)
