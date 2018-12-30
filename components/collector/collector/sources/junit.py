"""JUnit metric source."""

import xml.etree.cElementTree

import requests

from collector.source import Source
from collector.type import Measurement


class JUnit(Source):
    """Base class for JUnit test metrics."""

    name = "JUnit"
    test_status = "Subclass responsibility"

    def parse_source_response(self, response: requests.Response) -> Measurement:
        tree = xml.etree.cElementTree.fromstring(response.text)
        test_suites = [tree] if tree.tag == "testsuite" else tree.findall("testsuite")
        return Measurement(sum(int(test_suite.get(self.test_status, 0)) for test_suite in test_suites))


class JUnitTests(JUnit):
    """Source class to get the number of tests from JUnit XML reports."""

    test_status = "tests"


class JUnitFailedTests(JUnit):
    """Source class to get the number of failed tests from JUnit XML reports."""

    test_status = "failures"
