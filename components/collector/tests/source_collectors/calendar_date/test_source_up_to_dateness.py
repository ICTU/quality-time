"""Unit tests for the calendar source up-to-dateness collector."""

from collector_utilities.date_time import datetime_from_parts, days_ago

from .base import CalendarTestCase


class CalendarSourceUpToDatenessTest(CalendarTestCase):
    """Unit tests for the calendar source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"

    async def test_source_up_to_dateness(self):
        """Test the number of days since the user-specified date."""
        self.set_source_parameter("date", "2019-06-01")
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value=str(days_ago(datetime_from_parts(2019, 6, 1))))

    async def test_source_up_to_dateness_with_default(self):
        """Test the number of days without user-specified date."""
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="0")
