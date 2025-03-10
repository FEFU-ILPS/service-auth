from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Path, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from database.models import User
from schemas.users import RegisteredUserResponse

router = APIRouter(prefix="/users")


@router.get("", summary="Получить всех пользователей")
async def get_users(db: AsyncSession = Depends(get_db)) -> List[RegisteredUserResponse]:
    """Возвращает полный список всех зарегистрированных пользователей."""
    stmt = select(User)
    result = await db.execute(stmt)
    users = result.scalars().all()

    return [RegisteredUserResponse.model_validate(user) for user in users]


@router.get("/{uuid}")
async def get_user(
    uuid: Annotated[UUID, Path(...)],
    db: AsyncSession = Depends(get_db),
) -> RegisteredUserResponse:
    """Возвращает информацию о конкретном зарегистрированном пользователе по его UUID."""
    stmt = select(User).where(User.id == uuid)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return RegisteredUserResponse.model_validate(user)


@router.update("/{uuid}")
async def update_user(
    uuid: Annotated[UUID, Path(...)],
    db: AsyncSession = Depends(get_db),
) -> RegisteredUserResponse:
    pass
