"""Anchore source up-to-dateness collector."""

from datetime import datetime, timezone
from typing import cast

from dateutil.parser import parse

from base_collectors import JSONFileSourceCollector, SourceUpToDatenessCollector
from collector_utilities.type import Response, URL


class AnchoreSourceUpToDateness(JSONFileSourceCollector, SourceUpToDatenessCollector):
    """Anchore collector for source up-to-dateness."""

    async def _api_url(self) -> URL:
        """Override to return the details URL."""
        return URL(cast(str, self._parameter("details_url")))

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the analysis date and time from the report."""
        details = await response.json(content_type=None)
        return (
            parse(details[0]["analyzed_at"])
            if isinstance(details, list) and details and "analyzed_at" in details[0]
            else datetime.now(timezone.utc)
        )
