"""Robot Framework tests collector."""

from typing import cast

from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from collector_utilities.functions import parse_source_response_xml
from source_model import Entities, Entity, SourceMeasurement, SourceResponses

from .base import RobotFrameworkBaseClass


class RobotFrameworkTests(RobotFrameworkBaseClass):
    """Collector for Robot Framework tests."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the tests from the Robot Framework XML."""
        nr_of_tests, total_nr_of_tests, test_entities = 0, 0, Entities()
        test_results = cast(list[str], self._parameter("test_result"))
        all_test_results = self._data_model["sources"][self.source_type]["parameters"]["test_result"]["values"]
        for response in responses:
            tree = await parse_source_response_xml(response)
            count, total, entities = await self._parse_robot_framework_xml_v3(tree, test_results, all_test_results)
            nr_of_tests += count
            total_nr_of_tests += total
            test_entities.extend(entities)
        return SourceMeasurement(value=str(nr_of_tests), total=str(total_nr_of_tests), entities=test_entities)

    @staticmethod
    async def _parse_robot_framework_xml_v3(
        tree: Element, test_results: list[str], all_test_results: list[str]
    ) -> tuple[int, int, Entities]:
        """Parse a Robot Framework v3 XML."""
        nr_of_tests, total_nr_of_tests, entities = 0, 0, Entities()
        stats = tree.findall("statistics/total/stat")[1]
        for test_result in all_test_results:
            total_nr_of_tests += int(stats.get(test_result, 0))
            if test_result in test_results:
                nr_of_tests += int(stats.get(test_result, 0))
                for test in tree.findall(f".//test/status[@status='{test_result.upper()}']/.."):
                    entities.append(Entity(key=test.get("id", ""), name=test.get("name", ""), test_result=test_result))
        return nr_of_tests, total_nr_of_tests, entities
