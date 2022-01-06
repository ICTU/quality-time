"""Test the Metric model."""

import unittest

from shared.model.metric import Metric
from shared.model.measurement import Measurement
from shared.utils.functions import iso_timestamp

from tests.fixtures import METRIC_ID


class MetricTest(unittest.TestCase):
    """Test the Metric model."""

    DATA_MODEL = {"metrics": {"fixture_metric_type": {}}}

    def test_summarize_empty_metric(self):
        """Test that a minimal metric returns a summary."""
        metric = Metric(self.DATA_MODEL, {"type": "fixture_metric_type"}, METRIC_ID)

        result = metric.summarize([])
        self.assertDictEqual(
            result,
            {
                "type": "fixture_metric_type",
                "scale": "count",
                "status": None,
                "status_start": None,
                "latest_measurement": None,
                "recent_measurements": [],
            },
        )

    def test_summarize_measurements(self):
        """Test that a minimal metric returns a summary."""
        metric = Metric(self.DATA_MODEL, {"type": "fixture_metric_type"}, METRIC_ID)

        measurement_timestamp = iso_timestamp()
        measurement = Measurement(metric, count={"value": 1, "start": measurement_timestamp})
        self.maxDiff = None

        result = metric.summarize([measurement])
        self.assertDictEqual(
            result,
            {
                "issue_status": [],
                "type": "fixture_metric_type",
                "scale": "count",
                "status": None,
                "status_start": None,
                "latest_measurement": {
                    "count": {"value": 1, "start": measurement_timestamp},
                    "end": measurement_timestamp,
                    "sources": [],
                    "start": measurement_timestamp,
                },
                "recent_measurements": [
                    {
                        "count": {"status": None, "value": 1},
                        "end": measurement_timestamp,
                        "start": measurement_timestamp,
                    }
                ],
            },
        )

    def test_summarize_metric_data(self):
        """Test that metric data is summarized."""
        metric = Metric(
            self.DATA_MODEL, {"type": "fixture_metric_type", "some_metric_property": "some_value"}, METRIC_ID
        )

        result = metric.summarize([])
        self.assertDictEqual(
            result,
            {
                "type": "fixture_metric_type",
                "scale": "count",
                "status": None,
                "status_start": None,
                "latest_measurement": None,
                "recent_measurements": [],
                "some_metric_property": "some_value",
            },
        )

    def test_summarize_metric_kwargs(self):
        """Test that metric data is summarized."""
        metric = Metric(self.DATA_MODEL, {"type": "fixture_metric_type"}, METRIC_ID)

        result = metric.summarize([], some_kw="some_arg")
        self.assertDictEqual(
            result,
            {
                "type": "fixture_metric_type",
                "scale": "count",
                "status": None,
                "status_start": None,
                "latest_measurement": None,
                "recent_measurements": [],
                "some_kw": "some_arg",
            },
        )
