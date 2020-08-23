"""API source collector base classes."""

from datetime import datetime

from collector_utilities.type import URL, Response

from .source_collector import SourceUpToDatenessCollector


class JenkinsPluginSourceUpToDatenessCollector(SourceUpToDatenessCollector):
    """Base class for Jenkins plugin source up-to-dateness collectors."""

    async def _api_url(self) -> URL:
        return URL(f"{await super()._api_url()}/lastSuccessfulBuild/api/json")

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        return datetime.fromtimestamp(float((await response.json())["timestamp"]) / 1000.)
