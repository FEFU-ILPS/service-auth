import bcrypt as bc
from fastapi import APIRouter, Body, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from database.models import Password, User
from schemas.auth import RegisterUserRequest, AuthenticateUserRequest

router = APIRouter()


@router.get("/authenticate", summary="Аутентификация пользователя")
async def authenticate_user(
    user_data: AuthenticateUserRequest = Depends(),
    db: AsyncSession = Depends(get_db),
) -> None:
    stmt = select(User).where(User.name == user_data.name)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User identification failed.",
        )

    password = await user.awaitable_attrs.password

    is_valid = bc.checkpw(user_data.password.encode(), password.hash.encode())
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User authentication failed.",
        )

    return {
        "access_token": "token_here",
        "authentication_type": "Bearer",
    }


@router.post("/register", summary="Регистрация пользователя")
async def register_user(
    user_data: RegisterUserRequest = Body(...),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Регистрирует нового пользователя, создает для него и его пароля
    записи в базе данных.
    """
    # * Добавляем нового пользователя
    new_user = User(name=user_data.name, email=user_data.email)
    try:
        db.add(new_user)
        await db.flush()
        await db.refresh(new_user)

    except Exception as _:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this data already created.",
        )

    # * Добавляем пароль привязанный к пользователю
    hash = bc.hashpw(user_data.password.encode(), bc.gensalt())
    new_user_password = Password(user=new_user, hash=hash.decode())
    db.add(new_user_password)
    await db.commit()

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "User registered successfully",
            "user_uuid": str(new_user.id),
        },
    )
