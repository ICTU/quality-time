"""Jacoco Jenkins plugin coverage report collector."""

from datetime import datetime
from typing import Tuple

from collector_utilities.type import Entities, Response, Responses, URL, Value

from .source_collector import SourceCollector, SourceUpToDatenessCollector


class JacocoJenkinsPluginBaseClass(SourceCollector):
    """Base class for Jacoco Jenkins plugin collectors."""

    def _landing_url(self, responses: Responses) -> URL:
        return URL(f"{super()._api_url()}/lastSuccessfulBuild/jacoco")


class JacocoJenkinsPluginCoverageBaseClass(JacocoJenkinsPluginBaseClass):
    """Base class for Jacoco Jenkins plugin coverage collectors."""

    coverage_type = "subclass responsibility"

    def _api_url(self) -> URL:
        return URL(f"{super()._api_url()}/lastSuccessfulBuild/jacoco/api/json")

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        line_coverage = responses[0].json()[f"{self.coverage_type}Coverage"]
        return str(line_coverage["missed"]), str(line_coverage["total"]), []


class JacocoJenkinsPluginUncoveredLines(JacocoJenkinsPluginCoverageBaseClass):
    """Collector for Jacoco Jenkins plugin uncovered lines."""

    coverage_type = "line"


class JacocoJenkinsPluginUncoveredBranches(JacocoJenkinsPluginCoverageBaseClass):
    """Collector for Jacoco Jenkins plugin uncovered branches."""

    coverage_type = "branch"


class JacocoJenkinsPluginSourceUpToDateness(JacocoJenkinsPluginBaseClass, SourceUpToDatenessCollector):
    """Collector for the up to dateness of the Jacoco Jenkins plugin coverage report."""

    def _api_url(self) -> URL:
        return URL(f"{super()._api_url()}/lastSuccessfulBuild/api/json")

    def _parse_source_response_date_time(self, response: Response) -> datetime:
        return datetime.fromtimestamp(float(response.json()["timestamp"]) / 1000.)
