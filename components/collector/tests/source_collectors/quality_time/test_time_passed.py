"""Unit tests for the Quality-time time passed collector."""

from datetime import datetime

from dateutil.parser import parse

from collector_utilities.functions import days_ago

from .base import QualityTimeTestCase


class QualityTimeTimePassedTest(QualityTimeTestCase):
    """Unit tests for the Quality-time time passed collector."""

    METRIC_TYPE = "time_passed"
    METRIC_ADDITION = "max"

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.api_url = f"{self.url}/api/v3/reports"

    async def test_time_passed_all_reports(self):
        """Test that the time passed since any report was updated can be measured."""
        response = await self.collect(get_request_json_return_value=self.reports)
        expected_age = days_ago(parse("2020-06-24T07:53:17+00:00"))
        self.assert_measurement(response, value=str(expected_age), total="100", entities=[])

    async def test_time_passed_report(self):
        """Test that the time passed since a specific report was updated can be measured."""
        self.set_source_parameter("reports", ["r2"])
        response = await self.collect(get_request_json_return_value=self.reports)
        expected_age = days_ago(datetime.min)
        self.assert_measurement(response, value=str(expected_age), total="100", entities=[])

    def assert_measurement(self, measurement, *, source_index: int = 0, **attributes) -> None:
        """Override to pass the API URLs."""
        attributes["api_url"] = self.api_url
        super().assert_measurement(measurement, source_index=source_index, **attributes)
