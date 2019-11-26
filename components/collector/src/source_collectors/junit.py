"""JUnit metric collector."""

from abc import ABC
from datetime import datetime
from typing import cast, List, Tuple

from dateutil.parser import parse

from collector_utilities.type import Entity, Entities, Response, Responses, Value
from collector_utilities.functions import parse_source_response_xml
from .source_collector import FileSourceCollector, SourceUpToDatenessCollector


class JUnitBaseClass(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for JUnit collectors."""

    file_extensions = ["xml"]
    junit_status_nodes = dict(errored="error", failed="failure", skipped="skipped")


class JUnitTests(JUnitBaseClass):
    """Collector for JUnit tests."""

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        entities = []
        for response in responses:
            tree = parse_source_response_xml(response)
            for test_case in tree.findall(".//testcase"):
                for test_result, junit_status_node in self.junit_status_nodes.items():
                    if test_case.find(junit_status_node) is not None:
                        break
                else:
                    test_result = "passed"
                if test_result in self.__test_statuses_to_count():
                    entities.append(self.__entity(test_case, test_result))
        return str(len(entities)), "100", entities

    def __test_statuses_to_count(self) -> List[str]:  # pylint: disable=no-self-use
        """Return the test statuses to count."""
        return cast(List[str], self._parameter("test_result"))

    @staticmethod
    def __entity(case_node, case_result: str) -> Entity:
        """Transform a test case into a test case entity."""
        name = case_node.get("name", "<nameless test case>")
        return dict(key=name, name=name, class_name=case_node.get("classname", ""), test_result=case_result)


class JUnitFailedTests(JUnitBaseClass):
    """Collector to get the number of failed tests from JUnit XML reports."""

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        entities = []
        for response in responses:
            tree = parse_source_response_xml(response)
            for status in self.__test_statuses_to_count():
                status_node = self.junit_status_nodes[status]
                entities.extend(
                    [self.__entity(case_node, status) for case_node in tree.findall(f".//{status_node}/..")])
        return str(len(entities)), "100", entities

    def __test_statuses_to_count(self) -> List[str]:
        return cast(List[str], self._parameter("failure_type"))

    @staticmethod
    def __entity(case_node, test_case_status: str) -> Entity:
        """Transform a test case into a test case entity."""
        name = case_node.get("name", "<nameless test case>")
        return dict(key=name, name=name, class_name=case_node.get("classname", ""), failure_type=test_case_status)


class JUnitSourceUpToDateness(JUnitBaseClass, SourceUpToDatenessCollector):
    """Collector to collect the Junit report age."""

    def _parse_source_response_date_time(self, response: Response) -> datetime:
        tree = parse_source_response_xml(response)
        test_suite = tree if tree.tag == "testsuite" else tree.findall("testsuite")[0]
        return parse(test_suite.get("timestamp", ""))
