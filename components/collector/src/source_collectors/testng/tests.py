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
                if test_method.get("is-config", "false") == "true" or test_result not in test_results_to_count:
                    continue  # Skip config (beforeClass/afterClass) methods and test results the user wants to ignore
                name = test_method.get("name", "")
                description = test_method.get("description", "")
                key = f"{class_name}_{name}"
                entities.append(
                    Entity(key=key, name=name, description=description, class_name=class_name, test_result=test_result)
                )
        return entities
