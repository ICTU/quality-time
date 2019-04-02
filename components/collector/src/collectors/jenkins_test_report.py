"""Jenkins test report metric collector."""

from datetime import datetime
from typing import List

from dateutil.parser import parse
import requests

from ..collector import Collector
from ..type import Unit, Units, URL, Value


class JenkinsTestReportTests(Collector):
    """Collector to get the amount of tests from a Jenkins test report."""

    jenkins_test_report_counts = dict(failed="failCount", passed="passCount", skipped="skipCount")

    def api_url(self, **parameters) -> URL:
        return URL(f"{super().api_url(**parameters)}/lastSuccessfulBuild/testReport/api/json")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        json = response.json()
        statuses = [self.jenkins_test_report_counts[status] for status in self.test_statuses_to_count(**parameters)]
        return str(sum(int(json.get(status, 0)) for status in statuses))

    @staticmethod
    def test_statuses_to_count(**parameters) -> List[str]:  # pylint: disable=unused-argument
        """Return the test statuses to count."""
        return ["failed", "passed", "skipped"]


class JenkinsTestReportFailedTests(JenkinsTestReportTests):
    """Collector to get the amount of tests from a Jenkins test report."""

    @staticmethod
    def test_statuses_to_count(**parameters) -> List[str]:
        return parameters.get("failure_type") or ["failed", "skipped"]

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        """Return a list of failed tests."""

        def unit(case) -> Unit:
            """Transform a test case into a test case unit."""
            name = case.get("name", "<nameless test case>")
            return dict(key=name, name=name, class_name=case.get("className", ""), failure_type=status(case))

        def status(case) -> str:
            """Return the status of the test case."""
            # The Jenkins test report has three counts: passed, skipped, and failed. Individual test cases
            # can be skipped (indicated by the attribute skipped being "true") and/or have a status that can
            # take the values: "failed", "passed", "regression", and "fixed".
            status = "skipped" if case.get("skipped") == "true" else case.get("status", "").lower()
            return dict(regression="failed", fixed="passed").get(status, status)

        suites = response.json().get("suites", [])
        statuses = self.test_statuses_to_count(**parameters)
        return [unit(case) for suite in suites for case in suite.get("cases", []) if status(case) in statuses]


class JenkinsTestReportSourceFreshness(Collector):
    """Collector to get the age of the Jenkins test report."""

    def api_url(self, **parameters) -> URL:
        return URL(f"{super().api_url(**parameters)}/lastSuccessfulBuild/testReport/api/json")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        report_datetime = parse(response.json()["suites"][0]["timestamp"])
        return str((datetime.now() - report_datetime).days)
