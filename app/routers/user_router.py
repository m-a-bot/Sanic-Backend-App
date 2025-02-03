from typing import Any

import pydantic
from sanic import Blueprint, HTTPResponse, Request, exceptions, json

from app.auth import protected
from app.database.database import AsyncSessionLocal
from app.schemas.pyd import LoginData
from app.services.user_service import UserService

user_router = Blueprint(name="user_router", url_prefix="/user")


@user_router.post("/login")
async def login_user(request: Request) -> HTTPResponse:
    try:
        user_data = LoginData.model_validate(request.json)
    except pydantic.ValidationError as exc:
        raise exceptions.BadRequest from exc

    async with AsyncSessionLocal() as session:
        token = await UserService(session).login_user(
            str(user_data.email), user_data.password
        )

        return json({"token": token})


@user_router.get("/about_me")
@protected(user_type="user")
async def get_my_info(request: Request, **kwargs: Any) -> HTTPResponse:  # noqa: ARG001
    user_id = kwargs["user_id"]

    async with AsyncSessionLocal() as session:
        info = await UserService(session).get_info(user_id)

        return json(info.model_dump())


@user_router.get("/accounts/balances")
@protected(user_type="user")
async def get_my_accounts(request: Request, **kwargs: Any) -> HTTPResponse:  # noqa: ARG001
    user_id = kwargs["user_id"]

    async with AsyncSessionLocal() as session:
        accounts = await UserService(session).get_accounts(user_id)

        return json(accounts.model_dump())


@user_router.get("/payments")
@protected(user_type="user")
async def get_my_payments(request: Request, **kwargs: Any) -> HTTPResponse:  # noqa: ARG001
    user_id = kwargs["user_id"]

    async with AsyncSessionLocal() as session:
        payments = await UserService(session).get_payments(user_id)

        return json(payments.model_dump())
