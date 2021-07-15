"""Base classes for NCover collectors."""

import json
from abc import ABC

from bs4 import BeautifulSoup

from base_collectors import HTMLFileSourceCollector
from collector_utilities.type import Response
from model import SourceMeasurement, SourceResponses


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

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the coverage from the NCover HTML/Javascript."""
        covered, total = 0, 0
        for response in responses:
            script = await self._find_script(response, "ncover.execution.stats = ")
            json_string = script.strip().removeprefix("ncover.execution.stats = ").strip(";")
            coverage = json.loads(json_string)[f"{self.coverage_type}Coverage"]
            covered += int(coverage["coveredPoints"])
            total += int(coverage["coveragePoints"])
        return SourceMeasurement(value=str(total - covered), total=str(total))
