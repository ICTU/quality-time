"""Unit tests for the report routes."""

import unittest
from unittest.mock import Mock

from routes.report import get_metrics


class MetricTest(unittest.TestCase):
    """Unit tests for getting metrics."""

    def test_get_metrics(self):
        """Test that the metrics can be retrieved and deleted reports are skipped."""
        report = dict(
            _id="id", report_uuid="report_uuid",
            subjects=dict(subject_uuid=dict(metrics=dict(metric_uuid=dict(tags=[])))))
        database = Mock()
        database.reports_overviews.find_one.return_value = dict(_id="id", title="Reports", subtitle="")
        database.reports.distinct.return_value = ["report_uuid", "deleted_report"]
        database.reports.find_one.side_effect = [report, dict(deleted=True)]
        database.measurements.find.return_value = [dict(
            _id="id", metric_uuid="metric_uuid", status="red",
            sources=[dict(source_uuid="source_uuid", parse_error=None, connection_error=None, value="42")])]
        self.assertEqual(dict(metric_uuid=dict(tags=[])), get_metrics(database))
