"""TestNG tests collector."""

from typing import cast
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from base_collectors import XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from model import Entities, Entity, SourceMeasurement, SourceResponses


class TestNGTests(XMLFileSourceCollector):
    """Collector for TestNG tests."""

    TEST_RESULT = dict(FAIL="failed", PASS="passed", SKIP="skipped")  # nosec, TestNG test status to test result mapping

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the tests for the TestNG XML."""
        test_results_to_count = [status.lower() for status in cast(list[str], self._parameter("test_result"))]
        test_count = 0
        total = 0
        entities = Entities()
        for response in responses:
            tree = await parse_source_response_xml(response)
            for test_result in test_results_to_count:
                test_count += int(tree.get(test_result) or "0")
            total += int(tree.get("total") or "0")
            entities.extend(self.__entities(tree, test_results_to_count))
        return SourceMeasurement(value=str(test_count), total=str(total), entities=entities)

    @classmethod
    def __entities(cls, tree: Element, test_results_to_count: list[str]) -> Entities:
        """Transform the test methods into entities."""
        entities = Entities()
        for test_class in tree.findall(".//class"):
            class_name = test_class.get("name", "")
            for test_method in test_class.findall(".//test-method"):
                test_result = cls.TEST_RESULT.get(test_method.get("status", ""))
                if test_result in test_results_to_count:
                    entities.append(cls.__entity(test_method, class_name, test_result))
        return entities

    @staticmethod
    def __entity(  # pylint: disable=unused-private-member
        test_method: Element, class_name: str, test_result: str
    ) -> Entity:
        """Transform a test method into an entity."""
        name = test_method.get("name")
        key = f"{class_name}_{name}"
        return Entity(key=key, name=name, class_name=class_name, test_result=test_result)
