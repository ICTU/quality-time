"""TestNG tests collector."""

from typing import cast

from base_collectors import XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from model import SourceMeasurement, SourceResponses


class TestNGTests(XMLFileSourceCollector):
    """Collector for TestNG tests."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the tests for the TestNG XML."""
        test_statuses_to_count = cast(list[str], self._parameter("test_result"))
        test_count = 0
        total = 0
        for response in responses:
            tree = await parse_source_response_xml(response)
            for test_status in test_statuses_to_count:
                test_count += int(tree.get(test_status) or "0")
            total += int(tree.get("total") or "0")
        return SourceMeasurement(value=str(test_count), total=str(total))
