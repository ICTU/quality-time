"""Unit tests for the metrics route(s)."""

import unittest
from unittest.mock import MagicMock

from routes.metrics import get_metrics


class MetricsRouteTest(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the metrics routes."""

    def setUp(self) -> None:
        """Override to create database fixture."""
        self.database = MagicMock()
        self.reports = [dict(report_uuid="report_id", subjects=dict(subject_id=dict(metrics=dict(metric_id={}))))]
        self.database.reports.find.return_value = reports_cursor = MagicMock()
        reports_cursor.__aiter__.return_value = self.reports

    async def test_get_metrics(self):
        """Test that the metrics can be retrieved."""
        self.assertEqual(dict(metric_id=dict(report_uuid="report_id")), await get_metrics(self.database))

    async def test_get_metrics_with_issue(self):
        """Test that metrics with issues can be retrieved."""
        self.reports[0]["issue_tracker"] = issue_tracker = dict(type="jira", parameters=dict(url="https://jira"))
        self.reports[0]["subjects"]["subject_id"]["metrics"]["metric_id"]["issue_ids"] = ["FOO-42"]
        self.assertEqual(
            dict(metric_id=dict(report_uuid="report_id", issue_tracker=issue_tracker, issue_ids=["FOO-42"])),
            await get_metrics(self.database),
        )
