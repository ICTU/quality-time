"""Visual Studio TRX tests collector."""

import re
from typing import cast
from xml.etree.ElementTree import Element  # nosec # Element is not available from defusedxml, but only used as type

from base_collectors import XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml_with_namespace
from collector_utilities.type import ElementMap, Namespaces
from metric_collectors.test_cases import TestCases
from model import Entities, Entity, SourceMeasurement, SourceResponses


class VisualStudioTRXTests(XMLFileSourceCollector):
    """Collector for Visual Studio TRX tests."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the tests from the Visual Studio TRX report."""
        entities = Entities()
        test_results = {}
        total = 0
        for response in responses:
            tree, namespaces = await parse_source_response_xml_with_namespace(response)
            parent_map = self.parent_map(tree)
            for result in tree.findall(".//ns:UnitTestResult", namespaces):
                test_results[result.attrib["testId"]] = result.attrib["outcome"]
            for test in tree.findall(".//ns:UnitTest", namespaces):
                parsed_entity = self.__entity(test, test_results[test.attrib["id"]], namespaces, parent_map)
                if self._include_entity(parsed_entity):
                    entities.append(parsed_entity)
                total += 1
        return SourceMeasurement(entities=entities, total=str(total))

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include the entity in the measurement."""
        test_results_to_count = cast(list[str], self._parameter("test_result"))
        return entity["test_result"] in test_results_to_count

    @classmethod
    def __entity(cls, test: Element, result: str, namespaces: Namespaces, parent_map: ElementMap) -> Entity:
        """Transform a test case into a test entity."""
        name = test.attrib["name"]
        category_items = test.findall(".//ns:TestCategoryItem", namespaces)
        categories = [item.attrib["TestCategory"] for item in category_items]
        matches = [match[0] for category in categories if (match := re.search(TestCases.TEST_CASE_KEY_RE, category))]
        if matches:
            name += f" ({', '.join(sorted(matches))})"
        key = test.attrib["id"]
        suite_names = cls.parent_names(test, parent_map)
        return Entity(key=key, name=name, test_result=result, suite_names=suite_names)
