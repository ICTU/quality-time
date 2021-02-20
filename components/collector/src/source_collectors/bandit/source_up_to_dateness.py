"""Bandit source up-to-dateness collector."""

from datetime import datetime

from dateutil.parser import parse

from base_collectors import JSONFileSourceCollector, SourceUpToDatenessCollector
from collector_utilities.type import Response


class BanditSourceUpToDateness(JSONFileSourceCollector, SourceUpToDatenessCollector):
    """Bandit collector for source up-to-dateness."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the timestamp."""
        return parse((await response.json(content_type=None))["generated_at"])
