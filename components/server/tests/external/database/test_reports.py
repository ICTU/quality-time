"""Test the reports collection."""

import unittest
from unittest.mock import Mock

from external.database.reports import latest_metric, metrics_of_subject
from external.model.metric import Metric
from external.server_utilities.type import MetricId

from ..fixtures import METRIC_ID, METRIC_ID2, SUBJECT_ID


class MetricsTest(unittest.TestCase):
    """Unit tests for getting metrics from the reports collection."""

    def setUp(self):
        """Override to create a mock database fixture."""
        self.database = Mock()
        self.database.datamodels.find_one.return_value = self.data_model = dict(_id="id", metrics=dict(metric_type={}))
        self.database.reports.find.return_value = [
            dict(
                _id="1",
                report_uuid="report_uuid",
                subjects=dict(subject_uuid=dict(metrics=dict(metric_uuid=dict(type="metric_type", tags=[])))),
            )
        ]

    def test_latest_metrics(self):
        """Test that the latest metrics are returned."""
        self.database.measurements.find.return_value = [
            dict(
                _id="id",
                metric_uuid=METRIC_ID,
                status="red",
                sources=[dict(source_uuid="source_uuid", parse_error=None, connection_error=None, value="42")],
            )
        ]
        self.assertEqual(
            Metric(self.data_model, dict(tags=[], type="metric_type"), METRIC_ID),
            latest_metric(self.database, METRIC_ID),
        )

    def test_no_latest_metrics(self):
        """Test that None is returned for missing metrics."""
        self.database.measurements.find.return_value = []
        self.assertEqual(None, latest_metric(self.database, MetricId("non-existing")))


class MetricsForSubjectTest(unittest.TestCase):
    """Unittest for getting all metrics belonging to a single subject."""

    def setUp(self):
        """Override to create a mock database fixture."""
        self.database = Mock()
        self.database.reports.find_one.return_value = {
            "subjects": {SUBJECT_ID: {"metrics": {METRIC_ID: {}, METRIC_ID2: {}}}}
        }

    def test_metrics_of_subject(self):
        """Test if we get all metric id's in the subject."""
        metric_uuids = metrics_of_subject(self.database, SUBJECT_ID)

        self.assertEqual(len(metric_uuids), 2)
        for m_id in metric_uuids:
            self.assertIn(m_id, [METRIC_ID, METRIC_ID2])
