"""Unit tests for the Trivy JSON source up-to-dateness collector."""

from collector_utilities.date_time import days_ago, parse_datetime

from .base import TrivyJSONTestCase


class TrivyJSONSourceUpToDatenessTest(TrivyJSONTestCase):
    """Unit tests for the source up-to-dateness metric."""

    METRIC_TYPE = "source_up_to_dateness"

    async def test_source_up_to_dateness_schema_version_1(self):
        """Test the source up-to-dateness."""
        response = await self.collect(get_request_json_return_value=self.vulnerabilities_json(1))
        expected_error = "Measuring source up-to-dateness is not supported with Trivy JSON schema version 1"
        self.assert_measurement(response, parse_error=expected_error)

    async def test_source_up_to_dateness_schema_version_2(self):
        """Test the source up-to-dateness."""
        response = await self.collect(get_request_json_return_value=self.vulnerabilities_json())
        expected_value = str(days_ago(parse_datetime("2024-12-26T21:58:15.943876+05:30")))
        self.assert_measurement(response, value=expected_value)
