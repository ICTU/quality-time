"""Robot Framework metric collector."""

from dateutil.parser import parse
import requests

from ..collector import Collector
from ..type import Units, URL, Value
from ..util import days_ago, parse_source_response_xml


class RobotFrameworkBaseClass(Collector):
    """Base class for Robot Framework collectors."""

    def landing_url(self, response: requests.Response, **parameters) -> URL:
        url = super().landing_url(response, **parameters)
        return URL(url.replace("output.html", "report.html"))


class RobotFrameworkTests(RobotFrameworkBaseClass):
    """Collector for Robot Framework tests."""

    stat_types = ["pass", "fail"]

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        tree = parse_source_response_xml(response)
        stats = tree.findall("statistics/total/stat")[1]
        return str(sum([int(stats.get(stat_type)) for stat_type in self.stat_types]))


class RobotFrameworkFailedTests(RobotFrameworkTests):
    """Collector to get the number of failed tests from Robot Framework XML reports."""

    stat_types = ["fail"]

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        """Return a list of failed tests."""
        tree = parse_source_response_xml(response)
        failed_tests = tree.findall(".//test/status[@status='FAIL']/..")
        return [dict(key=test.get("id"), name=test.get("name"), failure_type="fail") for test in failed_tests]


class RobotFrameworkSourceUpToDateness(RobotFrameworkBaseClass):
    """Collector to collect the Robot Framework report age."""

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        tree = parse_source_response_xml(response)
        report_datetime = parse(tree.get("generated"))
        return str(days_ago(report_datetime))
