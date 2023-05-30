"""Tests for Metrics"""
from unittest.mock import patch

import mongomock

from shared.database.metrics import get_metrics_from_reports
from shared.database.shared_data import get_reports
from tests.fixtures import METRIC_ID, SUBJECT_ID, create_report

from ..base import DataModelTestCase

PATCH_DB_CLIENT = "shared.initialization.database.client"
NEW_REPORT = "New Report"


class TestMetrics(DataModelTestCase):
    """Test set for metrics"""

    def setUp(self) -> None:
        """Define info that is used in multiple tests."""
        self.client = mongomock.MongoClient()

    def test_get_metrics_from_reports(self):
        """test that the metrics are returned."""
        with patch(PATCH_DB_CLIENT, return_value=self.client):
            report = create_report(NEW_REPORT, metric_id=METRIC_ID)

            self.client["quality_time_db"]["reports"].insert_one(report)
            reports = get_reports()
            metrics = get_metrics_from_reports(reports)
            assert metrics[METRIC_ID]["name"] == report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["name"]
