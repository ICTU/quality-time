"""JUnit metric collector."""

import xml.etree.cElementTree
from typing import List

import requests

from ..collector import Collector
from ..type import Unit, Units, Value


class JUnit(Collector):
    """Base class for JUnit test collectors."""

    junit_test_report_counts = dict(errored="errors", failed="failures", passed="tests", skipped="skipped")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
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

    def test_statuses_to_count(self, **parameters) -> List[str]:
        return parameters.get("failure_type") or ["errored", "failed", "skipped"]

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        """Return a list of failed tests."""

        def unit(case_node, status: str) -> Unit:
            """Transform a test case into a test case unit."""
            name = case_node.get("name", "<nameless test case>")
            return dict(key=name, name=name, class_name=case_node.get("classname", ""), failure_type=status)

        tree = xml.etree.cElementTree.fromstring(response.text)
        units = []
        for status in self.test_statuses_to_count(**parameters):
            status_node = self.junit_status_nodes[status]
            units.extend([unit(case_node, status) for case_node in tree.findall(f".//{status_node}/..")])
        return units
