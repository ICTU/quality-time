"""JUnit metric collector."""

from datetime import datetime
from typing import List, cast

from dateutil.parser import parse

from base_collectors import SourceUpToDatenessCollector, XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from collector_utilities.type import Response
from source_model import Entity, SourceMeasurement, SourceResponses


class JUnitTests(XMLFileSourceCollector):
    """Collector for JUnit tests."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        entities = []
        test_statuses_to_count = cast(List[str], self._parameter("test_result"))
        junit_status_nodes = dict(errored="error", failed="failure", skipped="skipped")
        total = 0
        for response in responses:
            tree = await parse_source_response_xml(response)
            for test_case in tree.findall(".//testcase"):
                for test_result, junit_status_node in junit_status_nodes.items():
                    if test_case.find(junit_status_node) is not None:
                        break
                else:
                    test_result = "passed"
                if test_result in test_statuses_to_count:
                    entities.append(self.__entity(test_case, test_result))
                total += 1
        return SourceMeasurement(entities=entities, total=str(total))

    @staticmethod
    def __entity(case_node, case_result: str) -> Entity:
        """Transform a test case into a test case entity."""
        name = case_node.get("name", "<nameless test case>")
        return Entity(key=name, name=name, class_name=case_node.get("classname", ""), test_result=case_result)


class JUnitSourceUpToDateness(XMLFileSourceCollector, SourceUpToDatenessCollector):
    """Collector to collect the Junit report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        tree = await parse_source_response_xml(response)
        test_suite = tree if tree.tag == "testsuite" else tree.findall("testsuite")[0]
        return parse(test_suite.get("timestamp", ""))
