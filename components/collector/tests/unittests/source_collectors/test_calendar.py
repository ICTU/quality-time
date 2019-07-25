"""Unit tests for the calendar source."""

from datetime import datetime
import unittest

from metric_collectors import MetricCollector


class CalendarSourceUpToDatenessTest(unittest.TestCase):
    """Unit tests for the calendar source up to dateness metric."""

    def setUp(self):
        self.datamodel = dict(sources=dict(calendar=dict(parameters=dict(date=dict(default_value="2019-01-01")))))
        self.metric = dict(
            type="source_up_to_dateness", addition="max",
            sources=dict(source_uuid=dict(type="calendar", parameters=dict())))

    def test_source_up_to_dateness(self):
        """Test the number of days since the user-specified date."""
        self.metric["sources"]["source_uuid"]["parameters"]["date"] = "2019-06-01"
        response = MetricCollector(self.metric, self.datamodel).get()
        self.assertEqual(str((datetime.now() - datetime(2019, 6, 1)).days), response["sources"][0]["value"])

    def test_source_up_to_dateness_with_default(self):
        """Test the number of days without user-specified date."""
        response = MetricCollector(self.metric, self.datamodel).get()
        self.assertEqual(str((datetime.now() - datetime(2019, 1, 1)).days), response["sources"][0]["value"])
