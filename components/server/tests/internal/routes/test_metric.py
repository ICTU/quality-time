"""Unit tests for the metric routes."""

import unittest
from unittest.mock import Mock

from internal.routes import get_metrics

from ..fixtures import METRIC_ID, REPORT_ID, SUBJECT_ID, create_report


class MetricTest(unittest.TestCase):
    """Unit tests for adding and deleting metrics."""

    def setUp(self):
        """Override to set up the mock database."""
        self.database = Mock()
        self.report = create_report()
        self.database.reports.find.return_value = [self.report]
        self.database.reports.distinct.return_value = [REPORT_ID]
        self.database.datamodels.find_one.return_value = {"_id": "data_model_id", "metrics": {"metric_type": {}}}

    def test_get_metrics(self):
        """Test that the metrics can be retrieved."""
        self.assertEqual(
            {
                METRIC_ID: dict(
                    report_uuid=REPORT_ID,
                    name="Metric",
                    addition="sum",
                    accept_debt=False,
                    type="metric_type",
                    tags=["security"],
                    target="0",
                    scales=["count", "percentage"],
                    latest_measurement=None,
                    recent_measurements=[],
                    scale="count",
                    status=None,
                    status_start=None,
                    sources=dict(
                        source_uuid=dict(
                            name="Source", type="source_type", parameters=dict(url="https://url", password="password")
                        )
                    ),
                )
            },
            get_metrics(self.database),
        )

    def test_get_metrics_with_issue(self):
        """Test that the metrics can be retrieved and the issue tracker is included."""
        self.report["issue_tracker"] = dict(type="jira", parameters=dict(url="https://jira"))
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["issue_ids"] = ["FOO-42"]
        self.assertEqual(
            {
                METRIC_ID: dict(
                    report_uuid=REPORT_ID,
                    name="Metric",
                    addition="sum",
                    accept_debt=False,
                    type="metric_type",
                    tags=["security"],
                    target="0",
                    issue_ids=["FOO-42"],
                    issue_tracker=dict(type="jira", parameters=dict(url="https://jira")),
                    latest_measurement=None,
                    recent_measurements=[],
                    scale="count",
                    status=None,
                    status_start=None,
                    scales=["count", "percentage"],
                    sources=dict(
                        source_uuid=dict(
                            name="Source", type="source_type", parameters=dict(url="https://url", password="password")
                        )
                    ),
                )
            },
            get_metrics(self.database),
        )
