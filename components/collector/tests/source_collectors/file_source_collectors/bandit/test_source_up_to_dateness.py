"""Unit tests for the Bandit source up-to-dateness collector."""

from datetime import datetime, timezone

from .base import BanditTestCase


class BanditSourceUpToDatenessTest(BanditTestCase):
    """Unit tests for the source up to dateness metric."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        bandit_json = dict(generated_at="2019-07-12T07:38:47Z")
        response = await self.collect(self.metric, get_request_json_return_value=bandit_json)
        expected_age = (datetime.now(tz=timezone.utc) - datetime(2019, 7, 12, 7, 38, 47, tzinfo=timezone.utc)).days
        self.assert_measurement(response, value=str(expected_age))
