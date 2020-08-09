"""Jacoco coverage report collector."""

from datetime import datetime

from defusedxml import ElementTree

from collector_utilities.type import Response
from base_collectors import XMLFileSourceCollector, SourceMeasurement, SourceResponses, SourceUpToDatenessCollector


class JacocoCoverageBaseClass(XMLFileSourceCollector):
    """Base class for Jacoco coverage collectors."""

    coverage_type = "Subclass responsibility (Jacoco has: line, branch, instruction, complexity, method, class)"

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        missed, covered = 0, 0
        for response in responses:
            tree = ElementTree.fromstring(await response.text())
            counter = [c for c in tree.findall("counter") if c.get("type").lower() == self.coverage_type][0]
            missed += int(counter.get("missed"))
            covered += int(counter.get("covered"))
        return SourceMeasurement(value=str(missed), total=str(missed + covered))


class JacocoUncoveredLines(JacocoCoverageBaseClass):
    """Source class to get the number of uncovered lines from Jacoco XML reports."""

    coverage_type = "line"


class JacocoUncoveredBranches(JacocoCoverageBaseClass):
    """Source class to get the number of uncovered lines from Jacoco XML reports."""

    coverage_type = "branch"


class JacocoSourceUpToDateness(XMLFileSourceCollector, SourceUpToDatenessCollector):
    """Collector to collect the Jacoco report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        tree = ElementTree.fromstring(await response.text())
        session_info = tree.find(".//sessioninfo")
        timestamp = session_info.get("dump") if session_info is not None else "0"
        return datetime.utcfromtimestamp(int(timestamp) / 1000.)
