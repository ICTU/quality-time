"""Test the reports collection."""

import unittest
from unittest.mock import Mock

from src.database.reports import latest_metric


class MetricsTest(unittest.TestCase):
    """Unit tests for getting metrics from the reports collection."""

    def test_latest_metrics(self):
        """Test that the latest metrics are returned."""
        database = Mock()
        database.reports.distinct.return_value = ["report_uuid"]
        database.reports.find_one.return_value = dict(
            _id="1", report_uuid="report_uuid",
            subjects=dict(subject_uuid=dict(metrics=dict(metric_uuid=dict(tags=[])))))
        database.measurements.find.return_value = [
            dict(
                _id="id", metric_uuid="metric_uuid", status="red",
                sources=[dict(source_uuid="source_uuid", parse_error=None, connection_error=None, value="42")])]
        self.assertEqual(dict(tags=[]), latest_metric(database, "report_uuid", "metric_uuid"))

    def test_no_latest_metrics(self):
        """Test that None is returned for missing metrics."""
        database = Mock()
        database.reports.distinct.return_value = ["report_uuid"]
        database.reports.find_one.return_value = dict(_id="1", report_uuid="report_uuid")
        database.measurements.find.return_value = []
        self.assertEqual(None, latest_metric(database, "report_uuid", "non-existing"))
