"""Test the metric model."""

import unittest
from datetime import date
from typing import ClassVar

from shared.model.measurement import Measurement
from shared.model.metric import Metric
from shared.utils.functions import iso_timestamp

from tests.fixtures import METRIC_ID


class MetricTest(unittest.TestCase):
    """Test the metric model."""

    DATA_MODEL: ClassVar[dict] = {
        "metrics": {
            "fixture_metric_type": {"name": "fixture_metric_type", "unit": "issues"},
            "fixture_metric_type_without_name": {"unit": "issues"},
        },
    }

    def create_metric(self, **kwargs) -> Metric:
        """Return a metric fixture."""
        return Metric(self.DATA_MODEL, {"type": "fixture_metric_type", **kwargs}, METRIC_ID)

    def test_summarize_empty_metric(self):
        """Test that a minimal metric returns a summary."""
        summary = self.create_metric().summarize([])
        self.assertDictEqual(
            summary,
            {
                "type": "fixture_metric_type",
                "scale": "count",
                "status": None,
                "status_start": None,
                "latest_measurement": None,
                "recent_measurements": [],
                "sources": {},
            },
        )

    def test_summarize_measurements(self):
        """Test that a minimal metric returns a summary."""
        metric = self.create_metric()
        measurement_timestamp = iso_timestamp()
        measurement = Measurement(
            metric,
            count={"value": 1, "start": measurement_timestamp},
            status="target_met",
        )
        summary = metric.summarize([measurement])
        self.assertDictEqual(
            summary,
            {
                "issue_status": [],
                "type": "fixture_metric_type",
                "scale": "count",
                "status": "target_met",
                "status_start": None,
                "latest_measurement": {
                    "count": {"value": 1, "start": measurement_timestamp},
                    "end": measurement_timestamp,
                    "sources": [],
                    "start": measurement_timestamp,
                    "status": "target_met",
                },
                "recent_measurements": [
                    {
                        "count": {"status": "target_met", "value": 1},
                        "end": measurement_timestamp,
                        "start": measurement_timestamp,
                    },
                ],
                "sources": {},
            },
        )

    def test_summarize_metric_data(self):
        """Test that metric data is summarized."""
        summary = self.create_metric(some_metric_property="some_value").summarize([])
        self.assertDictEqual(
            summary,
            {
                "type": "fixture_metric_type",
                "scale": "count",
                "status": None,
                "status_start": None,
                "latest_measurement": None,
                "recent_measurements": [],
                "some_metric_property": "some_value",
                "sources": {},
            },
        )

    def test_summarize_metric_kwargs(self):
        """Test that metric data is summarized."""
        summary = self.create_metric().summarize([], some_kw="some_arg")
        self.assertDictEqual(
            summary,
            {
                "type": "fixture_metric_type",
                "scale": "count",
                "status": None,
                "status_start": None,
                "latest_measurement": None,
                "recent_measurements": [],
                "some_kw": "some_arg",
                "sources": {},
            },
        )

    def test_debt_end_date(self):
        """Test debt end date."""
        metric = self.create_metric()
        self.assertEqual(metric.debt_end_date(), date.max.isoformat())
        metric["debt_end_date"] = ""
        self.assertEqual(metric.debt_end_date(), date.max.isoformat())
        metric["debt_end_date"] = "some date"
        self.assertEqual(metric.debt_end_date(), "some date")

    def test_name(self):
        """Test that we get the metric name from the metric."""
        self.assertEqual("name", self.create_metric(name="name").name)

    def test_missing_name(self):
        """Test that we get the metric name from the data model if the metric has no name."""
        self.assertEqual("fixture_metric_type", self.create_metric().name)

    def test_missing_default_name(self):
        """Test that the metric name is None if neither metric nor data model have a name for the metric."""
        self.assertIsNone(self.create_metric(type="fixture_metric_type_without_name").name)

    def test_unit(self):
        """Test that we get the metric unit from the metric."""
        self.assertEqual("oopsies", self.create_metric(unit="oopsies").unit)

    def test_missing_unit(self):
        """Test that we get the metric unit from the data model if the metric has no unit."""
        self.assertEqual("issues", self.create_metric().unit)

    def test_equal(self):
        """Test that a metric is equal to itself."""
        self.assertEqual(self.create_metric(), self.create_metric())

    def test_not_equal(self):
        """Test that a metric is not equal to a metric with another type."""
        self.assertEqual(self.create_metric(type="size"), self.create_metric(type="violations"))

    def test_not_equal_to_string(self):
        """Test that a metric is not equal to a string."""
        self.assertNotEqual(self.create_metric(), "foo")
