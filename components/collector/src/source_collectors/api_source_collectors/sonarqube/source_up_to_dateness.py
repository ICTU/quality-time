"""Collectors for SonarQube."""

from datetime import datetime

from dateutil.parser import isoparse

from base_collectors import SourceUpToDatenessCollector
from collector_utilities.type import URL, Response
from source_model import SourceResponses

from .base import SonarQubeCollector


class SonarQubeSourceUpToDateness(SonarQubeCollector, SourceUpToDatenessCollector):
    """SonarQube source up-to-dateness."""

    async def _api_url(self) -> URL:
        url = await super()._api_url()
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/api/project_analyses/search?project={component}&branch={branch}")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        url = await super()._landing_url(responses)
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/project/activity?id={component}&branch={branch}")

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        return isoparse((await response.json())["analyses"][0]["date"])
