"""TestNG metric collector."""

from datetime import datetime
from typing import List, cast

from dateutil.parser import parse

from base_collectors import SourceUpToDatenessCollector, XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from collector_utilities.type import Response
from source_model import SourceMeasurement, SourceResponses


class TestNGTests(XMLFileSourceCollector):
    """Collector for TestNG tests."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        test_statuses_to_count = cast(List[str], self._parameter("test_result"))
        test_count = 0
        total = 0
        for response in responses:
            tree = await parse_source_response_xml(response)
            for test_status in test_statuses_to_count:
                test_count += int(tree.get(test_status) or "0")
            total += int(tree.get("total") or "0")
        return SourceMeasurement(value=str(test_count), total=str(total))


class TestNGSourceUpToDateness(XMLFileSourceCollector, SourceUpToDatenessCollector):
    """Collector to collect the TestNG report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        tree = await parse_source_response_xml(response)
        test_suite = tree.findall("suite")[0]
        return parse(test_suite.get("finished-at") or "")
