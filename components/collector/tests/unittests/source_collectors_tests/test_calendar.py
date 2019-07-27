"""Unit tests for the calendar source."""

from datetime import datetime

from .source_collector_test_case import SourceCollectorTestCase


class CalendarSourceUpToDatenessTest(SourceCollectorTestCase):
    """Unit tests for the calendar source up to dateness metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(
            type="source_up_to_dateness", addition="max",
            sources=dict(source_uuid=dict(type="calendar", parameters=dict())))

    def test_source_up_to_dateness(self):
        """Test the number of days since the user-specified date."""
        self.metric["sources"]["source_uuid"]["parameters"]["date"] = "2019-06-01"
        response = self.collect(self.metric)
        self.assert_value(str((datetime.now() - datetime(2019, 6, 1)).days), response)

    def test_source_up_to_dateness_with_default(self):
        """Test the number of days without user-specified date."""
        response = self.collect(self.metric)
        self.assert_value(str((datetime.now() - datetime(2019, 1, 1)).days), response)
