from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from techgear_api.database import close_mongo_connection, connect_to_mongo
from techgear_api.routers.orders import router as orders_router
from techgear_api.routers.products import router as products_router


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
app.include_router(products_router)
app.include_router(orders_router)


@app.get("/health", tags=["Sistema"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
