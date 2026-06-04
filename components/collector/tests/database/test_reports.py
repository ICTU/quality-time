"""Tests for the reports collection."""

import unittest
from typing import cast

import mongomock

from shared.model.metric import Metric
from shared.utils.type import MetricId

from database.reports import latest_metric

from shared_test_code.fixtures import METRIC_ID, REPORT_ID, SOURCE_ID

from tests.fixtures import create_report


class TestLatestMetric(unittest.TestCase):
    """Unit tests for the latest metric."""

    def setUp(self) -> None:
        """Extend to create a database fixture."""
        self.client: mongomock.MongoClient = mongomock.MongoClient()
        self.database = self.client["quality_time_db"]

    def test_latest_metric(self):
        """Test that the latest metric is returned."""
        self.database["reports"].insert_one(create_report(report_uuid=REPORT_ID))
        self.database["measurements"].insert_one(
            {
                "_id": "id",
                "metric_uuid": METRIC_ID,
                "status": "red",
                "sources": [{"source_uuid": SOURCE_ID, "parse_error": None, "connection_error": None, "value": "42"}],
            },
        )
        self.assertEqual(
            Metric({}, {"tags": [], "type": "violations"}, METRIC_ID),
            latest_metric(self.database, REPORT_ID, METRIC_ID),
        )

    def test_no_latest_metric(self):
        """Test that None is returned for missing metrics."""
        self.assertIsNone(latest_metric(self.database, REPORT_ID, cast(MetricId, "non-existing")))

    def test_no_latest_report(self):
        """Test that None is returned for missing metrics."""
        self.assertIsNone(latest_metric(self.database, REPORT_ID, METRIC_ID))
