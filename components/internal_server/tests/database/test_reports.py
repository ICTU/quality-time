"""Test the reports collection."""

from shared.model.metric import Metric
from shared.utils.type import MetricId

from database.reports import latest_metric

from ..base import DataModelTestCase
from ..fixtures import METRIC_ID, REPORT_ID, SOURCE_ID


class MetricsTest(DataModelTestCase):
    """Unit tests for getting metrics from the reports collection."""

    def setUp(self):
        """Extend to create a report fixture."""
        super().setUp()
        report = dict(
            _id="1",
            report_uuid=REPORT_ID,
            subjects=dict(subject_uuid=dict(metrics=dict(metric_uuid=dict(type="violations", tags=[])))),
        )
        self.database.reports.find.return_value = [report]
        self.database.reports.find_one.return_value = report

    def test_latest_metrics(self):
        """Test that the latest metrics are returned."""
        self.database.measurements.find.return_value = [
            dict(
                _id="id",
                metric_uuid=METRIC_ID,
                status="red",
                sources=[dict(source_uuid=SOURCE_ID, parse_error=None, connection_error=None, value="42")],
            )
        ]
        self.assertEqual(
            Metric(self.DATA_MODEL, dict(tags=[], type="violations"), METRIC_ID),
            latest_metric(self.database, REPORT_ID, METRIC_ID),
        )

    def test_no_latest_metrics(self):
        """Test that None is returned for missing metrics."""
        self.assertIsNone(latest_metric(self.database, REPORT_ID, MetricId("non-existing")))

    def test_no_latest_report(self):
        """Test that None is returned for missing metrics."""
        self.database.reports.find_one.return_value = None
        self.assertIsNone(latest_metric(self.database, REPORT_ID, METRIC_ID))
