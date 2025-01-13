"""Unit tests for the Harbor JSON source up-to-dateness collector."""

from collector_utilities.date_time import days_ago, parse_datetime

from .base import HarborJSONCollectorTestCase


class HarborJSONSourceUpToDatenessTest(HarborJSONCollectorTestCase):
    """Unit tests for the source up-to-dateness metric."""

    METRIC_TYPE = "source_up_to_dateness"

    async def test_souce_up_to_dateness(self):
        """Test the source up-to-dateness."""
        response = await self.collect(get_request_json_return_value=self.VULNERABILITIES_JSON)
        expected_value = str(days_ago(parse_datetime("2023-08-26T16:32:21.923910328Z")))
        self.assert_measurement(response, value=expected_value)
