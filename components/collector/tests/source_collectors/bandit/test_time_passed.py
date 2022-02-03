"""Unit tests for the Bandit time passed collector."""

from datetime import datetime, timezone

from .base import BanditTestCase


class BanditTimePassedTest(BanditTestCase):
    """Unit tests for the time passed collector."""

    METRIC_TYPE = "time_passed"
    METRIC_ADDITION = "max"

    async def test_time_passed(self):
        """Test that the source age in days is returned."""
        bandit_json = dict(generated_at="2019-07-12T07:38:47Z")
        response = await self.collect(get_request_json_return_value=bandit_json)
        expected_age = (datetime.now(tz=timezone.utc) - datetime(2019, 7, 12, 7, 38, 47, tzinfo=timezone.utc)).days
        self.assert_measurement(response, value=str(expected_age))
