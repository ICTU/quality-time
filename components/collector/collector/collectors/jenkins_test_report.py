"""Jenkins test report metric collector."""

import requests

from collector.collector import Collector
from collector.type import Measurement, Units, URL


class JenkinsTestReport(Collector):
    """Collector to get the amount of tests from a Jenkins test report."""
    test_statuses_to_count = ("subclassResponsibility",)

    def api_url(self, **parameters) -> URL:
        return URL(f"{parameters.get('url')}/lastSuccessfulBuild/testReport/api/json")

    def parse_source_response(self, response: requests.Response, **parameters) -> Measurement:
        json = response.json()
        return str(sum(int(json.get(status, 0)) for status in self.test_statuses_to_count))


class JenkinsTestReportTests(JenkinsTestReport):
    """Collector to get the amount of tests from a Jenkins test report."""

    test_statuses_to_count = ("passCount", "failCount", "skipCount")


class JenkinsTestReportFailedTests(JenkinsTestReport):
    """Collector to get the amount of tests from a Jenkins test report."""

    test_statuses_to_count = ("failCount",)

    def parse_source_response(self, response: requests.Response, **parameters) -> Measurement:
        failed_test_count = super().parse_source_response(response, **parameters)
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
