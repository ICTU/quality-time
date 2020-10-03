"""Cobertura Jenkins plugin coverage report collector."""

from base_collectors import JenkinsPluginSourceUpToDatenessCollector, SourceCollector
from collector_utilities.type import URL
from source_model import SourceMeasurement, SourceResponses


class CoberturaJenkinsPluginBaseClass(SourceCollector):
    """Base class for Cobertura Jenkins plugin collectors."""

    async def _landing_url(self, responses: SourceResponses) -> URL:
        return URL(f"{await super()._api_url()}/lastSuccessfulBuild/cobertura")


class CoberturaJenkinsPluginCoverageBaseClass(CoberturaJenkinsPluginBaseClass):
    """Base class for Cobertura Jenkins plugin coverage collectors."""

    coverage_type = "subclass responsibility"

    async def _api_url(self) -> URL:
        return URL(f"{await super()._api_url()}/lastSuccessfulBuild/cobertura/api/json?depth=2")

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        elements = (await responses[0].json())["results"]["elements"]
        coverage = [element for element in elements if element["name"].lower() == self.coverage_type][0]
        total = int(coverage["denominator"])
        return SourceMeasurement(value=str(total - int(coverage["numerator"])), total=str(total))


class CoberturaJenkinsPluginUncoveredLines(CoberturaJenkinsPluginCoverageBaseClass):
    """Collector for Cobertura Jenkins plugin uncovered lines."""

    coverage_type = "lines"


class CoberturaJenkinsPluginUncoveredBranches(CoberturaJenkinsPluginCoverageBaseClass):
    """Collector for Cobertura Jenkins plugin uncovered branches."""

    coverage_type = "conditionals"


class CoberturaJenkinsPluginSourceUpToDateness(
        CoberturaJenkinsPluginBaseClass, JenkinsPluginSourceUpToDatenessCollector):
    """Collector for the up to dateness of the Cobertura Jenkins plugin coverage report."""
