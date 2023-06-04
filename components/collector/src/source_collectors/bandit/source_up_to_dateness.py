"""Bandit source up-to-dateness collector."""

from datetime import datetime

from base_collectors import JSONFileSourceCollector, TimePassedCollector
from collector_utilities.date_time import parse_datetime
from collector_utilities.type import Response


class BanditSourceUpToDateness(JSONFileSourceCollector, TimePassedCollector):
    """Bandit collector for source up-to-dateness."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the timestamp."""
        return parse_datetime((await response.json(content_type=None))["generated_at"])
