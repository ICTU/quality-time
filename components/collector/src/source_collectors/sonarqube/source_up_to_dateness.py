"""Collectors for SonarQube."""

from datetime import datetime

from base_collectors import TimePassedCollector
from collector_utilities.date_time import parse_datetime
from collector_utilities.type import Response

from .base import SonarQubeProjectAnalysesBase


class SonarQubeSourceUpToDateness(SonarQubeProjectAnalysesBase, TimePassedCollector):
    """SonarQube source up-to-dateness."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the date of the most recent analysis."""
        return parse_datetime((await response.json())["analyses"][0]["date"])
