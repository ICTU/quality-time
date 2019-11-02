"""Robot Framework metric collector."""

from abc import ABC
from datetime import datetime

from dateutil.parser import parse

from collector_utilities.type import Entities, Response, Responses, URL, Value
from collector_utilities.functions import parse_source_response_xml
from .source_collector import FileSourceCollector, SourceUpToDatenessCollector


class RobotFrameworkBaseClass(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for Robot Framework collectors."""

    file_extensions = ["xml"]

    def _landing_url(self, responses: Responses) -> URL:
        url = str(super()._landing_url(responses))
        return URL(url.replace("output.html", "report.html"))


class RobotFrameworkTests(RobotFrameworkBaseClass):
    """Collector for Robot Framework tests."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        count = 0
        for response in responses:
            tree = parse_source_response_xml(response)
            stats = tree.findall("statistics/total/stat")[1]
            count += sum([int(stats.get(stat_type, "0")) for stat_type in self._parameter("test_result")])
        return str(count)

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        """Return a list of failed tests."""
        tests = []
        test_results = self._parameter("test_result")
        for response in responses:
            tree = parse_source_response_xml(response)
            for test_result in test_results:
                tests.extend(
                    [(test_result, test)
                     for test in tree.findall(f".//test/status[@status='{test_result.upper()}']/..")])
        return [
            dict(key=test.get("id", ""), name=test.get("name", ""), test_result=test_result)
            for (test_result, test) in tests]


class RobotFrameworkFailedTests(RobotFrameworkBaseClass):
    """Collector to get the number of failed tests from Robot Framework XML reports."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        count = 0
        for response in responses:
            tree = parse_source_response_xml(response)
            stats = tree.findall("statistics/total/stat")[1]
            count += int(stats.get("fail", "0"))
        return str(count)

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        """Return a list of failed tests."""
        entities: Entities = []
        for response in responses:
            tree = parse_source_response_xml(response)
            failed_tests = tree.findall(".//test/status[@status='FAIL']/..")
            entities.extend(
                [dict(key=test.get("id", ""), name=test.get("name", ""), failure_type="fail") for test in failed_tests])
        return entities


class RobotFrameworkSourceUpToDateness(RobotFrameworkBaseClass, SourceUpToDatenessCollector):
    """Collector to collect the Robot Framework report age."""

    def _parse_source_response_date_time(self, response: Response) -> datetime:
        return parse(parse_source_response_xml(response).get("generated", ""))
