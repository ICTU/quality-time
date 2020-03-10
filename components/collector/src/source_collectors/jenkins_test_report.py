"""Jenkins test report metric collector."""

from datetime import datetime
from typing import cast, Dict, Final, List, Tuple

from dateutil.parser import parse

from collector_utilities.type import Entity, Entities, Responses, URL, Value
from collector_utilities.functions import days_ago
from .source_collector import SourceCollector


TestCase = Dict[str, str]
Suite = Dict[str, List[TestCase]]


class JenkinsTestReportTests(SourceCollector):
    """Collector to get the amount of tests from a Jenkins test report."""

    JENKINS_TEST_REPORT_COUNTS: Final[Dict[str, str]] = dict(
        failed="failCount", passed="passCount", skipped="skipCount")

    async def _api_url(self) -> URL:
        return URL(f"{await super()._api_url()}/lastSuccessfulBuild/testReport/api/json")

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        json = await responses[0].json()
        statuses = cast(List[str], self._parameter("test_result"))
        status_counts = [self.JENKINS_TEST_REPORT_COUNTS[status] for status in statuses]
        results = [report["result"] for report in json["childReports"]] if "childReports" in json else [json]
        value = sum(int(result.get(status_count, 0)) for status_count in status_counts for result in results)
        suites: List[Suite] = []
        for result in results:
            suites.extend(result["suites"])
        entities = [
            self.__entity(case) for suite in suites for case in suite.get("cases", [])
            if self.__status(case) in statuses]
        return str(value), "100", entities

    def __entity(self, case: TestCase) -> Entity:
        """Transform a test case into a test case entity."""
        name = case.get("name", "<nameless test case>")
        return dict(key=name, name=name, class_name=case.get("className", ""), test_result=self.__status(case))

    @staticmethod
    def __status(case: TestCase) -> str:
        """Return the status of the test case."""
        # The Jenkins test report has three counts: passed, skipped, and failed. Individual test cases
        # can be skipped (indicated by the attribute skipped being "true") and/or have a status that can
        # take the values: "failed", "passed", "regression", and "fixed".
        test_case_status = "skipped" if case.get("skipped") == "true" else case.get("status", "").lower()
        return dict(regression="failed", fixed="passed").get(test_case_status, test_case_status)


class JenkinsTestReportSourceUpToDateness(SourceCollector):
    """Collector to get the age of the Jenkins test report."""

    async def _get_source_responses(self, api_url: URL) -> Responses:
        test_report_url = URL(f"{api_url}/lastSuccessfulBuild/testReport/api/json")
        job_url = URL(f"{api_url}/lastSuccessfulBuild/api/json")
        return await super()._get_source_responses(test_report_url) + await super()._get_source_responses(job_url)

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        timestamps = [suite.get("timestamp") for suite in (await responses[0].json()).get("suites", [])
                      if suite.get("timestamp")]
        report_datetime = parse(max(timestamps)) if timestamps else \
            datetime.fromtimestamp(float((await responses[1].json())["timestamp"]) / 1000.)
        return str(days_ago(report_datetime)), "100", []
