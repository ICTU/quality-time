"""Reports collection."""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorCursor, AsyncIOMotorDatabase

from model.metric import Metric
from utilities.type import MetricId

from .data_models import latest_data_model


def latest_reports(database: AsyncIOMotorDatabase) -> AsyncIOMotorCursor:
    """Return the latest, undeleted, reports in the reports collection."""
    return database.reports.find({"last": True, "deleted": {"$exists": False}})


async def latest_metric(database: AsyncIOMotorDatabase, metric_uuid: MetricId) -> Optional[Metric]:
    """Return the latest metric with the specified metric uuid."""
    async for report in latest_reports(database):
        for subject in report.get("subjects", {}).values():
            metrics = subject.get("metrics", {})
            if metric_uuid in metrics:
                return Metric(await latest_data_model(database), metrics[metric_uuid], metric_uuid)
    return None
