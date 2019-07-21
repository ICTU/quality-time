"""Unit tests for the calendar source."""

from datetime import datetime
import unittest

from metric_collectors import MetricCollector


class CalendarTest(unittest.TestCase):
    """Unit tests for the calendar metrics."""

    def test_source_up_to_dateness(self):
        """Test the number of days since the user-specified date."""
        metric = dict(
            type="source_up_to_dateness", addition="max",
            sources=dict(a=dict(type="calendar", parameters=dict(date="2019-01-01"))))
        response = MetricCollector(metric).get()
        self.assertEqual(str((datetime.now() - datetime(2019, 1, 1)).days), response["sources"][0]["value"])
