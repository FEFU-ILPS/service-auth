from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from configs import configs
from database.models import User


async def identificate_user(db: AsyncSession, name: str) -> Optional[User]:
    """Производит идентификацию пользхователя, путем поиска записи
    о нем в базе данных.

    Args:
        db (AsyncSession): Асинхронная сессия подключения к базек данных.
        name (str): Имя пользователя.

    Returns:
        Optional[User]: Обьект пользователя.
    """
    stmt = select(User).where(User.name == name)
    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def encode_access_token(subject: str, expiration_delta: Optional[timedelta] = None) -> str:
    """Генерирует токенд тоступа для пользователя (subject).

    Args:
        subject (str): UUID пользователя.
        expiration_delta (Optional[timedelta]): Дельта времени, через которое токен просрочится.

    Returns:
        str: Токен доступа.
    """
    expiration_delta = expiration_delta or timedelta(minutes=configs.jwt.ACCESS_TOKEN_LIFETIME)
    now_time = datetime.now(tz=timezone.utc)

    payload = {
        "sub": subject,
        "iss": "ilps-service-auth",
        "exp": now_time + expiration_delta,
        "iat": now_time,
    }

    return jwt.encode(payload=payload, key=configs.jwt.SECRET)
