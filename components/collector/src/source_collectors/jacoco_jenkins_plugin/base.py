"""Jacoco Jenkins plugin coverage report collector base classes."""

from abc import ABC

from base_collectors import JenkinsPluginCollector
from source_model import SourceMeasurement, SourceResponses


class JacocoJenkinsPluginBaseClass(JenkinsPluginCollector, ABC):  # skipcq: PYL-W0223
    """Base class for Jacoco Jenkins plugin collectors."""

    plugin = "jacoco"


class JacocoJenkinsPluginCoverageBaseClass(JacocoJenkinsPluginBaseClass):
    """Base class for Jacoco Jenkins plugin coverage collectors."""

    coverage_type = "subclass responsibility"

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the coverage data from the response."""
        coverage = (await responses[0].json())[f"{self.coverage_type}Coverage"]
        return SourceMeasurement(value=str(coverage["missed"]), total=str(coverage["total"]))
