import pydantic
from sanic import Blueprint, HTTPResponse, Request, exceptions, text

from app.database.database import AsyncSessionLocal
from app.schemas.pyd import WebhookData
from app.services.webhook_service import WebhookService

webhooks_payments_router = Blueprint(name="webhooks_payments_router")


@webhooks_payments_router.post("/webhooks/payments")
async def webhook_processing(request: Request) -> HTTPResponse:
    try:
        webhook = WebhookData.model_validate(request.json)
    except pydantic.ValidationError as exc:
        raise exceptions.BadRequest from exc

    async with AsyncSessionLocal() as session:
        await WebhookService(session).pipeline(webhook)

    return text("ok")
