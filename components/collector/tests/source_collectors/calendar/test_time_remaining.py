"""Unit tests for the calendar time remaining collector."""

from datetime import datetime

from ...data_model_fixture import CALENDAR_DEFAULT_DATE
from ..source_collector_test_case import SourceCollectorTestCase


class CalendarTimeRemainingTest(SourceCollectorTestCase):
    """Unit tests for the calendar time remaining collector."""

    SOURCE_TYPE = "calendar"
    METRIC_TYPE = "time_remaining"

    async def test_time_remaining(self):
        """Test the number of days until the user-specified date."""
        self.set_source_parameter("date", "3000-01-01")
        response = await self.collect()
        self.assert_measurement(response, value=str((datetime(3000, 1, 1) - datetime.now()).days))

    async def test_time_remaining_with_default(self):
        """Test the number of days without user-specified date."""
        response = await self.collect()
        self.assert_measurement(response, value=str((CALENDAR_DEFAULT_DATE - datetime.now()).days))
