"""Test the reports collection."""

import unittest
from unittest.mock import Mock

from shared_data_model import DATA_MODEL
from shared.model.metric import Metric
from shared.utils.type import MetricId

from database.reports import latest_metric

from ..fixtures import METRIC_ID, REPORT_ID, SOURCE_ID


class MetricsTest(unittest.TestCase):
    """Unit tests for getting metrics from the reports collection."""

    def setUp(self):
        """Override to create a mock database fixture."""
        self.database = Mock()
        self.data_model = DATA_MODEL.dict()
        self.data_model["_id"] = "id"
        self.database.datamodels.find_one.return_value = self.data_model
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
            Metric(self.data_model, dict(tags=[], type="violations"), METRIC_ID),
            latest_metric(self.database, REPORT_ID, METRIC_ID),
        )

    def test_no_latest_metrics(self):
        """Test that None is returned for missing metrics."""
        self.assertIsNone(latest_metric(self.database, REPORT_ID, MetricId("non-existing")))

    def test_no_latest_report(self):
        """Test that None is returned for missing metrics."""
        self.database.reports.find_one.return_value = None
        self.assertIsNone(latest_metric(self.database, REPORT_ID, METRIC_ID))
