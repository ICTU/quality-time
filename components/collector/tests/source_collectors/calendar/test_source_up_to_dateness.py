"""Unit tests for the calendar source up-to-dateness collector."""

from datetime import datetime

from ..source_collector_test_case import SourceCollectorTestCase


class CalendarSourceUpToDatenessTest(SourceCollectorTestCase):
    """Unit tests for the calendar source up-to-dateness collector."""

    SOURCE_TYPE = "calendar"
    METRIC_TYPE = "source_up_to_dateness"

    async def test_source_up_to_dateness(self):
        """Test the number of days since the user-specified date."""
        self.set_source_parameter("date", "2019-06-01")
        response = await self.collect()
        self.assert_measurement(response, value=str((datetime.now() - datetime(2019, 6, 1)).days))

    async def test_source_up_to_dateness_with_default(self):
        """Test the number of days without user-specified date."""
        response = await self.collect()
        self.assert_measurement(response, value=str((datetime.now() - datetime(2020, 1, 1)).days))
