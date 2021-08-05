"""Base classes for Quality-time collectors."""

from abc import ABC
from typing import Any

from base_collectors import SourceCollector, SourceCollectorException
from collector_utilities.type import Response, URL


class QualityTimeCollector(SourceCollector, ABC):  # skipcq: PYL-W0223
    """Base collector for Quality-time metrics."""

    API_VERSION = "v3"

    async def _api_url(self) -> URL:
        """Get the api url for this api version"""
        api_url = await super()._api_url()
        return URL(f"{api_url}/api/{self.API_VERSION}")

    async def _get_reports(self, response: Response) -> list[dict[str, Any]]:
        """Get the relevant reports from the reports response."""
        report_titles_or_ids = set(self._parameter("reports"))
        response_json = await response.json()
        reports = list(response_json["reports"])
        if report_titles_or_ids:
            reports = [report for report in reports if report_titles_or_ids & {report["title"], report["report_uuid"]}]
        if not reports:
            message = "No reports found" + (f" with title or id {report_titles_or_ids}" if report_titles_or_ids else "")
            raise SourceCollectorException(message)
        return reports
