import bcrypt as bc
from fastapi import APIRouter, Body, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from database.models import Password, User
from schemas.auth import (
    AuthenticateUserRequest,
    AuthenticateUserResponse,
    AuthorizeUserRequest,
    AuthorizeUserResponse,
    RegisterUserRequest,
    RegisterUserResponse,
)
from service_logging import logger
from utils.auth import decode_access_token, encode_access_token, identificate_user

router = APIRouter()


@router.post("/login", summary="Аутентификация пользователя")
async def authenticate_user(
    user_data: AuthenticateUserRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthenticateUserResponse:
    """Аутентифицирует пользователя, возвращает JWT токен авторизации в случае успеха."""
    # Идентификация
    logger.info("User identification...")
    user = await identificate_user(db, user_data.username)
    if user is None:
        detail = "User identification failed."
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )

    # Аутентификация
    logger.info("User authentication...")
    password = await user.awaitable_attrs.password
    is_valid = bc.checkpw(user_data.password.encode(), password.hash.encode())
    if not is_valid:
        detail = "User authentication failed."
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

    logger.success("Authentication is complete. Issuing a JWT token.")
    access_token = await encode_access_token(subject=user.id)
    return AuthenticateUserResponse(access_token=access_token)


@router.post("/register", summary="Регистрация пользователя")
async def register_user(
    user_data: RegisterUserRequest = Body(...),
    db: AsyncSession = Depends(get_db),
) -> RegisterUserResponse:
    """Регистрирует нового пользователя, создает для него и его пароля записи в базе данных."""
    # Создание нового пользователя
    logger.info("User registration...")
    new_user = User(name=user_data.name, email=user_data.email)
    try:
        db.add(new_user)
        await db.flush()
        await db.refresh(new_user)

    except Exception as _:
        await db.rollback()
        detail = "User with this data already created."
        logger.error(f"Registration failed: {detail}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

    # Создание пароля привязанного к пользователю
    logger.info("Creating password...")
    hash = bc.hashpw(user_data.password.encode(), bc.gensalt())
    new_user_password = Password(user=new_user, hash=hash.decode())
    db.add(new_user_password)
    await db.commit()

    item = RegisterUserResponse(id=new_user.id, name=new_user.name)
    logger.success(f"User has been successfully registered: {item.id}")

    return item


@router.post("/verify", summary="Авторизация пользователя")
async def authorize_user(
    user_data: AuthorizeUserRequest = Body(...),
    db: AsyncSession = Depends(get_db),
) -> AuthorizeUserResponse:
    # Расшифровка JWT токена доступа
    logger.success("Decoding a JWT token....")
    user_id = await decode_access_token(access_token=user_data.access_token)
    print(user_id)
    if user_id is None:
        detail = "Access token is invalid."
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )

    # Получение данных о пользователе
    logger.info("Getting information about an user...")
    stmt = select(User).where((User.id == user_id) & (~User.is_disabled))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        detail = "User account is disabled or does not exist."
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )

    item = AuthorizeUserResponse(id=user.id, name=user.name, is_admin=user.is_admin)
    logger.success(f"User authorized: {item.id}")

    return item
