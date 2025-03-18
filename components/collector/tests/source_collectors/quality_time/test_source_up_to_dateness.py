"""Unit tests for the Quality-time source up-to-dateness collector."""

from datetime import UTC, datetime

from dateutil.parser import parse

from collector_utilities.date_time import days_ago

from .base import QualityTimeTestCase


class QualityTimeSourceUpToDatenessTest(QualityTimeTestCase):
    """Unit tests for the Quality-time source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_source_up_to_dateness(self):
        """Test that the source up-to-dateness of all reports can be measured."""
        self.set_source_parameter("reports", ["r1"])
        response = await self.collect(get_request_json_return_value=self.reports)
        expected_age = days_ago(parse("2020-06-24T07:53:17+00:00"))
        self.assert_measurement(response, value=str(expected_age), total="0", entities=[])

    async def test_source_up_to_dateness_report(self):
        """Test that the source up-to-dateness of a specific report can be measured."""
        self.set_source_parameter("reports", ["r2"])
        response = await self.collect(get_request_json_return_value=self.reports)
        expected_age = days_ago(datetime.min.replace(tzinfo=UTC))
        self.assert_measurement(response, value=str(expected_age), total="0", entities=[])

    def assert_measurement(self, measurement, *, source_index: int = 0, **attributes: list | str | None) -> None:
        """Override to pass the api URLs."""
        attributes["api_url"] = f"{self.url}/api/internal/report"
        super().assert_measurement(measurement, source_index=source_index, **attributes)
