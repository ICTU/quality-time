"""Base class for Cobertura coverage report collectors."""

from base_collectors import XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from model import SourceMeasurement, SourceResponses


class CoberturaCoverageBaseClass(XMLFileSourceCollector):
    """Base class for Cobertura coverage collectors."""

    coverage_type = "Subclass responsibility (Cobertura has: lines, branches)"

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the coverage from the responses."""
        valid, covered = 0, 0
        for response in responses:
            tree = await parse_source_response_xml(response)
            valid += int(tree.get(f"{self.coverage_type}-valid", 0))
            covered += int(tree.get(f"{self.coverage_type}-covered", 0))
        return SourceMeasurement(value=str(valid - covered), total=str(valid))
