"""JUnit tests collector."""

from typing import cast

from base_collectors import XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from source_model import Entities, Entity, SourceMeasurement, SourceResponses


class JUnitTests(XMLFileSourceCollector):
    """Collector for JUnit tests."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the tests from the JUnit XML."""
        entities = Entities()
        test_statuses_to_count = cast(list[str], self._parameter("test_result"))
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
