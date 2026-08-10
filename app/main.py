from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.logging import configure_logging
from app.models import ItemModel  # noqa: F401 — register model with Base
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Hello World CRUD", lifespan=lifespan)
app.include_router(router)
