"""JUnit metric collector."""

import xml.etree.cElementTree
from typing import cast

import requests

from collector.collector import Collector
from collector.type import Measurement, Unit, Units, Value


class JUnit(Collector):
    """Base class for JUnit test collectors."""

    test_status = "Subclass responsibility"

    def parse_source_response(self, response: requests.Response, **parameters) -> Measurement:
        tree = xml.etree.cElementTree.fromstring(response.text)
        test_suites = [tree] if tree.tag == "testsuite" else tree.findall("testsuite")
        return str(sum(int(test_suite.get(self.test_status, 0)) for test_suite in test_suites))


class JUnitTests(JUnit):
    """Collector to get the number of tests from JUnit XML reports."""

    test_status = "tests"


class JUnitFailedTests(JUnit):
    """Collector to get the number of failed tests from JUnit XML reports."""

    test_status = "failures"

    def parse_source_response(self, response: requests.Response, **parameters) -> Measurement:
        failed_test_count = cast(Value, super().parse_source_response(response, **parameters))
        failed_tests = self.failed_tests(response)
        return failed_test_count, failed_tests

    @staticmethod
    def failed_tests(response: requests.Response) -> Units:
        """Return a list of failed tests."""

        def unit(case_node) -> Unit:
            """Transform a test case into a test case unit."""
            name = case_node.get("name", "<nameless test case>")
            return dict(key=name, name=name, class_name=case_node.get("classname", ""))

        tree = xml.etree.cElementTree.fromstring(response.text)
        return [unit(case_node) for case_node in tree.findall(".//failure/..")]
