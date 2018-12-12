"""Jacoco coverage report metric source."""

import xml.etree.cElementTree

import requests

from quality_time.source import Source
from quality_time.type import Measurement


class JacocoCoverageBaseClass(Source):
    """Base class for Jacoco coverage metrics."""

    coverage_status = "Subclass responsibility (Jacoco has: covered or missed)"
    coverage_type = "Subclass responsibility (Jacoco has: line, branch, instruction, complexity, method, class)"

    def parse_source_response(self, response: requests.Response) -> Measurement:
        tree = xml.etree.cElementTree.fromstring(response.text)
        counter = [c for c in tree.findall("counter") if c.get("type").lower() == self.coverage_type][0]
        return Measurement(counter.get(self.coverage_status))


class JacocoCoveredLines(JacocoCoverageBaseClass):
    """Source class to get the number of covered lines from Jacoco XML reports."""

    coverage_status = "covered"
    coverage_type = "line"


class JacocoUncoveredLines(JacocoCoverageBaseClass):
    """Source class to get the number of uncovered lines from Jacoco XML reports."""

    coverage_status = "missed"
    coverage_type = "line"


class JacocoCoveredBranches(JacocoCoverageBaseClass):
    """Source class to get the number of covered lines from Jacoco XML reports."""

    coverage_status = "covered"
    coverage_type = "branch"


class JacocoUncoveredBranches(JacocoCoverageBaseClass):
    """Source class to get the number of uncovered lines from Jacoco XML reports."""

    coverage_status = "missed"
    coverage_type = "branch"
