"""Jacoco coverage report collector."""

from abc import ABC
from datetime import datetime
from typing import Tuple

from defusedxml import ElementTree

from collector_utilities.type import Entities, Response, Responses, Value
from .source_collector import FileSourceCollector, SourceUpToDatenessCollector


class JacococBaseClass(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for Jacoco collectors."""

    file_extensions = ["xml"]


class JacocoCoverageBaseClass(JacococBaseClass):
    """Base class for Jacoco coverage collectors."""

    coverage_type = "Subclass responsibility (Jacoco has: line, branch, instruction, complexity, method, class)"

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        missed, covered = 0, 0
        for response in responses:
            tree = ElementTree.fromstring(response.text)
            counter = [c for c in tree.findall("counter") if c.get("type").lower() == self.coverage_type][0]
            missed += int(counter.get("missed"))
            covered += int(counter.get("covered"))
        return str(missed), str(missed + covered), []


class JacocoUncoveredLines(JacocoCoverageBaseClass):
    """Source class to get the number of uncovered lines from Jacoco XML reports."""

    coverage_type = "line"


class JacocoUncoveredBranches(JacocoCoverageBaseClass):
    """Source class to get the number of uncovered lines from Jacoco XML reports."""

    coverage_type = "branch"


class JacocoSourceUpToDateness(JacococBaseClass, SourceUpToDatenessCollector):
    """Collector to collect the Jacoco report age."""

    def _parse_source_response_date_time(self, response: Response) -> datetime:
        tree = ElementTree.fromstring(response.text)
        session_info = tree.find(".//sessioninfo")
        timestamp = session_info.get("dump") if session_info is not None else "0"
        return datetime.utcfromtimestamp(int(timestamp) / 1000.)
