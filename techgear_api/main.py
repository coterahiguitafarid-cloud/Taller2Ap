from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from database import close_mongo_connection, connect_to_mongo


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await connect_to_mongo()
    try:
        yield
    finally:
        await close_mongo_connection()


app = FastAPI(
    title="TechGear API",
    description="API de catálogo de productos y pedidos de TechGear.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["Sistema"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
