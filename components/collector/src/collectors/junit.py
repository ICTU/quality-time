"""JUnit metric collector."""

from typing import List

from dateutil.parser import parse
import requests

from ..collector import Collector
from ..type import Unit, Units, Value
from ..util import days_ago, parse_source_response_xml


class JUnitTests(Collector):
    """Collector for JUnit tests."""

    junit_test_report_counts = dict(errored="errors", failed="failures", passed="tests", skipped="skipped")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        tree = parse_source_response_xml(response)
        test_suites = [tree] if tree.tag == "testsuite" else tree.findall("testsuite")
        statuses = [self.junit_test_report_counts[status] for status in self.test_statuses_to_count(**parameters)]
        return str(sum(int(test_suite.get(status, 0)) for status in statuses for test_suite in test_suites))

    def test_statuses_to_count(self, **parameters) -> List[str]:  # pylint: disable=no-self-use,unused-argument
        """Return the test statuses to count."""
        return ["passed"]


class JUnitFailedTests(JUnitTests):
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

        tree = parse_source_response_xml(response)
        units = []
        for status in self.test_statuses_to_count(**parameters):
            status_node = self.junit_status_nodes[status]
            units.extend([unit(case_node, status) for case_node in tree.findall(f".//{status_node}/..")])
        return units


class JunitSourceUpToDateness(Collector):
    """Collector to collect the Junit report age."""

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        tree = parse_source_response_xml(response)
        test_suite = tree if tree.tag == "testsuite" else tree.findall("testsuite")[0]
        report_datetime = parse(test_suite.get("timestamp"))
        return str(days_ago(report_datetime))
