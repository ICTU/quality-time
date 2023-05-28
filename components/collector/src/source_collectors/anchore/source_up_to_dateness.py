"""Anchore source up-to-dateness collector."""

from datetime import datetime
from typing import cast

from base_collectors import JSONFileSourceCollector, TimePassedCollector
from collector_utilities.date_time import now, parse_datetime
from collector_utilities.type import URL, Response


class AnchoreSourceUpToDateness(JSONFileSourceCollector, TimePassedCollector):
    """Anchore collector for source up-to-dateness."""

    async def _api_url(self) -> URL:
        """Override to return the details URL."""
        return URL(cast(str, self._parameter("details_url")))

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the analysis date and time from the report."""
        details = await response.json(content_type=None)
        return (
            parse_datetime(details[0]["analyzed_at"])
            if isinstance(details, list) and details and "analyzed_at" in details[0]
            else now()
        )
