"""Unit tests for the Jenkins test report source up-to-dateness collector."""

from datetime import datetime

from collector_utilities.functions import days_ago

from .base import JenkinsTestReportTestCase


class JenkinsTestReportSourceUpToDatenessTest(JenkinsTestReportTestCase):
    """Unit tests for the Jenkins test report source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        response = await self.collect(
            get_request_json_return_value=dict(suites=[dict(timestamp="2019-04-02T08:52:50")])
        )
        expected_age = (datetime.now() - datetime(2019, 4, 2, 8, 52, 50)).days
        self.assert_measurement(response, value=str(expected_age))

    async def test_source_up_to_dateness_without_timestamps(self):
        """Test that the job age in days is returned if the test report doesn't contain timestamps."""
        response = await self.collect(
            get_request_json_side_effect=[dict(suites=[dict(timestamp=None)]), dict(timestamp="1565284457173")]
        )
        expected_age = days_ago(datetime.fromtimestamp(1565284457173 / 1000.0))
        self.assert_measurement(response, value=str(expected_age))
