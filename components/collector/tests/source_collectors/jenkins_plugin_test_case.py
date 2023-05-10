"""Generic unit tests for Jenkins plugin sources."""

from collector_utilities.date_time import days_ago, datetime_fromtimestamp


class JenkinsPluginSourceUpToDatenessMixin:
    """Unit tests for Jenkins plugin source up-to-dateness collectors to be mixed in."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_source_up_to_dateness(self):
        """Test that the source up-to-dateness is returned."""
        response = await self.collect(get_request_json_return_value={"timestamp": "1565284457173"})
        expected_age = days_ago(datetime_fromtimestamp(1565284457173 / 1000.0))
        self.assert_measurement(response, value=str(expected_age))
