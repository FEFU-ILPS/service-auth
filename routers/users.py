from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from database.models import User
from schemas.users import UserResponse
from service_logging import logger

from .utils.pagination import PaginatedResponse, Pagination

router = APIRouter(prefix="/users")


@router.get("/", summary="Получить всех пользователей")
async def get_users(
    pg: Annotated[Pagination, Depends()],
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[UserResponse]:
    """Постранично возвращает список всех зарегистрированных пользователей."""
    logger.info("Getting the user list...")
    stmt = select(User).offset(pg.skip).limit(pg.size)
    result = await db.execute(stmt)
    users = result.scalars().all()

    stmt = select(func.count()).select_from(User)
    result = await db.execute(stmt)
    total = result.scalar_one()

    items = [UserResponse.model_validate(user) for user in users]
    logger.success(f"Received {len(items)} users.")

    return PaginatedResponse[UserResponse](
        items=items,
        page=pg.page,
        size=pg.size,
        total=total,
    )


@router.get("/{uuid}")
async def get_user(
    uuid: Annotated[UUID, Path(...)],
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Возвращает информацию о конкретном зарегистрированном пользователе по его UUID."""
    logger.info("Getting information about an user...")
    stmt = select(User).where(User.id == uuid)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        detail = "User not found."
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )
    item = UserResponse.model_validate(user)
    logger.success(f"Text received: {item.id}")

    return item
