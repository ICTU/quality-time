"""NCover collectors."""

import re
import json
from abc import ABC
from datetime import datetime
from typing import Tuple

from bs4 import BeautifulSoup

from collector_utilities.functions import days_ago
from collector_utilities.type import Responses, Value
from .source_collector import SourceCollector


class NCoverBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for NCover collectors."""

    @staticmethod
    def _find_script(responses: Responses, text: str) -> str:
        """Return the script containing the text."""
        for script in BeautifulSoup(responses[0].text, "html.parser").find_all("script", type="text/javascript"):
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
        script = self._find_script(responses, "ncover.execution.stats = ")
        json_string = script.strip()[len('ncover.execution.stats = '):].strip(";")
        coverage = json.loads(json_string)[f"{self.coverage_type}Coverage"]
        return str(coverage["coveredPoints"]), str(coverage["coveragePoints"])


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
        script = self._find_script(responses, "ncover.createDateTime")
        match = re.search(r"ncover\.createDateTime = '(\d+)'", script)
        timestamp = match.group(1) if match else ""
        return str(days_ago(datetime.fromtimestamp(float(timestamp) / 1000)))
