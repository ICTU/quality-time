"""Data model routes."""

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from initialization.database import quality_time_database
from database.data_models import latest_data_model


router = APIRouter()


@router.get("data_model")
async def get_data_model(database: AsyncIOMotorDatabase = Depends(quality_time_database)):
    """Return the latest data model."""
    return await latest_data_model(database)
