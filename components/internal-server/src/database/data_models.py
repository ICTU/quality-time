"""Data models collection."""

import pymongo
from motor.motor_asyncio import AsyncIOMotorDatabase


async def latest_data_model(database: AsyncIOMotorDatabase):
    """Return the latest data model."""
    if data_model := await database.datamodels.find_one(sort=[("timestamp", pymongo.DESCENDING)]):
        data_model["_id"] = str(data_model["_id"])
    return data_model or {}
