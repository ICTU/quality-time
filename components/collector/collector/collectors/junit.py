"""JUnit metric collector."""

import xml.etree.cElementTree

import requests

from collector.collector import Collector
from collector.type import Measurement


class JUnit(Collector):
    """Base class for JUnit test collectors."""

    test_status = "Subclass responsibility"

    def parse_source_response(self, response: requests.Response) -> Measurement:
        tree = xml.etree.cElementTree.fromstring(response.text)
        test_suites = [tree] if tree.tag == "testsuite" else tree.findall("testsuite")
        return Measurement(sum(int(test_suite.get(self.test_status, 0)) for test_suite in test_suites))


class JUnitTests(JUnit):
    """Collector to get the number of tests from JUnit XML reports."""

    test_status = "tests"


class JUnitFailedTests(JUnit):
    """Collector to get the number of failed tests from JUnit XML reports."""

    test_status = "failures"
