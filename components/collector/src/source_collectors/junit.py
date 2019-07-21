"""JUnit metric collector."""

from typing import cast, List

from dateutil.parser import parse
import requests

from utilities.type import Entity, Entities, Value
from utilities.functions import days_ago, parse_source_response_xml
from .source_collector import SourceCollector


class JUnitTests(SourceCollector):
    """Collector for JUnit tests."""

    junit_test_report_counts = dict(errored="errors", failed="failures", passed="tests", skipped="skipped")

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        tree = parse_source_response_xml(responses[0])
        test_suites = [tree] if tree.tag == "testsuite" else tree.findall("testsuite")
        statuses = [self.junit_test_report_counts[status] for status in self.test_statuses_to_count()]
        return str(sum(int(test_suite.get(status, 0)) for status in statuses for test_suite in test_suites))

    def test_statuses_to_count(self) -> List[str]:  # pylint: disable=no-self-use
        """Return the test statuses to count."""
        return ["passed"]


class JUnitFailedTests(JUnitTests):
    """Collector to get the number of failed tests from JUnit XML reports."""

    junit_status_nodes = dict(errored="error", failed="failure", skipped="skipped")

    def test_statuses_to_count(self) -> List[str]:
        return cast(List[str], self.parameters.get("failure_type", [])) or ["errored", "failed", "skipped"]

    def parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        """Return a list of failed tests."""

        def entity(case_node, status: str) -> Entity:
            """Transform a test case into a test case entity."""
            name = case_node.get("name", "<nameless test case>")
            return dict(key=name, name=name, class_name=case_node.get("classname", ""), failure_type=status)

        tree = parse_source_response_xml(responses[0])
        entities = []
        for status in self.test_statuses_to_count():
            status_node = self.junit_status_nodes[status]
            entities.extend([entity(case_node, status) for case_node in tree.findall(f".//{status_node}/..")])
        return entities


class JunitSourceUpToDateness(SourceCollector):
    """Collector to collect the Junit report age."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        tree = parse_source_response_xml(responses[0])
        test_suite = tree if tree.tag == "testsuite" else tree.findall("testsuite")[0]
        report_datetime = parse(test_suite.get("timestamp"))
        return str(days_ago(report_datetime))
