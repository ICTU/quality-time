"""Unit tests for the Axe-core source up-to-dateness collector."""

from datetime import datetime, timezone

from .base import AxeCoreTestCase


class AxeCoreSourceUpToDatenessTest(AxeCoreTestCase):
    """Unit tests for the source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"
    TIMESTAMP = "2020-09-01T14:07:09.445Z"

    def setUp(self):
        """Extend to set up test fixtures."""
        super().setUp()
        self.expected_age = (datetime.now(tz=timezone.utc) - datetime(2020, 9, 1, 14, 6, 9, tzinfo=timezone.utc)).days

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        axe_json = dict(timestamp=self.TIMESTAMP)
        response = await self.collect(get_request_json_return_value=axe_json)
        self.assert_measurement(response, value=str(self.expected_age))

    async def test_source_up_to_dateness_in_list(self):
        """Test that the source age in days is returned."""
        axe_json = [dict(timestamp=self.TIMESTAMP)]
        response = await self.collect(get_request_json_return_value=axe_json)
        self.assert_measurement(response, value=str(self.expected_age))
