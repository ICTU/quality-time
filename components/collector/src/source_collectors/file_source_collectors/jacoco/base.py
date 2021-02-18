"""Base classes for Jacoco coverage report unit tests."""

from base_collectors import XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from source_model import SourceMeasurement, SourceResponses


class JacocoCoverageBaseClass(XMLFileSourceCollector):
    """Base class for Jacoco coverage collectors."""

    coverage_type = "Subclass responsibility (Jacoco has: line, branch, instruction, complexity, method, class)"

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the coverage from the JaCoCo XML."""
        missed, covered = 0, 0
        for response in responses:
            tree = await parse_source_response_xml(response)
            counters = [c for c in tree.findall("counter") if c.get("type", "").lower() == self.coverage_type]
            if counters:
                missed += int(counters[0].get("missed", 0))
                covered += int(counters[0].get("covered", 0))
        return SourceMeasurement(value=str(missed), total=str(missed + covered))
