"""Jenkins test report metric tests collector."""

from typing import Final, cast

from base_collectors import SourceCollector
from collector_utilities.type import URL
from source_model import Entities, Entity, SourceMeasurement, SourceResponses


TestCase = dict[str, str]
Suite = dict[str, list[TestCase]]


class JenkinsTestReportTests(SourceCollector):
    """Collector to get the amount of tests from a Jenkins test report."""

    JENKINS_TEST_REPORT_COUNTS: Final[dict[str, str]] = dict(
        failed="failCount", passed="passCount", skipped="skipCount"
    )

    async def _api_url(self) -> URL:
        """Extend to add the test report API path."""
        return URL(f"{await super()._api_url()}/lastSuccessfulBuild/testReport/api/json")

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the test report."""
        json = await responses[0].json()
        statuses = cast(list[str], self._parameter("test_result"))
        status_counts = [self.JENKINS_TEST_REPORT_COUNTS[status] for status in statuses]
        all_status_counts = self.JENKINS_TEST_REPORT_COUNTS.values()
        results = [report["result"] for report in json["childReports"]] if "childReports" in json else [json]
        value = sum(int(result.get(status_count, 0)) for status_count in status_counts for result in results)
        total = sum(int(result.get(status_count, 0)) for status_count in all_status_counts for result in results)
        suites: list[Suite] = []
        for result in results:
            suites.extend(result["suites"])
        entities = Entities(
            self.__entity(case)
            for suite in suites
            for case in suite.get("cases", [])
            if self.__status(case) in statuses
        )
        return SourceMeasurement(value=str(value), total=str(total), entities=entities)

    def __entity(self, case: TestCase) -> Entity:
        """Transform a test case into a test case entity."""
        name = case.get("name", "<nameless test case>")
        return Entity(
            key=name,
            name=name,
            class_name=case.get("className", ""),
            test_result=self.__status(case),
            age=str(case.get("age", 0)),
        )

    @staticmethod
    def __status(case: TestCase) -> str:
        """Return the status of the test case."""
        # The Jenkins test report has three counts: passed, skipped, and failed. Individual test cases
        # can be skipped (indicated by the attribute skipped being "true") and/or have a status that can
        # take the values: "failed", "passed", "regression", and "fixed".
        test_case_status = "skipped" if case.get("skipped") == "true" else case.get("status", "").lower()
        return dict(regression="failed", fixed="passed").get(test_case_status, test_case_status)
