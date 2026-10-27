from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongodb_uri: str = Field(
        validation_alias=AliasChoices("MONGODB_URI", "MONGO_URI")
    )
    mongodb_database: str = "techgear"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


client: AsyncIOMotorClient | None = None
database: AsyncIOMotorDatabase | None = None


async def connect_to_mongo() -> None:
    global client, database

    settings = Settings()
    mongo_client = AsyncIOMotorClient(settings.mongodb_uri)
    connected = False
    try:
        await mongo_client.admin.command("ping")
        connected = True
    finally:
        if not connected:
            mongo_client.close()
    client = mongo_client
    database = mongo_client[settings.mongodb_database]


async def close_mongo_connection() -> None:
    global client, database

    if client is not None:
        client.close()
    client = None
    database = None


def get_database() -> AsyncIOMotorDatabase:
    if database is None:
        raise RuntimeError("La conexión con MongoDB no está inicializada.")
    return database


def get_mongo_client() -> AsyncIOMotorClient:
    if client is None:
        raise RuntimeError("La conexión con MongoDB no está inicializada.")
    return client
