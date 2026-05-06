"""Quality-time source up-to-dateness collector."""

from typing import TYPE_CHECKING

from shared.model.iterators import metrics

from base_collectors import TimePassedCollector
from collector_utilities.date_time import MIN_DATETIME, parse_datetime
from collector_utilities.type import URL, Response

from .base import QualityTimeCollector

if TYPE_CHECKING:
    from datetime import datetime


class QualityTimeSourceUpToDateness(QualityTimeCollector, TimePassedCollector):
    """Collector to get the "source up-to-dateness" metric from Quality-time."""

    async def _api_url(self) -> URL:
        """Extend to add the reports API path."""
        return URL(await super()._api_url() + "/api/internal/report")

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the oldest datetime from the recent measurements."""
        reports = await self._get_reports(response)
        measurement_dates = [
            parse_datetime(metric["recent_measurements"][-1]["end"])
            for metric in metrics(*reports)
            if metric.get("recent_measurements", [])
        ]
        return min(measurement_dates, default=MIN_DATETIME)
