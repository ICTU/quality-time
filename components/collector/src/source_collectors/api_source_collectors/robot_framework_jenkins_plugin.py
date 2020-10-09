"""Robot Framework Jenkins plugin collector."""

from abc import ABC
from typing import cast, List

from base_collectors import JenkinsPluginCollector, JenkinsPluginSourceUpToDatenessCollector
from source_model import SourceMeasurement, SourceResponses


class RobotFrameworkJenkinsPluginBaseClass(JenkinsPluginCollector, ABC):  # skipcq: PYL-W0223
    """Base class for Robot Framework Jenkins plugin collectors."""

    plugin = "robot"


class RobotFrameworkJenkinsPluginTests(RobotFrameworkJenkinsPluginBaseClass):
    """Collector for Robot Framework Jenkins plugin tests."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        statuses = cast(List[str], self._parameter("test_result"))
        json = await responses[0].json()
        value = sum(int(json[status]) for status in statuses)
        return SourceMeasurement(value=str(value), total=str(json["overallTotal"]))


class RobotFrameworkJenkinsPluginSourceUpToDateness(
        RobotFrameworkJenkinsPluginBaseClass, JenkinsPluginSourceUpToDatenessCollector):
    """Collector for the up-to-dateness of the Robot Framework Jenkins plugin coverage report."""
