"""Base classes for Quality-time collectors."""

from abc import ABC
from typing import TYPE_CHECKING, Any

from base_collectors import SourceCollector
from collector_utilities.exceptions import CollectorError

if TYPE_CHECKING:
    from collector_utilities.type import Response


class QualityTimeCollector(SourceCollector, ABC):
    """Base collector for Quality-time metrics."""

    async def _get_reports(self, response: Response) -> list[dict[str, Any]]:
        """Get the relevant reports from the reports response."""
        report_titles_or_ids = set(self._parameter("reports"))
        response_json = await response.json()
        reports = list(response_json["reports"])
        if report_titles_or_ids:
            reports = [report for report in reports if report_titles_or_ids & {report["title"], report["report_uuid"]}]
        if not reports:
            message = "No reports found" + (f" with title or id {report_titles_or_ids}" if report_titles_or_ids else "")
            raise CollectorError(message)
        return reports
