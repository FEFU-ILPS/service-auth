from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Path

router = APIRouter(prefix="/users")


@router.get("")
async def get_users() -> None:
    pass


@router.get("/{uuid}")
async def get_user(uuid: Annotated[UUID, Path(...)]) -> None:
    pass


@router.update("/{uuid}")
async def update_user(uuid: Annotated[UUID, Path(...)]) -> None:
    pass
