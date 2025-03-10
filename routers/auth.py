import bcrypt as bc
from fastapi import APIRouter, Body, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from database.models import Password, User
from schemas.auth import AuthenticateUserRequest, AuthorizationTokenResponse, RegisterUserRequest
from utils.auth import encode_access_token, identificate_user

router = APIRouter()


@router.get("/login", summary="Аутентификация пользователя")
async def authenticate_user(
    user_data: AuthenticateUserRequest = Depends(),
    db: AsyncSession = Depends(get_db),
) -> AuthorizationTokenResponse:
    """Аутентифицирует пользователя, возвращает JWT токен авторизации в случае успеха."""
    # Идентификация
    user = await identificate_user(db, user_data.name)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User identification failed.",
        )

    # Аутентификация
    password = await user.awaitable_attrs.password
    is_valid = bc.checkpw(user_data.password.encode(), password.hash.encode())
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User authentication failed.",
        )

    access_token = await encode_access_token(subject=user.name)
    return AuthorizationTokenResponse(access_token=access_token)


@router.post("/register", summary="Регистрация пользователя")
async def register_user(
    user_data: RegisterUserRequest = Body(...),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Регистрирует нового пользователя, создает для него и его пароля записи в базе данных."""
    # Создание нового пользователя
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

    # Создание пароля привязанного к пользователю
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
