"""Robot Framework metric collector."""

from typing import List

from dateutil.parser import parse
import requests

from utilities.type import Entities, URL, Value
from utilities.functions import days_ago, parse_source_response_xml
from .source_collector import SourceCollector


class RobotFrameworkBaseClass(SourceCollector):
    """Base class for Robot Framework collectors."""

    def _landing_url(self, responses: List[requests.Response]) -> URL:
        url = str(super()._landing_url(responses))
        return URL(url.replace("output.html", "report.html"))


class RobotFrameworkTests(RobotFrameworkBaseClass):
    """Collector for Robot Framework tests."""

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        tree = parse_source_response_xml(responses[0])
        stats = tree.findall("statistics/total/stat")[1]
        return str(sum([int(stats.get(stat_type, "0")) for stat_type in self._parameter("test_result")]))

    def _parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        """Return a list of failed tests."""
        tree = parse_source_response_xml(responses[0])
        tests = []
        for test_result in self._parameter("test_result"):
            tests.extend(
                [(test_result, test) for test in tree.findall(f".//test/status[@status='{test_result.upper()}']/..")])
        return [
            dict(key=test.get("id", ""), name=test.get("name", ""), test_result=test_result)
            for (test_result, test) in tests]


class RobotFrameworkFailedTests(RobotFrameworkBaseClass):
    """Collector to get the number of failed tests from Robot Framework XML reports."""

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        tree = parse_source_response_xml(responses[0])
        stats = tree.findall("statistics/total/stat")[1]
        return str(int(stats.get("fail", "0")))

    def _parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        """Return a list of failed tests."""
        tree = parse_source_response_xml(responses[0])
        failed_tests = tree.findall(".//test/status[@status='FAIL']/..")
        return [dict(key=test.get("id", ""), name=test.get("name", ""), failure_type="fail") for test in failed_tests]


class RobotFrameworkSourceUpToDateness(RobotFrameworkBaseClass):
    """Collector to collect the Robot Framework report age."""

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        tree = parse_source_response_xml(responses[0])
        report_datetime = parse(tree.get("generated", ""))
        return str(days_ago(report_datetime))
