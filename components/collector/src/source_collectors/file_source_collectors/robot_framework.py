"""Robot Framework metric collector."""

from abc import ABC
from datetime import datetime
from typing import List, cast

from dateutil.parser import parse

from base_collectors import SourceUpToDatenessCollector, XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from collector_utilities.type import URL, Response
from source_model import Entity, SourceMeasurement, SourceResponses


class RobotFrameworkBaseClass(XMLFileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for Robot Framework collectors."""

    async def _landing_url(self, responses: SourceResponses) -> URL:
        url = str(await super()._landing_url(responses))
        return URL(url.replace("output.html", "report.html"))


class RobotFrameworkTests(RobotFrameworkBaseClass):
    """Collector for Robot Framework tests."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
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
                            Entity(key=test.get("id", ""), name=test.get("name", ""), test_result=test_result))
        return SourceMeasurement(value=str(count), total=str(total), entities=entities)


class RobotFrameworkSourceUpToDateness(RobotFrameworkBaseClass, SourceUpToDatenessCollector):
    """Collector to collect the Robot Framework report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        return parse((await parse_source_response_xml(response)).get("generated", ""))
