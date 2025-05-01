"""Grafana k6 slow transactions collector."""

from typing import Literal, NotRequired, cast

from typing_extensions import TypedDict

from base_collectors import JSONFileSourceCollector
from collector_utilities.type import JSON, JSONDict
from model import Entities, Entity


class ThresholdEvaluation(TypedDict):
    """Class representing a Grafana k6 threshold evaluation."""

    ok: bool


class Values(TypedDict, extra_items=float):  # type: ignore[call-arg]
    """Class representing the values of a Grafana k6 metric, if metric.contains == "time"."""

    # Note that in addition to the values below, the metric values may also include other values such as p95, p99, etc.
    # Since these can be defined by the user of Grafana k6 we can't list them exhaustively, but need to allow for
    # extra items. Unfortunately, typing.TypedDict does not support extra items yet, so we use
    # typing_extensions.TypedDict instead. mypy does not support extra items yet either, so we also need to
    # suppress the mypy errors.

    count: int
    avg: float
    min: float
    med: float
    max: float


class Metric(TypedDict):
    """Class representing a Grafana k6 metric.

    See https://grafana.com/docs/k6/latest/results-output/end-of-test/custom-summary/#metric-schema.
    """

    contains: Literal["data", "default", "time"]
    thresholds: NotRequired[dict[str, ThresholdEvaluation]]
    values: Values


class GrafanaK6SlowTransactions(JSONFileSourceCollector):
    """Collector for the number of slow transactions in a Grafana k6 JSON (summary.json) report."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the transactions from the JSON."""
        entities = Entities()
        metrics = cast(JSONDict, json).get("metrics", {})
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
