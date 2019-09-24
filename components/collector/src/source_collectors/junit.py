"""JUnit metric collector."""

from typing import cast, List

from dateutil.parser import parse
import requests

from utilities.type import Entity, Entities, Value
from utilities.functions import days_ago, parse_source_response_xml
from .source_collector import SourceCollector


class JUnitTests(SourceCollector):
    """Collector for JUnit tests."""

    junit_status_nodes = dict(errored="error", failed="failure", skipped="skipped")

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(len(self._parse_source_responses_entities(responses)))

    def _test_statuses_to_count(self) -> List[str]:  # pylint: disable=no-self-use
        """Return the test statuses to count."""
        return cast(List[str], self._parameter("test_result"))

    def _parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        """Return a list of failed tests."""

        def entity(case_node, case_result: str) -> Entity:
            """Transform a test case into a test case entity."""
            name = case_node.get("name", "<nameless test case>")
            return dict(key=name, name=name, class_name=case_node.get("classname", ""), test_result=case_result)

        tree = parse_source_response_xml(responses[0])
        entities = []
        for test_case in tree.findall(".//testcase"):
            for test_result, junit_status_node in self.junit_status_nodes.items():
                if test_case.find(junit_status_node) is not None:
                    break
            else:
                test_result = "passed"
            if test_result in self._test_statuses_to_count():
                entities.append(entity(test_case, test_result))
        return entities


class JUnitFailedTests(JUnitTests):
    """Collector to get the number of failed tests from JUnit XML reports."""

    def _test_statuses_to_count(self) -> List[str]:
        return cast(List[str], self._parameter("failure_type"))

    def _parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        """Return a list of failed tests."""

        def entity(case_node, test_case_status: str) -> Entity:
            """Transform a test case into a test case entity."""
            name = case_node.get("name", "<nameless test case>")
            return dict(key=name, name=name, class_name=case_node.get("classname", ""), failure_type=test_case_status)

        tree = parse_source_response_xml(responses[0])
        entities = []
        for status in self._test_statuses_to_count():
            status_node = self.junit_status_nodes[status]
            entities.extend([entity(case_node, status) for case_node in tree.findall(f".//{status_node}/..")])
        return entities


class JUnitSourceUpToDateness(SourceCollector):
    """Collector to collect the Junit report age."""

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        tree = parse_source_response_xml(responses[0])
        test_suite = tree if tree.tag == "testsuite" else tree.findall("testsuite")[0]
        report_datetime = parse(test_suite.get("timestamp", ""))
        return str(days_ago(report_datetime))
