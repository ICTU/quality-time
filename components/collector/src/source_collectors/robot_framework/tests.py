"""Robot Framework tests collector."""

from typing import cast

from shared.utils.functions import first
from shared_data_model import DATA_MODEL

from collector_utilities.functions import parse_source_response_xml
from collector_utilities.type import Response
from model import Entities, Entity, SourceMeasurement, SourceResponses

from .base import RobotFrameworkBaseClass


class RobotFrameworkTests(RobotFrameworkBaseClass):
    """Collector for Robot Framework tests."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the tests from the Robot Framework XML."""
        nr_of_tests, total_nr_of_tests, test_entities = 0, 0, Entities()
        test_results = cast(list[str], self._parameter("test_result"))
        all_test_results = DATA_MODEL.sources[self.source_type].parameters["test_result"].values or []
        for response in responses:
            count, total, entities = await self._parse_source_response(response, test_results, all_test_results)
            nr_of_tests += count
            total_nr_of_tests += total
            test_entities.extend(entities)
        return SourceMeasurement(value=str(nr_of_tests), total=str(total_nr_of_tests), entities=test_entities)

    @classmethod
    async def _parse_source_response(
        cls,
        response: Response,
        test_results: list[str],
        all_test_results: list[str],
    ) -> tuple[int, int, Entities]:
        """Parse a Robot Framework XML."""
        nr_of_tests, total_nr_of_tests, entities = 0, 0, Entities()
        tree = await parse_source_response_xml(response)
        stats = first(tree.findall("statistics/total/stat"), lambda stat: (stat.text or "").lower() == "all tests")
        parent_map = cls.parent_map(tree)
        for test_result in all_test_results:
            total_nr_of_tests += int(stats.get(test_result, 0))
            if test_result not in test_results:
                continue
            nr_of_tests += int(stats.get(test_result, 0))
            for suite in tree.findall(".//suite[test]"):
                suite_name = suite.get("name", "unknown")
                for test in suite.findall(f"test/status[@status='{test_result.upper()}']/.."):
                    test_id = test.get("id", "")
                    test_name = test.get("name", "unknown")
                    suite_names = cls.parent_names(test, parent_map)
                    entity = Entity(
                        key=test_id,
                        test_name=test_name,
                        suite_name=suite_name,
                        suite_names=suite_names,
                        test_result=test_result,
                    )
                    entities.append(entity)
        return nr_of_tests, total_nr_of_tests, entities
