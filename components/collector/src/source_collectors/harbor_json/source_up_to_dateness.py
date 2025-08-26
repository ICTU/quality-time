"""Harbor JSON source up-to-dateness collector."""

from datetime import datetime

from base_collectors import JSONFileSourceCollector, TimePassedCollector
from collector_utilities.date_time import parse_datetime
from collector_utilities.type import Response

from .json_types import REPORT_MIME_TYPE


class HarborJSONSourceUpToDateness(JSONFileSourceCollector, TimePassedCollector):
    """Harbor JSON collector for source up-to-dateness."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the date of the most recent analysis."""
        return parse_datetime((await response.json())[REPORT_MIME_TYPE]["generated_at"])
