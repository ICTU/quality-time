"""Grafana k6 slow transactions collector."""

from typing import cast

from base_collectors import JSONFileSourceCollector
from collector_utilities.type import JSON
from model import Entities, Entity

from .base import Metric, SummaryJSON


class GrafanaK6SlowTransactions(JSONFileSourceCollector):
    """Collector for the number of slow transactions in a Grafana k6 JSON (summary.json) report."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the transactions from the JSON."""
        entities = Entities()
        metrics = cast(SummaryJSON, json).get("metrics", {})
        for metric_key, metric in metrics.items():
            if not self._include_metric(metric):
                continue
            values = metric["values"]
            entity = Entity(
                key=metric_key,
                name=metric_key,
                count=str(values["count"]),
                average_response_time=str(values["avg"]),
                median_response_time=str(values["med"]),
                min_response_time=str(values["min"]),
                max_response_time=str(values["max"]),
                thresholds=self._format_thresholds(metric),
            )
            entities.append(entity)
        return entities

    @staticmethod
    def _include_metric(metric: Metric) -> bool:
        """Return whether the metric should be included in the result."""
        threshold_evaluations = metric.get("thresholds", {}).values()
        return metric["contains"] == "time" and any(not evaluation["ok"] for evaluation in threshold_evaluations)

    @staticmethod
    def _format_thresholds(metric: Metric) -> str:
        """Return a human-readable representation of the thresholds."""
        thresholds = metric.get("thresholds", {})
        result = []
        for threshold in thresholds:
            metric_value_key = threshold.split("<")[0]
            actual_value = metric["values"][metric_value_key]  # type: ignore[literal-required]
            result.append(f"Expected {threshold} but got {round(actual_value)}")
        return ", ".join(result)
