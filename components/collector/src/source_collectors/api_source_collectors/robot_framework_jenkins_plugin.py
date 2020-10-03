"""Robot Framework Jenkins plugin collector."""

from abc import ABC

from base_collectors import JenkinsPluginSourceUpToDatenessCollector, SourceCollector
from collector_utilities.type import URL
from source_model import SourceMeasurement, SourceResponses


class RobotFrameworkJenkinsPluginBaseClass(SourceCollector, ABC):  # skipcq: PYL-W0223
    """Base class for Robot Framework Jenkins plugin collectors."""

    async def _landing_url(self, responses: SourceResponses) -> URL:
        return URL(f"{await super()._api_url()}/lastSuccessfulBuild/robot")


class RobotFrameworkJenkinsPluginTests(RobotFrameworkJenkinsPluginBaseClass):
    """Collector for Robot Framework Jenkins plugin tests."""

    async def _api_url(self) -> URL:
        return URL(f"{await super()._api_url()}/lastSuccessfulBuild/robot/api/json")

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        json = await responses[0].json()
        return SourceMeasurement(value=str(json["overallTotal"]), total=str(json["overallTotal"]))


class RobotFrameworkJenkinsPluginSourceUpToDateness(
        RobotFrameworkJenkinsPluginBaseClass, JenkinsPluginSourceUpToDatenessCollector):
    """Collector for the up-to-dateness of the Robot Framework Jenkins plugin coverage report."""
