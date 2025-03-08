from fastapi import FastAPI

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # on_startup

    yield

    # on_shutdown


service = FastAPI(lifespan=lifespan)
