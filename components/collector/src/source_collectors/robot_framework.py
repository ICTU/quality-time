"""Robot Framework metric collector."""

from abc import ABC
from datetime import datetime
from typing import cast, List, Tuple

from dateutil.parser import parse

from collector_utilities.type import Entities, Response, Responses, URL, Value
from collector_utilities.functions import parse_source_response_xml
from .source_collector import XMLFileSourceCollector, SourceUpToDatenessCollector


class RobotFrameworkBaseClass(XMLFileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for Robot Framework collectors."""

    def _landing_url(self, responses: Responses) -> URL:
        url = str(super()._landing_url(responses))
        return URL(url.replace("output.html", "report.html"))


class RobotFrameworkTests(RobotFrameworkBaseClass):
    """Collector for Robot Framework tests."""

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        count = 0
        entities: Entities = []
        test_results = cast(List[str], self._parameter("test_result"))
        for response in responses:
            tree = parse_source_response_xml(response)
            stats = tree.findall("statistics/total/stat")[1]
            for test_result in test_results:
                count += int(stats.get(test_result, 0))
                for test in tree.findall(f".//test/status[@status='{test_result.upper()}']/.."):
                    entities.append(dict(key=test.get("id", ""), name=test.get("name", ""), test_result=test_result))
        return str(count), "100", entities


class RobotFrameworkSourceUpToDateness(RobotFrameworkBaseClass, SourceUpToDatenessCollector):
    """Collector to collect the Robot Framework report age."""

    def _parse_source_response_date_time(self, response: Response) -> datetime:
        return parse(parse_source_response_xml(response).get("generated", ""))
