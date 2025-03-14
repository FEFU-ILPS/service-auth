import re
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# TODO: Изменить название
class RegisteredUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Annotated[UUID, Field(...)]
    name: Annotated[str, Field(max_length=255)]
    email: Annotated[str, Field(max_length=255)]
    # TODO: Добавить поля

    @field_validator("email")
    def validate_email(cls, value):
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, value):
            raise ValueError("Invalid email format")
        return value
