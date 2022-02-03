"""Unit tests for the Axe-core time passed collector."""

from datetime import datetime, timezone

from .base import AxeCoreTestCase


class AxeCoreTimePassedTest(AxeCoreTestCase):
    """Unit tests for the time passed collector."""

    METRIC_TYPE = "time_passed"
    METRIC_ADDITION = "max"
    TIMESTAMP = "2020-09-01T14:07:09.445Z"

    def setUp(self):
        """Extend to set up test fixtures."""
        super().setUp()
        self.expected_age = (datetime.now(tz=timezone.utc) - datetime(2020, 9, 1, 14, 6, 9, tzinfo=timezone.utc)).days

    async def test_time_passed(self):
        """Test that the source age in days is returned."""
        axe_json = dict(timestamp=self.TIMESTAMP)
        response = await self.collect(get_request_json_return_value=axe_json)
        self.assert_measurement(response, value=str(self.expected_age))

    async def test_time_passed_in_list(self):
        """Test that the source age in days is returned."""
        axe_json = [dict(timestamp=self.TIMESTAMP)]
        response = await self.collect(get_request_json_return_value=axe_json)
        self.assert_measurement(response, value=str(self.expected_age))
