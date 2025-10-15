"""Trivy JSON collector."""

from typing import TYPE_CHECKING

from base_collectors import JSONFileSourceCollector, TimePassedCollector
from collector_utilities.date_time import parse_datetime
from collector_utilities.exceptions import CollectorError

if TYPE_CHECKING:
    from datetime import datetime

    from collector_utilities.type import Response


class TrivyJSONSourceUpToDateness(JSONFileSourceCollector, TimePassedCollector):
    """Trivy JSON collector for source up-to-dateness."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the date of the most recent analysis."""
        json = await response.json()
        try:
            created_at = json["CreatedAt"]
        except TypeError as error:
            message = "Measuring source up-to-dateness is not supported with Trivy JSON schema version 1"
            raise CollectorError(message) from error
        return parse_datetime(created_at)
