from contextlib import asynccontextmanager

from fastapi import FastAPI

from routers import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # on_startup

    yield

    # on_shutdown


service = FastAPI(lifespan=lifespan)

service.include_router(auth_router)
