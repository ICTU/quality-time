"""Jenkins test report metric source up-to-dateness collector."""

from datetime import datetime

from dateutil.parser import parse

from base_collectors import SourceCollector
from collector_utilities.functions import days_ago
from collector_utilities.type import URL
from source_model import SourceMeasurement, SourceResponses


class JenkinsTestReportSourceUpToDateness(SourceCollector):
    """Collector to get the age of the Jenkins test report."""

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to get both the test report and the job that created it, so we can use either one to get a date."""
        test_report_url = URL(f"{urls[0]}/lastSuccessfulBuild/testReport/api/json")
        job_url = URL(f"{urls[0]}/lastSuccessfulBuild/api/json")
        return await super()._get_source_responses(test_report_url, job_url)

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the timestamp from either the job or the test report."""
        timestamps = [
            suite.get("timestamp") for suite in (await responses[0].json()).get("suites", []) if suite.get("timestamp")
        ]
        report_datetime = (
            parse(max(timestamps))
            if timestamps
            else datetime.fromtimestamp(float((await responses[1].json())["timestamp"]) / 1000.0)
        )
        return SourceMeasurement(value=str(days_ago(report_datetime)))
