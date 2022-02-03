"""Unit tests for the calendar time passed collector."""

from datetime import date

from ...data_model_fixture import CALENDAR_DEFAULT_DATE
from ..source_collector_test_case import SourceCollectorTestCase


class CalendarTimePassedTest(SourceCollectorTestCase):
    """Unit tests for the calendar time passed collector."""

    SOURCE_TYPE = "calendar"
    METRIC_TYPE = "time_passed"

    async def test_time_passed(self):
        """Test the number of days since the user-specified date."""
        self.set_source_parameter("date", "2019-06-01")
        response = await self.collect()
        self.assert_measurement(response, value=str((date.today() - date(2019, 6, 1)).days))

    async def test_time_passed_with_default(self):
        """Test the number of days without user-specified date."""
        response = await self.collect()
        self.assert_measurement(response, value=str((date.today() - CALENDAR_DEFAULT_DATE).days))
