"""Quality-time source up-to-dateness collector."""

from datetime import datetime
from urllib import parse

from dateutil.parser import parse as parse_datetime

from base_collectors import SourceUpToDatenessCollector
from collector_utilities.type import Response, URL

from .base import QualityTimeCollector


class QualityTimeSourceUpToDateness(QualityTimeCollector, SourceUpToDatenessCollector):
    """Collector to get the "source up-to-dateness" metric from Quality-time."""

    async def _api_url(self) -> URL:
        """Extend to add the reports API path."""
        parts = parse.urlsplit(await super()._api_url())
        netloc = f"{parts.netloc.split(':')[0]}"
        return URL(parse.urlunsplit((parts.scheme, netloc, f"{parts.path}/reports", "", "")))

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the oldest datetime from the recent measurements."""
        measurement_dates = []
        for report in await self._get_reports(response):
            for subject in report.get("subjects", {}).values():
                for metric in subject.get("metrics", {}).values():
                    if recent_measurements := metric.get("recent_measurements", []):
                        measurement_dates.append(parse_datetime(recent_measurements[-1]["end"]))
        return min(measurement_dates, default=datetime.min)
