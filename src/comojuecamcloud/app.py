from contextlib import asynccontextmanager

from fastapi import FastAPI

from comojuecamcloud.api import clients_router, websocket_router
from comojuecamcloud.database import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="ComojueCamCloud",
    description="Telemetry server for ComojueCam Android app",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(websocket_router)
app.include_router(clients_router)
