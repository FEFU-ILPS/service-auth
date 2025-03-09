import bcrypt as bc
from fastapi import APIRouter, Body, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from database.models import Password, User
from schemas.auth import RegisterUserRequest

router = APIRouter()


@router.get("/authenticate")
async def authenticate_user() -> None:
    pass


@router.post("/register")
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
    new_user_password = Password(user=new_user, hash=hash)
    db.add(new_user_password)
    await db.commit()

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "User registered successfully",
            "user_uuid": new_user.id,
        },
    )
