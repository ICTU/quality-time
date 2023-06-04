"""Unit tests for the calendar time remaining collector."""

from collector_utilities.date_time import datetime_fromparts, days_to_go

from .base import CalendarTestCase


class CalendarTimeRemainingTest(CalendarTestCase):
    """Unit tests for the calendar time remaining collector."""

    METRIC_TYPE = "time_remaining"

    async def test_time_remaining(self):
        """Test the number of days until the user-specified date."""
        self.set_source_parameter("date", "3000-01-01")
        response = await self.collect()
        self.assert_measurement(response, value=str(days_to_go(datetime_fromparts(3000, 1, 1))))

    async def test_time_remaining_with_default(self):
        """Test the number of days without user-specified date."""
        response = await self.collect()
        self.assert_measurement(response, value="0")
