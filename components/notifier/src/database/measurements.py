"""Meaasurements collection."""

import pymongo
from pymongo.database import Database

from shared.model.measurement import Measurement
from shared.model.metric import Metric


def get_recent_measurements(
    database: Database,
    metrics: list[Metric],
    limit_per_metric: int = 2,
) -> list[Measurement]:  # pragma: no feature-test-cover
    """Return recent measurements for the specified metrics, without entities and issue status."""
    projection = {
        "_id": False,
        "sources.entities": False,
        "sources.entity_user_data": False,
        "issue_status": False,
    }
    measurements: list = []
    for metric in metrics:
        measurement_data = list(
            database["measurements"].find(
                {"metric_uuid": metric.uuid},
                limit=limit_per_metric,
                sort=[("start", pymongo.DESCENDING)],
                projection=projection,
            ),
        )
        for measurement in measurement_data:
            measurements.append(Measurement(metric, measurement))

    return measurements
