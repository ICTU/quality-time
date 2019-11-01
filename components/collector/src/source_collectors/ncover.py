"""NCover collectors."""

import re
import json
from abc import ABC
from datetime import datetime
from typing import Tuple

from bs4 import BeautifulSoup

from collector_utilities.functions import days_ago
from collector_utilities.type import Response, Responses, Value
from .source_collector import FileSourceCollector


class NCoverBase(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for NCover collectors."""

    file_extensions = ["html", "htm"]

    @staticmethod
    def _find_script(response: Response, text: str) -> str:
        """Return the script containing the text."""
        for script in BeautifulSoup(response.text, "html.parser").find_all("script", type="text/javascript"):
            if text in script.string:
                return str(script.string)
        return ""  # pragma: nocover


class NCoverCoverageBase(NCoverBase, ABC):  # pylint: disable=abstract-method
    """Base class for NCover coverage collectors."""

    coverage_type = "Subclass responsibility"

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        covered_items, total_items = self.__coverage(responses)
        return str(int(total_items) - int(covered_items))

    def _parse_source_responses_total(self, responses: Responses) -> Value:
        return self.__coverage(responses)[1]

    def __coverage(self, responses) -> Tuple[str, str]:
        """Return the coverage (covered items, total number) from the execution summary with the specified label."""
        covered, total = 0, 0
        for response in responses:
            script = self._find_script(response, "ncover.execution.stats = ")
            json_string = script.strip()[len('ncover.execution.stats = '):].strip(";")
            coverage = json.loads(json_string)[f"{self.coverage_type}Coverage"]
            covered += int(coverage["coveredPoints"])
            total += int(coverage["coveragePoints"])
        return str(covered), str(total)


class NCoverUncoveredLines(NCoverCoverageBase):
    """Collector to get the uncovered lines. Since NCover doesn't report lines, but sequence points, we use those.
    See http://www.ncover.com/blog/code-coverage-metrics-sequence-point-coverage/."""

    coverage_type = "sequencePoint"


class NCoverUncoveredBranches(NCoverCoverageBase):
    """Collector to get the uncovered branches."""

    coverage_type = "branch"


class NCoverSourceUpToDateness(NCoverBase):
    """Collector to collect the NCover report age."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(days_ago(min(self.__parse_date_time(response) for response in responses)))

    def __parse_date_time(self, response: Response) -> datetime:
        """Parse the date time from the NCover report."""
        script = self._find_script(response, "ncover.createDateTime")
        match = re.search(r"ncover\.createDateTime = '(\d+)'", script)
        timestamp = match.group(1) if match else ""
        return datetime.fromtimestamp(float(timestamp) / 1000)
