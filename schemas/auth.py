import re
from typing import Annotated
from uuid import UUID

from fastapi import Body
from pydantic import BaseModel, Field, field_validator


class AuthenticateUserRequest(BaseModel):
    name: Annotated[str, Body(max_length=255, examples=["nagibator_rus"])]
    password: Annotated[str, Body(max_length=40, min_length=8, examples=["!Password123"])]


class AuthenticateUserResponse(BaseModel):
    access_token: Annotated[str, Field(...)]
    token_type: Annotated[str, Field(default="Bearer")]


class RegisterUserRequest(BaseModel):
    name: Annotated[str, Field(..., max_length=255, examples=["nagibator_rus"])]
    email: Annotated[str, Field(..., max_length=255, examples=["email@example.com"])]
    password: Annotated[str, Field(max_length=40, min_length=8, examples=["!Password123"])]

    @field_validator("email")
    def validate_email(cls, value):
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, value):
            raise ValueError("Invalid email format")
        return value

    @field_validator("password")
    def validate_password(cls, value):
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError("Password must contain at least one special character")

        return value


class RegisterUserResponse(BaseModel):
    id: Annotated[UUID, Field(..., examples=["16fd2706-8baf-433b-82eb-8c7fada847da"])]
    name: Annotated[str, Field(..., max_length=255, examples=["nagibator_rus"])]
