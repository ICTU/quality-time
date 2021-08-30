"""Unit tests for the metrics route(s)."""

import unittest
from unittest.mock import MagicMock

from routes.metrics import get_metrics


class MetricsRouteTest(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the metrics routes."""

    async def test_get_metrics(self):
        """Test that the metrics can be retrieved and deleted reports are skipped."""
        database = MagicMock()
        reports = MagicMock()
        reports.__aiter__.return_value = [
            dict(report_uuid="report_id", subjects=dict(subject_id=dict(metrics=dict(metric_id={}))))
        ]
        database.reports.find.return_value = reports
        self.assertEqual(dict(metric_id=dict(report_uuid="report_id")), await get_metrics(database))

    async def test_get_metrics_with_issue(self):
        """Test that the metrics with issues can be retrieved."""
        issue_tracker = dict(type="jira", parameters=dict(url="https://jira"))
        database = MagicMock()
        reports = MagicMock()
        reports.__aiter__.return_value = [
            dict(
                report_uuid="report_id", 
                issue_tracker=issue_tracker, 
                subjects=dict(subject_id=dict(metrics=dict(metric_id=dict(issue_ids=["FOO=42"])))),
            )
        ]
        database.reports.find.return_value = reports
        self.assertEqual(
            dict(metric_id=dict(report_uuid="report_id", issue_tracker=issue_tracker)), await get_metrics(database)
        )
