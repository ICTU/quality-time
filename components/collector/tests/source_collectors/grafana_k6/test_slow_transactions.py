"""Unit tests for the Grafana k6 slow transactions collector."""

from copy import deepcopy
from typing import ClassVar

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class GrafanaK6SlowTransactionsTest(SourceCollectorTestCase):
    """Unit tests for the Grafana k6 slow transactions collector."""

    METRIC_TYPE = "slow_transactions"
    SOURCE_TYPE = "grafana_k6"
    GRAFANA_K6_JSON: ClassVar = {
        "metrics": {
            "http_req_duration": {
                "thresholds": {"p(98)<200": {"ok": False}},
                "type": "trend",
                "contains": "time",
                "values": {
                    "count": 950,
                    "avg": 29.550348787368417,
                    "min": 1.716026,
                    "med": 8.16256,
                    "max": 483.387151,
                    "p(98)": 241.06767703999992,
                },
            },
        },
    }
    EXPECTED_ENTITIES: ClassVar = [
        {
            "key": "http_req_duration",
            "name": "http_req_duration",
            "count": "950",
            "average_response_time": "29.550348787368417",
            "median_response_time": "8.16256",
            "max_response_time": "483.387151",
            "min_response_time": "1.716026",
            "thresholds": "Expected p(98)<200 but got 241",
        }
    ]

    async def test_empty_json(self):
        """Test that the number of slow transactions is 0 if the JSON is empty."""
        response = await self.collect(get_request_json_return_value={})
        self.assert_measurement(response, value="0")

    async def test_no_metrics(self):
        """Test that the number of slow transactions is 0 if the JSON has no metrics."""
        response = await self.collect(get_request_json_return_value={"metrics": {}})
        self.assert_measurement(response, value="0")

    async def test_one_metric_that_is_ok(self):
        """Test that the number of slow transactions is 0 if the JSON has one metric that is ok."""
        grafana_k6_json = deepcopy(self.GRAFANA_K6_JSON)
        grafana_k6_json["metrics"]["http_req_duration"]["thresholds"] = {"p(98)<1000": {"ok": True}}
        response = await self.collect(get_request_json_return_value=grafana_k6_json)
        self.assert_measurement(response, value="0")

    async def test_one_metric_that_is_not_ok(self):
        """Test that the number of slow transactions is 1 if the JSON has one metric that is not ok."""
        response = await self.collect(get_request_json_return_value=self.GRAFANA_K6_JSON)
        self.assert_measurement(response, value="1", entities=self.EXPECTED_ENTITIES)

    async def test_two_metrics_one_ok_one_not_ok(self):
        """Test that the number of slow transactions is 1 if the JSON has two metrics, one of which is not ok."""
        grafana_k6_json = deepcopy(self.GRAFANA_K6_JSON)
        grafana_k6_json["metrics"]["http_req_duration2"] = deepcopy(grafana_k6_json["metrics"]["http_req_duration"])
        grafana_k6_json["metrics"]["http_req_duration2"]["thresholds"] = {"p(98)<1000": {"ok": True}}
        response = await self.collect(get_request_json_return_value=grafana_k6_json)
        self.assert_measurement(response, value="1", entities=self.EXPECTED_ENTITIES)
