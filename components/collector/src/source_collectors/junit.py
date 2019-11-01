"""JUnit metric collector."""

from abc import ABC
from datetime import datetime
from typing import cast, List

from dateutil.parser import parse

from collector_utilities.type import Entity, Entities, Response, Responses, Value
from collector_utilities.functions import days_ago, parse_source_response_xml
from .source_collector import FileSourceCollector


class JUnitBaseClass(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for JUnit collectors."""

    file_extensions = ["xml"]


class JUnitTests(JUnitBaseClass):
    """Collector for JUnit tests."""

    junit_status_nodes = dict(errored="error", failed="failure", skipped="skipped")

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(len(self._parse_source_responses_entities(responses)))

    def _test_statuses_to_count(self) -> List[str]:  # pylint: disable=no-self-use
        """Return the test statuses to count."""
        return cast(List[str], self._parameter("test_result"))

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        """Return a list of failed tests."""

        def entity(case_node, case_result: str) -> Entity:
            """Transform a test case into a test case entity."""
            name = case_node.get("name", "<nameless test case>")
            return dict(key=name, name=name, class_name=case_node.get("classname", ""), test_result=case_result)

        entities = []
        for response in responses:
            tree = parse_source_response_xml(response)
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

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        """Return a list of failed tests."""

        def entity(case_node, test_case_status: str) -> Entity:
            """Transform a test case into a test case entity."""
            name = case_node.get("name", "<nameless test case>")
            return dict(key=name, name=name, class_name=case_node.get("classname", ""), failure_type=test_case_status)

        entities = []
        for response in responses:
            tree = parse_source_response_xml(response)
            for status in self._test_statuses_to_count():
                status_node = self.junit_status_nodes[status]
                entities.extend([entity(case_node, status) for case_node in tree.findall(f".//{status_node}/..")])
        return entities


class JUnitSourceUpToDateness(JUnitBaseClass):
    """Collector to collect the Junit report age."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(days_ago(min(self.__parse_date_time(response) for response in responses)))

    @staticmethod
    def __parse_date_time(response: Response) -> datetime:
        """Parse the date time from the JUnit report."""
        tree = parse_source_response_xml(response)
        test_suite = tree if tree.tag == "testsuite" else tree.findall("testsuite")[0]
        return parse(test_suite.get("timestamp", ""))
