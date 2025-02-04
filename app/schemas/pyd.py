import uuid
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, field_validator, model_validator
from sanic import exceptions
from sanic.logging.loggers import logger
from typing_extensions import Self

from app.config import settings
from app.utils.utils import get_hash


class WebhookData(BaseModel):
    transaction_id: uuid.UUID
    account_id: int
    user_id: int
    amount: float
    signature: str

    @model_validator(mode="after")
    def validate_webhook_data(self) -> Self:
        if self.amount < 0:
            raise exceptions.BadRequest

        string = (
            f"{self.account_id}"
            f"{self.amount}"
            f"{self.transaction_id}"
            f"{self.user_id}"
            f"{settings.SECRET_KEY}"
        )

        logger.info(string)

        new_signature = get_hash(string)

        logger.info(new_signature)

        if new_signature != self.signature:
            raise exceptions.BadRequest

        return self


class LoginData(BaseModel):
    email: EmailStr
    password: str


class Payload(BaseModel):
    user_id: int
    email: EmailStr
    fullname: str
    type: Literal["user", "admin"]


class UserCreateRequest(BaseModel):
    email: EmailStr
    fullname: str
    password: str

    @model_validator(mode="after")
    def check_lengths(self) -> Self:
        if (
            len(self.fullname) < settings.MIN_LENGTH_FULLNAME
            or len(self.password) < settings.MIN_LENGTH_PASSWORD
        ):
            raise exceptions.BadRequest
        return self


class UserUpdateRequest(BaseModel):
    email: EmailStr
    fullname: str
    password: str


class UserSchema(BaseModel):
    user_id: int
    email: EmailStr
    fullname: str
    password: str

    class Config:
        from_attributes = True


class PublicUserSchema(BaseModel):
    user_id: int
    email: EmailStr
    fullname: str

    class Config:
        from_attributes = True


class AccountSchema(BaseModel):
    account_id: int
    balance: float
    user_id: int

    class Config:
        from_attributes = True


class PaymentSchema(BaseModel):
    transaction_id: str
    account_id: int
    amount: float
    user_id: int

    @field_validator("transaction_id", mode="before")
    @classmethod
    def convert_uuid_to_str(cls, value: Any) -> Any:
        if isinstance(value, uuid.UUID):
            return str(value)
        raise exceptions.BadRequest

    class Config:
        from_attributes = True


class UserAccounts(BaseModel):
    user: PublicUserSchema
    items: list[AccountSchema]

    class Config:
        from_attributes = True


class UserPayments(BaseModel):
    user: PublicUserSchema
    items: list[PaymentSchema]

    class Config:
        from_attributes = True
