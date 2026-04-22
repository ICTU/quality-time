"""Unit tests for the Grafana k6 tests collector."""

from copy import deepcopy
from typing import ClassVar

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class GrafanaK6TestsTest(SourceCollectorTestCase):
    """Unit tests for the Grafana k6 tests collector."""

    METRIC_TYPE = "tests"
    SOURCE_TYPE = "grafana_k6"
    GRAFANA_K6_JSON: ClassVar = {
        "metrics": {
            "http_req_duration": {
                "thresholds": {"p(98)<200": {"ok": False}},
                "type": "trend",
                "contains": "time",
                "values": {"count": 950, "avg": 29.5, "min": 1.7, "med": 8.2, "max": 483.4, "p(98)": 241.1},
            },
            "http_req_failed": {
                "thresholds": {"rate<0.01": {"ok": True}},
                "type": "rate",
                "contains": "default",
                "values": {"rate": 0.0, "passes": 950, "fails": 0},
            },
            "vus": {
                "type": "gauge",
                "contains": "default",
                "values": {"min": 1, "max": 5, "value": 1},
            },
        },
    }

    async def test_empty_json(self):
        """Test that the number of tests is 0 if the JSON is empty."""
        response = await self.collect(get_request_json_return_value={})
        self.assert_measurement(response, value="0", total="0")

    async def test_no_metrics(self):
        """Test that the number of tests is 0 if the JSON has no metrics."""
        response = await self.collect(get_request_json_return_value={"metrics": {}})
        self.assert_measurement(response, value="0", total="0")

    async def test_metrics_without_thresholds_are_ignored(self):
        """Test that metrics without thresholds are not counted as tests."""
        grafana_k6_json = {"metrics": {"vus": deepcopy(self.GRAFANA_K6_JSON["metrics"]["vus"])}}
        response = await self.collect(get_request_json_return_value=grafana_k6_json)
        self.assert_measurement(response, value="0", total="0")

    async def test_default_counts_passed_and_failed(self):
        """Test that by default the collector counts both passed and failed tests."""
        response = await self.collect(get_request_json_return_value=self.GRAFANA_K6_JSON)
        self.assert_measurement(response, value="2", total="2")

    async def test_only_failed(self):
        """Test that only failed tests are counted if requested."""
        self.set_source_parameter("test_result", ["failed"])
        response = await self.collect(get_request_json_return_value=self.GRAFANA_K6_JSON)
        self.assert_measurement(response, value="1", total="2")

    async def test_only_passed(self):
        """Test that only passed tests are counted if requested."""
        self.set_source_parameter("test_result", ["passed"])
        response = await self.collect(get_request_json_return_value=self.GRAFANA_K6_JSON)
        self.assert_measurement(response, value="1", total="2")

    async def test_multiple_thresholds_one_failing_counts_as_failed(self):
        """Test that a metric with multiple thresholds counts as failed if any threshold is not ok."""
        grafana_k6_json = deepcopy(self.GRAFANA_K6_JSON)
        grafana_k6_json["metrics"]["http_req_failed"]["thresholds"] = {
            "rate<0.01": {"ok": True},
            "rate<0.05": {"ok": False},
        }
        self.set_source_parameter("test_result", ["failed"])
        response = await self.collect(get_request_json_return_value=grafana_k6_json)
        self.assert_measurement(response, value="2", total="2")
