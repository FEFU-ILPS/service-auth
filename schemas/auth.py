import re
from uuid import UUID

from fastapi import Body
from pydantic import BaseModel, Field, field_validator


class AuthenticateUserRequest(BaseModel):
    username: str = Body(max_length=255, description="Имя пользователя", examples=["nagibator_rus"])
    password: str = Body(
        max_length=40, description="Пароль пользователя", min_length=8, examples=["!Password123"]
    )


class AuthenticateUserResponse(BaseModel):
    access_token: str = Field(description="JWT токен доступа")
    token_type: str = Field(description="Тип токена доступа", default="Bearer")


class RegisterUserRequest(BaseModel):
    name: str = Field(description="Имя пользователя", max_length=255, examples=["nagibator_rus"])
    email: str = Field(
        description="Электронная почта пользователя", max_length=255, examples=["email@example.com"]
    )
    password: str = Field(
        description="Пароль пользователя", max_length=40, min_length=8, examples=["!Password123"]
    )

    @field_validator("email")
    def validate_email(cls, value: str) -> str:
        """Валидатор электронной почты пользователя.

        Args:
            value (str): Невалидированное значение.

        Raises:
            ValueError: Неверный формат почты.

        Returns:
            str: Валидированное значение.
        """
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(email_regex, value):
            raise ValueError("Invalid email format")

        return value

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        """Валидатор пароля игрока.

        Args:
            value (str): Невалидированное значение.

        Raises:
            ValueError: Неверный формат пароля.

        Returns:
            str: Валидированное значение.
        """
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError("Password must contain at least one special character")

        return value


class RegisterUserResponse(BaseModel):
    id: UUID = Field(
        description="Идентификатор пользователя", examples=["16fd2706-8baf-433b-82eb-8c7fada847da"]
    )
    name: str = Field(description="Имя пользователя", max_length=255, examples=["nagibator_rus"])


class AuthorizeUserRequest(BaseModel):
    access_token: str = Field(description="JWT токен доступа")


class AuthorizeUserResponse(BaseModel):
    id: UUID = Field(
        description="Идентификатор пользователя", examples=["16fd2706-8baf-433b-82eb-8c7fada847da"]
    )
    name: str = Field(description="Имя пользователя", max_length=255, examples=["nagibator_rus"])
    is_admin: bool = Field(description="Флаг админ прав", examples=["False"])
