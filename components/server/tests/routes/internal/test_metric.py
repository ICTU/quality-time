"""Unit tests for the metric routes."""

import unittest
from unittest.mock import Mock

from routes.internal import get_metrics

from ...fixtures import JOHN, METRIC_ID, REPORT_ID, SUBJECT_ID, create_report


class MetricTest(unittest.TestCase):
    """Unit tests for adding and deleting metrics."""

    def setUp(self):
        """Override to set up the mock database."""
        self.database = Mock()
        self.report = create_report()
        self.database.reports.find.return_value = [self.report]
        self.database.measurements.find.return_value = []
        self.database.sessions.find_one.return_value = JOHN
        self.database.datamodels.find_one.return_value = dict(
            _id="",
            metrics=dict(
                metric_type=dict(
                    name="Metric type",
                    default_scale="count",
                    addition="sum",
                    direction="<",
                    target="0",
                    near_target="1",
                    tags=[],
                )
            ),
            sources=dict(source_type=dict(name="Source type")),
        )

    def test_get_metrics(self):
        """Test that the metrics can be retrieved and deleted reports are skipped."""
        self.database.reports_overviews.find_one.return_value = dict(_id="id", title="Reports", subtitle="")
        self.database.reports.distinct.return_value = [REPORT_ID, "deleted_report"]
        self.database.reports.find_one.side_effect = [self.report, dict(deleted=True)]
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
        self.database.reports_overviews.find_one.return_value = dict(_id="id", title="Reports", subtitle="")
        self.database.reports.distinct.return_value = [REPORT_ID]
        self.database.reports.find_one.side_effect = [self.report]
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
                    sources=dict(
                        source_uuid=dict(
                            name="Source", type="source_type", parameters=dict(url="https://url", password="password")
                        )
                    ),
                )
            },
            get_metrics(self.database),
        )
