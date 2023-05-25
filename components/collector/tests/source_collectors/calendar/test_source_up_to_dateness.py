"""Unit tests for the calendar source up-to-dateness collector."""

from collector_utilities.date_time import days_ago, datetime_fromparts

from .base import CalendarTestCase


class CalendarSourceUpToDatenessTest(CalendarTestCase):
    """Unit tests for the calendar source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"

    async def test_source_up_to_dateness(self):
        """Test the number of days since the user-specified date."""
        self.set_source_parameter("date", "2019-06-01")
        response = await self.collect()
        self.assert_measurement(response, value=str(days_ago(datetime_fromparts(2019, 6, 1))))

    async def test_source_up_to_dateness_with_default(self):
        """Test the number of days without user-specified date."""
        response = await self.collect()
        self.assert_measurement(response, value="0")
