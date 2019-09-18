"""Jacoco coverage report collector."""

from datetime import datetime
from typing import List

from defusedxml import ElementTree
import requests

from utilities.type import Value
from utilities.functions import days_ago
from .source_collector import SourceCollector


class JacocoCoverageBaseClass(SourceCollector):
    """Base class for Jacoco coverage collectors."""

    coverage_type = "Subclass responsibility (Jacoco has: line, branch, instruction, complexity, method, class)"

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(self.__parse_source_responses(responses, "missed"))

    def _parse_source_responses_total(self, responses: List[requests.Response]) -> Value:
        return str(sum(self.__parse_source_responses(responses, status) for status in ("missed", "covered")))

    def __parse_source_responses(self, responses: List[requests.Response], coverage_status: str) -> int:
        tree = ElementTree.fromstring(responses[0].text)
        counter = [c for c in tree.findall("counter") if c.get("type").lower() == self.coverage_type][0]
        return int(counter.get(coverage_status))


class JacocoUncoveredLines(JacocoCoverageBaseClass):
    """Source class to get the number of uncovered lines from Jacoco XML reports."""

    coverage_type = "line"


class JacocoUncoveredBranches(JacocoCoverageBaseClass):
    """Source class to get the number of uncovered lines from Jacoco XML reports."""

    coverage_type = "branch"


class JacocoSourceUpToDateness(SourceCollector):
    """Collector to collect the Jacoco report age."""

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        tree = ElementTree.fromstring(responses[0].text)
        session_info = tree.find(".//sessioninfo")
        timestamp = session_info.get("dump") if session_info is not None else "0"
        report_datetime = datetime.utcfromtimestamp(int(timestamp) / 1000.)
        return str(days_ago(report_datetime))
