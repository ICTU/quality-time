"""Robot Framework tests collector."""

from typing import List, cast

from collector_utilities.functions import parse_source_response_xml
from source_model import Entity, SourceMeasurement, SourceResponses

from .base import RobotFrameworkBaseClass


class RobotFrameworkTests(RobotFrameworkBaseClass):
    """Collector for Robot Framework tests."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the tests from the Robot Framework XML."""
        count = 0
        total = 0
        entities = []
        test_results = cast(List[str], self._parameter("test_result"))
        all_test_results = self._data_model["sources"][self.source_type]["parameters"]["test_result"]["values"]
        for response in responses:
            tree = await parse_source_response_xml(response)
            stats = tree.findall("statistics/total/stat")[1]
            for test_result in all_test_results:
                total += int(stats.get(test_result, 0))
                if test_result in test_results:
                    count += int(stats.get(test_result, 0))
                    for test in tree.findall(f".//test/status[@status='{test_result.upper()}']/.."):
                        entities.append(
                            Entity(key=test.get("id", ""), name=test.get("name", ""), test_result=test_result)
                        )
        return SourceMeasurement(value=str(count), total=str(total), entities=entities)
