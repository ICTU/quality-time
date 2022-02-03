"""API source collector base classes."""

from abc import ABC
from datetime import datetime

from collector_utilities.type import URL, Response

from model import SourceResponses
from .source_collector import SourceCollector, TimePassedCollector


class JenkinsPluginCollector(SourceCollector, ABC):  # skipcq: PYL-W0223
    """Base class for Jenkins plugin collectors."""

    plugin = "Subclass responsibility"
    depth = 0  # Override to pass a higher depth to the plugin API, which means: "please, give me more details"

    async def _api_url(self) -> URL:
        """Extend to return the API URL for the plugin, with an optional depth."""
        depth = f"?depth={self.depth}" if self.depth > 0 else ""
        return URL(f"{await super()._api_url()}/lastSuccessfulBuild/{self.plugin}/api/json{depth}")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Override to return the URL for the plugin."""
        return URL(f"{await super()._api_url()}/lastSuccessfulBuild/{self.plugin}")


class JenkinsPluginTimePassedCollector(TimePassedCollector):
    """Base class for Jenkins plugin time passed collectors."""

    async def _api_url(self) -> URL:
        """Extend to return the API URL for the job."""
        return URL(f"{await super()._api_url()}/lastSuccessfulBuild/api/json")

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the job's timestamp."""
        return datetime.fromtimestamp(float((await response.json())["timestamp"]) / 1000.0)
