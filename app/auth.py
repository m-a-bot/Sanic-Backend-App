from functools import wraps
from typing import Any, Literal

import jwt
from sanic import Request, exceptions, text
from typing_extensions import Unpack

from app.schemas.pyd import Payload


def check_token(request: Request, user_type: str) -> int | None:
    if not request.token:
        return False

    try:
        payload_data = jwt.decode(
            request.token, request.app.config.SECRET, algorithms=["HS256"]
        )
        payload = Payload.model_validate(payload_data)

        if payload.type != user_type:
            raise exceptions.Forbidden

    except jwt.exceptions.InvalidTokenError:
        return None
    else:
        return payload.user_id


def protected(user_type: Literal["user", "admin"]):
    def decorator(f: Any):
        @wraps(f)
        async def decorated_function(
            request: Request, *args: Unpack[Any], **kwargs: Unpack[Any]
        ):
            user_id = check_token(request, user_type)

            if user_id:
                kwargs["user_id"] = user_id
                return await f(request, *args, **kwargs)

            return text("You are unauthorized.", 401)

        return decorated_function

    return decorator
