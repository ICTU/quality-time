"""JUnit metric collector."""

import xml.etree.cElementTree
from typing import cast, List

import requests

from collector.collector import Collector
from collector.type import Measurement, Unit, Units, Value


class JUnit(Collector):
    """Base class for JUnit test collectors."""

    junit_test_report_counts = dict(errored="errors", failed="failures", passed="tests", skipped="skipped")

    def parse_source_response(self, response: requests.Response, **parameters) -> Measurement:
        tree = xml.etree.cElementTree.fromstring(response.text)
        test_suites = [tree] if tree.tag == "testsuite" else tree.findall("testsuite")
        statuses = [self.junit_test_report_counts[status] for status in self.test_statuses_to_count(**parameters)]
        return str(sum(int(test_suite.get(status, 0)) for status in statuses for test_suite in test_suites))

    def test_statuses_to_count(self, **parameters) -> List[str]:
        """Return the test statuses to count."""
        raise NotImplementedError  # pragma: nocover


class JUnitTests(JUnit):
    """Collector to get the number of tests from JUnit XML reports."""

    def test_statuses_to_count(self, **parameters) -> List[str]:
        return ["passed"]


class JUnitFailedTests(JUnit):
    """Collector to get the number of failed tests from JUnit XML reports."""

    junit_status_nodes = dict(errored="error", failed="failure", skipped="skipped")

    def parse_source_response(self, response: requests.Response, **parameters) -> Measurement:
        failed_test_count = cast(Value, super().parse_source_response(response, **parameters))
        failed_tests = self.failed_tests(response, **parameters)
        return failed_test_count, failed_tests

    def test_statuses_to_count(self, **parameters) -> List[str]:
        return parameters.get("failure_type") or ["errored", "failed", "skipped"]

    def failed_tests(self, response: requests.Response, **parameters) -> Units:
        """Return a list of failed tests."""

        def unit(case_node) -> Unit:
            """Transform a test case into a test case unit."""
            name = case_node.get("name", "<nameless test case>")
            return dict(key=name, name=name, class_name=case_node.get("classname", ""))

        tree = xml.etree.cElementTree.fromstring(response.text)
        case_nodes = []
        for status in self.test_statuses_to_count(**parameters):
            status_node = self.junit_status_nodes[status]
            case_nodes.extend(tree.findall(f".//{status_node}/.."))
        return [unit(case_node) for case_node in case_nodes]
