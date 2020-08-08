"""NCover collectors."""

import re
import json
from abc import ABC
from datetime import datetime

from bs4 import BeautifulSoup

from collector_utilities.type import Response, Responses
from base_collectors import HTMLFileSourceCollector, SourceMeasurement, SourceUpToDatenessCollector


class NCoverBase(HTMLFileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for NCover collectors."""

    @staticmethod
    async def _find_script(response: Response, text: str) -> str:
        """Return the script containing the text."""
        for script in BeautifulSoup(await response.text(), "html.parser").find_all("script", type="text/javascript"):
            if text in script.string:
                return str(script.string)
        return ""  # pragma: no cover


class NCoverCoverageBase(NCoverBase, ABC):  # pylint: disable=abstract-method
    """Base class for NCover coverage collectors."""

    coverage_type = "Subclass responsibility"

    async def _parse_source_responses(self, responses: Responses) -> SourceMeasurement:
        covered, total = 0, 0
        for response in responses:
            script = await self._find_script(response, "ncover.execution.stats = ")
            json_string = script.strip()[len('ncover.execution.stats = '):].strip(";")
            coverage = json.loads(json_string)[f"{self.coverage_type}Coverage"]
            covered += int(coverage["coveredPoints"])
            total += int(coverage["coveragePoints"])
        return SourceMeasurement(str(total - covered), str(total))


class NCoverUncoveredLines(NCoverCoverageBase):
    """Collector to get the uncovered lines. Since NCover doesn't report lines, but sequence points, we use those.
    See http://www.ncover.com/blog/code-coverage-metrics-sequence-point-coverage/."""

    coverage_type = "sequencePoint"


class NCoverUncoveredBranches(NCoverCoverageBase):
    """Collector to get the uncovered branches."""

    coverage_type = "branch"


class NCoverSourceUpToDateness(NCoverBase, SourceUpToDatenessCollector):
    """Collector to collect the NCover report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        script = await self._find_script(response, "ncover.createDateTime")
        match = re.search(r"ncover\.createDateTime = '(\d+)'", script)
        timestamp = match.group(1) if match else ""
        return datetime.fromtimestamp(float(timestamp) / 1000)
