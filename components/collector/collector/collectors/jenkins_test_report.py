"""Jenkins test report metric collector."""

from typing import cast, List

import requests

from collector.collector import Collector
from collector.type import Measurement, Units, URL, Value


class JenkinsTestReport(Collector):
    """Collector to get the amount of tests from a Jenkins test report."""

    jenkins_test_report_counts = dict(failed="failCount", passed="passCount", skipped="skipCount")

    def api_url(self, **parameters) -> URL:
        return URL(f"{parameters.get('url')}/lastSuccessfulBuild/testReport/api/json")

    def parse_source_response(self, response: requests.Response, **parameters) -> Measurement:
        json = response.json()
        statuses = [self.jenkins_test_report_counts[status] for status in self.test_statuses_to_count(**parameters)]
        return str(sum(int(json.get(status, 0)) for status in statuses))

    def test_statuses_to_count(self, **parameters) -> List[str]:
        """Return the test statuses to count."""
        raise NotImplementedError  # pragma: nocover


class JenkinsTestReportTests(JenkinsTestReport):
    """Collector to get the amount of tests from a Jenkins test report."""

    def test_statuses_to_count(self, **parameters) -> List[str]:
        return ["passed", "failed", "skipped"]


class JenkinsTestReportFailedTests(JenkinsTestReport):
    """Collector to get the amount of tests from a Jenkins test report."""

    def parse_source_response(self, response: requests.Response, **parameters) -> Measurement:
        failed_test_count = cast(Value, super().parse_source_response(response, **parameters))
        failed_tests = self.failed_tests(response)
        return failed_test_count, failed_tests

    @staticmethod
    def failed_tests(response: requests.Response) -> Units:
        """Return a list of failed tests."""

        def unit(case):
            """Transform a test case into a test case unit."""
            name = case.get("name", "<nameless test case>")
            return dict(key=name, name=name, class_name=case.get("className", ""))

        suites = response.json().get("suites", [])
        return [unit(case) for suite in suites for case in suite.get("cases", []) if case.get("status") == "FAILED"]

    def test_statuses_to_count(self, **parameters) -> List[str]:
        return parameters.get("failure_type") or ["failed", "skipped"]
