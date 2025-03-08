from fastapi import APIRouter


router = APIRouter()


@router.get("/authenticate")
async def authenticate_user() -> None:
    pass


@router.post("/register")
async def register_user() -> None:
    pass
