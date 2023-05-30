"""Tests shared data"""

from unittest.mock import patch

import mongomock

from shared.database.shared_data import _latest_report, create_measurement, latest_metric, latest_reports
from shared.model.measurement import Measurement
from shared.model.metric import Metric
from shared.utils.type import MetricId
from tests.fixtures import METRIC_ID, METRIC_ID2, REPORT_ID, SOURCE_ID, create_report
from tests.shared.base import DataModelTestCase


class TestSharedData(DataModelTestCase):
    """Test set for shared_data"""

    def setUp(self) -> None:
        """Define info that is used in multiple tests."""

        # Override to create a database fixture.
        super().setUp()

        self.metric = Metric(
            self.DATA_MODEL, dict(type="violations", sources={SOURCE_ID: dict(type="violations")}), "metric_uuid"
        )
        self.measurements = [
            {"_id": 1, "start": "0", "end": "1", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 2, "start": "3", "end": "4", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 3, "start": "6", "end": "7", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 4, "start": "1", "end": "2", "sources": [], "metric_uuid": METRIC_ID2},
            {"_id": 5, "start": "4", "end": "5", "sources": [], "metric_uuid": METRIC_ID2},
            {"_id": 6, "start": "7", "end": "8", "sources": [], "metric_uuid": METRIC_ID2},
        ]

        self.measurement_data = {
            "start": "0",
            "end": "1",
            "sources": [
                dict(
                    type="sonarqube",
                    source_uuid=SOURCE_ID,
                    name="Source",
                    parameters=dict(url="https://url", password="password"),
                )
            ],
            "metric_uuid": METRIC_ID,
            "report_uuid": REPORT_ID,
        }

        self.client = mongomock.MongoClient()
        self.database = self.client["quality_time_db"]

    def test_latest_metrics(self):
        """Test that the latest metrics are returned."""
        self.database["reports"].insert_one(create_report(report_uuid=REPORT_ID))
        self.client["quality_time_db"]["measurements"].insert_one(
            dict(
                _id="id",
                metric_uuid=METRIC_ID,
                status="red",
                sources=[dict(source_uuid=SOURCE_ID, parse_error=None, connection_error=None, value="42")],
            )
        )
        with patch("shared.initialization.database.client", return_value=self.client):
            self.assertEqual(
                Metric(self.DATA_MODEL, dict(tags=[], type="violations"), METRIC_ID),
                latest_metric(REPORT_ID, METRIC_ID),
            )

    def test_no_latest_metrics(self):
        """Test that None is returned for missing metrics."""
        with patch("shared.initialization.database.client", return_value=self.client):
            self.assertIsNone(latest_metric(REPORT_ID, MetricId("non-existing")))

    def test_no_latest_report(self):
        """Test that None is returned for missing metrics."""
        # self.database.reports.find_one.return_value = None
        with patch("shared.initialization.database.client", return_value=self.client):
            self.assertIsNone(latest_metric(REPORT_ID, METRIC_ID))

    def test_create_measurement(self):
        """Test that create measurement is handles by the database"""
        with patch("shared.initialization.database.client", return_value=self.client) as database_client:
            self.database["reports"].insert_one(create_report())
            create_measurement(self.measurement_data)
            database_client.assert_called_with("mongodb://root:root@localhost:27017")

    def test_create_measurement_without_latest_measurement(self):
        """Test that create_measurement without a latest measurement inserts new measurement"""
        with patch("shared.database.shared_data.latest_metric", return_value=self.metric), patch(
            "shared.database.shared_data.Measurement.sources_exist", return_value=True
        ), patch("shared.initialization.database.client", return_value=self.client), patch(
            "shared.database.shared_data.insert_new_measurement"
        ) as insert_new_measurement, patch(
            "shared.database.shared_data.latest_measurement", return_value=False
        ):
            self.database["reports"].insert_one(create_report())
            create_measurement(self.measurement_data)
            insert_new_measurement.assert_called_once()

    def test_create_measurement_with_latest_measurement(self):
        """Test that create_measurement with a latest measurement inserts new measurement"""
        with patch("shared.database.shared_data.latest_metric", return_value=self.metric), patch(
            "shared.database.shared_data.Measurement.sources_exist", return_value=True
        ), patch("shared.initialization.database.client", return_value=self.client), patch(
            "shared.database.shared_data.insert_new_measurement"
        ) as insert_new_measurement, patch(
            "shared.database.shared_data.latest_measurement",
            return_value=Measurement(self.metric, self.measurement_data),
        ):
            self.database["reports"].insert_one(create_report(metric_id=METRIC_ID))
            self.client["quality_time_db"]["measurements"].insert_one(
                dict(
                    _id="id",
                    metric_uuid=METRIC_ID,
                    status="red",
                    sources=[dict(source_uuid=SOURCE_ID, parse_error=None, connection_error=None, value="42")],
                )
            )
            create_measurement(self.measurement_data)
            insert_new_measurement.assert_called_once()

    def test_create_measurement_with_no_latest_metric(self):
        """Test that create_measurement without a latest metric doesn't insert new measurement"""
        with patch("shared.initialization.database.client", return_value=self.client), patch(
            "shared.database.shared_data.insert_new_measurement"
        ) as insert_new_measurement, patch("shared.database.shared_data.latest_metric", return_value=None):
            create_measurement(self.measurement_data)
            insert_new_measurement.assert_not_called()

    def test_create_measurement_without_source(self):
        """Test that create_measurement without a source doesnt insert new measurement"""
        with patch("shared.database.shared_data.latest_metric", return_value=self.metric), patch(
            "shared.database.shared_data.Measurement.sources_exist", return_value=False
        ), patch("shared.initialization.database.client", return_value=self.client), patch(
            "shared.database.shared_data.insert_new_measurement"
        ) as insert_new_measurement:
            self.database["reports"].insert_one(create_report())
            create_measurement(self.measurement_data)
            insert_new_measurement.assert_not_called()

    def test_create_measurement_when_its_equal(self):
        """Test that create_measurement with equal measurement doesn't insert new measurement"""
        with patch("shared.database.shared_data.latest_metric", return_value=self.metric), patch(
            "shared.database.shared_data.Measurement.equals", return_value=True
        ), patch("shared.initialization.database.client", return_value=self.client), patch(
            "shared.database.shared_data.insert_new_measurement"
        ) as insert_new_measurement:
            self.client["quality_time_db"]["measurements"].insert_one(
                dict(
                    _id="id",
                    metric_uuid=METRIC_ID,
                    status="red",
                    sources=[dict(source_uuid=SOURCE_ID, parse_error=None, connection_error=None, value="42")],
                )
            )
            self.database["reports"].insert_one(create_report())
            create_measurement(self.measurement_data)
            insert_new_measurement.assert_not_called()

    def test__latest_report(self):
        """Test that _latest_report returns latest report"""
        with patch("shared.initialization.database.client", return_value=self.client):
            self.assertIsNone(_latest_report(REPORT_ID))
            self.database["reports"].insert_one(create_report(report_uuid=REPORT_ID))
            self.assertEqual(_latest_report(REPORT_ID)["report_uuid"], "report_uuid")

    def test_latest_reports(self):
        """Test that latest reports returns list of latest reports"""
        with patch("shared.initialization.database.client", return_value=self.client):
            self.assertFalse(latest_reports())
            self.database["reports"].insert_one(create_report(report_uuid=REPORT_ID))
            self.database["reports"].insert_one(create_report(report_uuid=REPORT_ID, last=False, title="Not last"))
            self.assertEqual(latest_reports()[0]["report_uuid"], "report_uuid")
            self.assertEqual(len(latest_reports()), 1)
