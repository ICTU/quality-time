"""Generic unit tests for Jenkins plugin sources."""

from datetime import datetime

from collector_utilities.functions import days_ago


class JenkinsPluginSourceUpToDatenessMixin:  # pylint: disable=too-few-public-methods
    """Unit tests for Jenkins plugin source up-to-dateness collectors to be mixed in."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_source_up_to_dateness(self):
        """Test that the source up-to-dateness is returned."""
        response = await self.collect(self.metric, get_request_json_return_value=dict(timestamp="1565284457173"))
        expected_age = days_ago(datetime.fromtimestamp(1565284457173 / 1000.0))
        self.assert_measurement(response, value=str(expected_age))
