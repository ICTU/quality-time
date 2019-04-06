"""Jacoco coverage report collector."""

from datetime import datetime
import xml.etree.cElementTree

import requests

from ..collector import Collector
from ..type import Value


class JacocoCoverageBaseClass(Collector):
    """Base class for Jacoco coverage collectors."""

    coverage_status = "Subclass responsibility (Jacoco has: covered or missed)"
    coverage_type = "Subclass responsibility (Jacoco has: line, branch, instruction, complexity, method, class)"

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        tree = xml.etree.cElementTree.fromstring(response.text)
        counter = [c for c in tree.findall("counter") if c.get("type").lower() == self.coverage_type][0]
        return str(counter.get(self.coverage_status))


class JacocoUncoveredLines(JacocoCoverageBaseClass):
    """Source class to get the number of uncovered lines from Jacoco XML reports."""

    coverage_status = "missed"
    coverage_type = "line"


class JacocoUncoveredBranches(JacocoCoverageBaseClass):
    """Source class to get the number of uncovered lines from Jacoco XML reports."""

    coverage_status = "missed"
    coverage_type = "branch"


class JacocoSourceUpToDateness(Collector):
    """Collector to collect the Jacoco report age."""

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        tree = xml.etree.cElementTree.fromstring(response.text)
        session_info = tree.find(".//sessioninfo")
        timestamp = session_info.get("dump") if session_info is not None else "0"
        report_datetime = datetime.utcfromtimestamp(int(timestamp) / 1000.)
        return str((datetime.utcnow() - report_datetime).days)
