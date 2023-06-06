"""Tests for Metrics"""

import mongomock

from shared.database.metrics import get_metrics_from_reports
from shared.database.shared_data import get_reports
from tests.fixtures import METRIC_ID, SUBJECT_ID, create_report

from ..base import DataModelTestCase

NEW_REPORT = "New Report"


class TestMetrics(DataModelTestCase):
    """Test set for metrics"""

    def setUp(self) -> None:
        """Define info that is used in multiple tests."""
        self.database = mongomock.MongoClient()["quality_time_db"]

    def test_get_metrics_from_reports(self):
        """test that the metrics are returned."""
        report = create_report(NEW_REPORT, metric_id=METRIC_ID)

        self.database["reports"].insert_one(report)
        reports = get_reports(self.database)
        metrics = get_metrics_from_reports(reports)
        assert metrics[METRIC_ID]["name"] == report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["name"]
