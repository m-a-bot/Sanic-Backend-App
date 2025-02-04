from typing import Literal

from pydantic import BaseModel, EmailStr, model_validator
from sanic import exceptions
from typing_extensions import Self

from app.config import settings


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
    transaction_id: int
    account_id: int
    amount: float
    user_id: int

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
