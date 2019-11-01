"""Jacoco coverage report collector."""

from datetime import datetime
from abc import ABC

from defusedxml import ElementTree

from collector_utilities.type import Response, Responses, Value
from collector_utilities.functions import days_ago
from .source_collector import FileSourceCollector


class JacococBaseClass(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for Jacoco collectors."""

    file_extensions = ["xml"]


class JacocoCoverageBaseClass(JacococBaseClass):
    """Base class for Jacoco coverage collectors."""

    coverage_type = "Subclass responsibility (Jacoco has: line, branch, instruction, complexity, method, class)"

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(self.__parse_source_responses(responses, "missed"))

    def _parse_source_responses_total(self, responses: Responses) -> Value:
        return str(sum(self.__parse_source_responses(responses, status) for status in ("missed", "covered")))

    def __parse_source_responses(self, responses: Responses, coverage_status: str) -> int:
        total = 0
        for response in responses:
            tree = ElementTree.fromstring(response.text)
            counter = [c for c in tree.findall("counter") if c.get("type").lower() == self.coverage_type][0]
            total += int(counter.get(coverage_status))
        return total


class JacocoUncoveredLines(JacocoCoverageBaseClass):
    """Source class to get the number of uncovered lines from Jacoco XML reports."""

    coverage_type = "line"


class JacocoUncoveredBranches(JacocoCoverageBaseClass):
    """Source class to get the number of uncovered lines from Jacoco XML reports."""

    coverage_type = "branch"


class JacocoSourceUpToDateness(JacococBaseClass):
    """Collector to collect the Jacoco report age."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(days_ago(min(self.__parse_date_time(response) for response in responses)))

    @staticmethod
    def __parse_date_time(response: Response) -> datetime:
        """Parse the date time from the Jacoco report."""
        tree = ElementTree.fromstring(response.text)
        session_info = tree.find(".//sessioninfo")
        timestamp = session_info.get("dump") if session_info is not None else "0"
        return datetime.utcfromtimestamp(int(timestamp) / 1000.)
