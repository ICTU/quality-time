"""Metrics endpoint(s)."""

from typing import Any

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from initialization.database import quality_time_database
from database.reports import latest_reports


router = APIRouter()


@router.get("/metrics")
async def get_metrics(database: AsyncIOMotorDatabase = Depends(quality_time_database)) -> dict[str, Any]:
    """Return all metrics from all (latest) reports."""
    metrics: dict[str, Any] = {}
    async for report in latest_reports(database):
        issue_tracker = report.get("issue_tracker", {})
        has_issue_tracker = bool(issue_tracker.get("type") and issue_tracker.get("parameters", {}).get("url"))
        for subject in report["subjects"].values():
            for metric_uuid, metric in subject["metrics"].items():
                metric["report_uuid"] = report["report_uuid"]
                if has_issue_tracker and metric.get("issue_ids"):
                    metric["issue_tracker"] = issue_tracker
                metrics[metric_uuid] = metric
    return metrics
