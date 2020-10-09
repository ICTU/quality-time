"""API source collector base classes."""

from abc import ABC
from datetime import datetime

from collector_utilities.type import URL, Response

from .source_collector import SourceCollector, SourceUpToDatenessCollector
from source_model import SourceResponses


class JenkinsPluginCollector(SourceCollector, ABC):  # skipcq: PYL-W0223
    """Base class for Jenkins plugin collectors."""
    plugin = "subclass responsibility"
    depth = 0

    async def _api_url(self) -> URL:
        depth = f"?depth={self.depth}" if self.depth > 0 else ""
        return URL(f"{await super()._api_url()}/lastSuccessfulBuild/{self.plugin}/api/json{depth}")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        return URL(f"{await super()._api_url()}/lastSuccessfulBuild/{self.plugin}")


class JenkinsPluginSourceUpToDatenessCollector(SourceUpToDatenessCollector):
    """Base class for Jenkins plugin source up-to-dateness collectors."""

    async def _api_url(self) -> URL:
        return URL(f"{await super()._api_url()}/lastSuccessfulBuild/api/json")

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        return datetime.fromtimestamp(float((await response.json())["timestamp"]) / 1000.)
