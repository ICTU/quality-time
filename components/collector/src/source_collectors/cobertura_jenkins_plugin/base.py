"""Cobertura Jenkins plugin coverage report collector base classes."""

from abc import ABC

from shared.utils.functions import first

from base_collectors import JenkinsPluginCollector
from model import SourceMeasurement, SourceResponses


class CoberturaJenkinsPluginBaseClass(JenkinsPluginCollector, ABC):
    """Base class for Cobertura Jenkins plugin collectors."""

    plugin = "cobertura"
    depth = 2


class CoberturaJenkinsPluginCoverageBaseClass(CoberturaJenkinsPluginBaseClass):
    """Base class for Cobertura Jenkins plugin coverage collectors."""

    coverage_type = "subclass responsibility"

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the coverage measurements."""
        elements = (await responses[0].json())["results"]["elements"]
        coverage = first(elements, lambda element: element["name"].lower() == self.coverage_type)
        total = int(coverage["denominator"])
        return SourceMeasurement(value=str(total - int(coverage["numerator"])), total=str(total))
