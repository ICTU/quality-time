"""Base classes for Quality-time collectors."""

from abc import ABC
from typing import Any, Dict, List
from urllib import parse

from base_collectors import SourceCollector, SourceCollectorException
from collector_utilities.type import URL, Response


class QualityTimeCollector(SourceCollector, ABC):
    """Base collector for Quality-time metrics."""

    async def _api_url(self) -> URL:
        """Extend to add the reports API path."""
        parts = parse.urlsplit(await super()._api_url())
        netloc = f"{parts.netloc.split(':')[0]}"
        return URL(parse.urlunsplit((parts.scheme, netloc, "/api/v3/reports", "", "")))

    async def _get_reports(self, response: Response) -> List[Dict[str, Any]]:
        """Get the relevant reports from the reports response."""
        report_titles_or_ids = set(self._parameter("reports"))
        reports = list((await response.json())["reports"])
        reports = (
            [report for report in reports if (report_titles_or_ids & {report["title"], report["report_uuid"]})]
            if report_titles_or_ids
            else reports
        )
        if not reports:
            message = "No reports found" + (f" with title or id {report_titles_or_ids}" if report_titles_or_ids else "")
            raise SourceCollectorException(message)
        return reports
