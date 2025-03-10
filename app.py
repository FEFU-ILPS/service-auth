from contextlib import asynccontextmanager

from fastapi import FastAPI

from routers import auth_router, users_router
from database import disconnect_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # on_startup

    yield

    # on_shutdown
    await disconnect_db()


service = FastAPI(lifespan=lifespan)

service.include_router(auth_router)
service.include_router(users_router)
