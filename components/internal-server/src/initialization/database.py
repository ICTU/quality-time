"""Quality-time database."""

import os

from asyncstdlib.functools import cache
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


@cache
async def quality_time_database() -> AsyncIOMotorDatabase:
    """Return the (cached) Quality-time database."""
    database_url = os.environ.get("DATABASE_URL", "mongodb://root:root@localhost:27017")
    client = AsyncIOMotorClient(database_url)
    return client.quality_time_db
