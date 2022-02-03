"""Collector for the time passed since the latest SonarQube analysis."""

from datetime import datetime

from dateutil.parser import isoparse

from base_collectors import TimePassedCollector
from collector_utilities.type import URL, Response
from model import SourceResponses

from .base import SonarQubeCollector


class SonarQubeTimePassed(SonarQubeCollector, TimePassedCollector):
    """Collector for the time passed since the latest SonarQube analysis."""

    async def _api_url(self) -> URL:
        """Extend to add the project analyses path and parameters."""
        url = await super()._api_url()
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/api/project_analyses/search?project={component}&branch={branch}")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the project activity path and parameters."""
        url = await super()._landing_url(responses)
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/project/activity?id={component}&branch={branch}")

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the date of the most recent analysis."""
        return isoparse((await response.json())["analyses"][0]["date"])
