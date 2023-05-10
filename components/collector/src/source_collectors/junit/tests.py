"""JUnit tests collector."""

from typing import cast

from xml.etree.ElementTree import Element  # nosec # Element is not available from defusedxml, but only used as type

from base_collectors import XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from model import Entities, Entity, SourceMeasurement, SourceResponses


class JUnitTests(XMLFileSourceCollector):
    """Collector for JUnit tests."""

    JUNIT_STATUS_NODES = {"errored": "error", "failed": "failure", "skipped": "skipped"}

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the tests from the JUnit XML."""
        entities = Entities()
        total = 0
        for response in responses:
            tree = await parse_source_response_xml(response)
            for test_case in tree.findall(".//testcase"):
                test_case_test_result = "passed"
                for test_result, junit_status_node in self.JUNIT_STATUS_NODES.items():
                    if test_case.find(junit_status_node) is not None:
                        test_case_test_result = test_result
                        break
                parsed_entity = self.__entity(test_case, test_case_test_result)
                if self._include_entity(parsed_entity):
                    entities.append(parsed_entity)
                total += 1
        return SourceMeasurement(entities=entities, total=str(total))

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include the entity in the measurement."""
        test_statuses_to_count = cast(list[str], self._parameter("test_result"))
        return entity["test_result"] in test_statuses_to_count

    @staticmethod
    def __entity(case_node: Element, case_result: str) -> Entity:
        """Transform a test case into a test case entity."""
        name = case_node.get("name", "<nameless test case>")
        return Entity(key=name, name=name, class_name=case_node.get("classname", ""), test_result=case_result)
