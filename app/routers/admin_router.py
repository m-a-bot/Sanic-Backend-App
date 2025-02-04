from typing import Any

import pydantic
from sanic import Blueprint, HTTPResponse, Request, exceptions, json

from app.auth import protected
from app.database.database import AsyncSessionLocal
from app.schemas.pyd import LoginData, UserCreateRequest, UserUpdateRequest
from app.services.admin_service import AdminService

admin_user_router = Blueprint(
    name="admin_user_router", url_prefix="/admin_user"
)


@admin_user_router.post("/login")
async def login_user(request: Request) -> HTTPResponse:
    try:
        user_data = LoginData.model_validate(request.json)
    except pydantic.ValidationError as exc:
        raise exceptions.BadRequest from exc

    async with AsyncSessionLocal() as session:
        token = await AdminService(session).login_user(
            str(user_data.email), user_data.password
        )

        return json({"token": token})


@admin_user_router.get("/about_me")
@protected(user_type="admin")
async def get_my_info(request: Request, **kwargs: Any) -> HTTPResponse:  # noqa: ARG001
    user_id = kwargs["user_id"]

    async with AsyncSessionLocal() as session:
        info = await AdminService(session).get_info(user_id)

        return json(info.model_dump())


@admin_user_router.get("/users/")
@protected(user_type="admin")
async def get_users(request: Request, **kwargs: Any) -> HTTPResponse:  # noqa: ARG001
    async with AsyncSessionLocal() as session:
        users_balances = await AdminService(session).get_users()

        return json(users_balances)


@admin_user_router.post("/users")
@protected(user_type="admin")
async def create_user(request: Request, **kwargs: Any) -> HTTPResponse:  # noqa: ARG001
    try:
        user_create_request = UserCreateRequest.model_validate(request.json)
    except pydantic.ValidationError as exc:
        raise exceptions.BadRequest from exc

    async with AsyncSessionLocal() as session:
        created_user = await AdminService(session).create_user(
            user_create_request
        )

        return json(created_user.model_dump())


@admin_user_router.get("/users/<id>/accounts")
@protected(user_type="admin")
async def get_users_balances(
    request: Request,  # noqa: ARG001
    id: int,
    **kwargs: Any,  # noqa: ARG001
) -> HTTPResponse:
    async with AsyncSessionLocal() as session:
        users_balances = await AdminService(session).get_users_balances(id)

        return json(users_balances.model_dump())


@admin_user_router.put("/users/<id>")
@protected(user_type="admin")
async def update_user(
    request: Request,
    id: int,
    **kwargs: Any,  # noqa: ARG001
) -> HTTPResponse:
    try:
        user_update_request = UserUpdateRequest.model_validate(request.json)
    except pydantic.ValidationError as exc:
        raise exceptions.BadRequest from exc

    async with AsyncSessionLocal() as session:
        updated_user = await AdminService(session).update_user(
            user_update_request, id
        )

        return json(updated_user.model_dump())


@admin_user_router.delete("/users/<id>")
@protected(user_type="admin")
async def delete_user(
    request: Request,  # noqa: ARG001
    id: int,
    **kwargs: Any,  # noqa: ARG001
) -> HTTPResponse:
    async with AsyncSessionLocal() as session:
        await AdminService(session).delete_user(id)

        return json({"success": True})
