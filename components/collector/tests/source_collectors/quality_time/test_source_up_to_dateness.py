"""Unit tests for the Quality-time source up-to-dateness collector."""

from datetime import datetime

from dateutil.parser import parse

from collector_utilities.functions import days_ago

from .base import QualityTimeTestCase


class QualityTimeSourceUpToDatenessTest(QualityTimeTestCase):
    """Unit tests for the Quality-time source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_source_up_to_dateness(self):
        """Test that the source up-to-dateness of all reports can be measured."""
        response = await self.collect(self.metric, get_request_json_return_value=self.reports)
        expected_age = days_ago(parse("2020-06-24T07:53:17+00:00"))
        self.assert_measurement(response, value=str(expected_age), total="100", entities=[])

    async def test_source_up_to_dateness_report(self):
        """Test that the source up-to-dateness of a specific report can be measured."""
        self.sources["source_id"]["parameters"]["reports"] = ["r2"]
        response = await self.collect(self.metric, get_request_json_return_value=self.reports)
        expected_age = days_ago(datetime.min)
        self.assert_measurement(response, value=str(expected_age), total="100", entities=[])
