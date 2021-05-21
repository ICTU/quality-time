"""Unit tests for the Quality-time source up-to-dateness collector."""

from datetime import datetime

from dateutil.parser import parse

from collector_utilities.functions import days_ago

from .base import QualityTimeTestCase


class QualityTimeSourceUpToDatenessTest(QualityTimeTestCase):
    """Unit tests for the Quality-time source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    def setUp(self):
        super().setUp()
        self.api_url = f"{self.url}/api/v3/reports"

    async def test_source_up_to_dateness(self):
        """Test that the source up-to-dateness of all reports can be measured."""
        response = await self.collect(get_request_json_return_value=self.reports)
        expected_age = days_ago(parse("2020-06-24T07:53:17+00:00"))
        self.assert_measurement(response, value=str(expected_age), total="100", entities=[])

    async def test_source_up_to_dateness_report(self):
        """Test that the source up-to-dateness of a specific report can be measured."""
        self.set_source_parameter("reports", ["r2"])
        response = await self.collect(get_request_json_return_value=self.reports)
        expected_age = days_ago(datetime.min)
        self.assert_measurement(response, value=str(expected_age), total="100", entities=[])

    def assert_measurement(self, measurement, *, source_index: int = 0, **attributes) -> None:
        """Override to pass the api and landing URLs."""
        attributes["api_url"] = self.api_url
        super().assert_measurement(measurement, source_index=source_index, **attributes)
