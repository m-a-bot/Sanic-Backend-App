import jwt

from app.schemas.pyd import Payload


class TokenService:
    async def generate_jwt_token(
        self, payload: Payload, key: str, algorithm: str | None = "HS256"
    ) -> str:
        payload_data = payload.model_dump()
        return jwt.encode(payload_data, key, algorithm)
