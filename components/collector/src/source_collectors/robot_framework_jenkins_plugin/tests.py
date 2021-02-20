"""Robot Framework Jenkins plugin tests collector."""

from typing import cast, List

from source_model import SourceMeasurement, SourceResponses

from .base import RobotFrameworkJenkinsPluginBaseClass


class RobotFrameworkJenkinsPluginTests(RobotFrameworkJenkinsPluginBaseClass):
    """Collector for Robot Framework Jenkins plugin tests."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the number of tests."""
        statuses = cast(List[str], self._parameter("test_result"))
        json = await responses[0].json()
        value = sum(int(json[status]) for status in statuses)
        return SourceMeasurement(value=str(value), total=str(json["overallTotal"]))
