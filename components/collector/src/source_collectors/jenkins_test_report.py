"""Jenkins test report metric collector."""

from datetime import datetime
from typing import cast, List, Tuple

from dateutil.parser import parse
import requests

from collector_utilities.type import Entity, Entities, Responses, URL, Value
from collector_utilities.functions import days_ago
from .source_collector import SourceCollector


class JenkinsTestReportTests(SourceCollector):
    """Collector to get the amount of tests from a Jenkins test report."""

    jenkins_test_report_counts = dict(failed="failCount", passed="passCount", skipped="skipCount")

    def _api_url(self) -> URL:
        return URL(f"{super()._api_url()}/lastSuccessfulBuild/testReport/api/json")

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        json = responses[0].json()
        suites = json.get("suites", [])
        statuses = cast(List[str], self._parameter("test_result"))
        status_counts = [self.jenkins_test_report_counts[status] for status in statuses]
        value = str(sum(int(json.get(status_count, 0)) for status_count in status_counts))
        entities = [
            self.__entity(case) for suite in suites for case in suite.get("cases", [])
            if self.__status(case) in statuses]
        return value, "100", entities

    def __entity(self, case) -> Entity:
        """Transform a test case into a test case entity."""
        name = case.get("name", "<nameless test case>")
        return dict(key=name, name=name, class_name=case.get("className", ""), test_result=self.__status(case))

    @staticmethod
    def __status(case) -> str:
        """Return the status of the test case."""
        # The Jenkins test report has three counts: passed, skipped, and failed. Individual test cases
        # can be skipped (indicated by the attribute skipped being "true") and/or have a status that can
        # take the values: "failed", "passed", "regression", and "fixed".
        test_case_status = "skipped" if case.get("skipped") == "true" else case.get("status", "").lower()
        return dict(regression="failed", fixed="passed").get(test_case_status, test_case_status)


class JenkinsTestReportSourceUpToDateness(SourceCollector):
    """Collector to get the age of the Jenkins test report."""

    def _get_source_responses(self, api_url: URL) -> Responses:
        api_url = self._api_url()
        test_report_url = URL(f"{api_url}/lastSuccessfulBuild/testReport/api/json")
        job_url = URL(f"{api_url}/lastSuccessfulBuild/api/json")
        return [requests.get(url, timeout=self.TIMEOUT, auth=self._basic_auth_credentials())
                for url in (test_report_url, job_url)]

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        timestamps = [suite.get("timestamp") for suite in responses[0].json().get("suites", [])
                      if suite.get("timestamp")]
        report_datetime = parse(max(timestamps)) if timestamps else \
            datetime.fromtimestamp(float(responses[1].json()["timestamp"]) / 1000.)
        return str(days_ago(report_datetime)), "100", []
