"""Grafana k6 slow transactions collector."""

from typing import cast

from shared_data_model import DATA_MODEL

from base_collectors import JSONFileSourceCollector, SlowTransactionsCollector, TransactionEntity
from collector_utilities.type import JSON
from model import Entities

from .base import Metric, SummaryJSON


def is_default_response_time(response_time_to_evaluate: str) -> bool:
    """Return whether the response time to evaluate is the default type."""
    default_value = DATA_MODEL.sources["grafana_k6"].parameters["response_time_to_evaluate"].default_value
    return response_time_to_evaluate == default_value


class GrafanaK6TransactionEntity(TransactionEntity):
    """Entity for a Grafana k6 transaction."""

    def is_slow(
        self,
        response_time_to_evaluate: str,
        target_response_time: float,
        transaction_specific_target_response_times: list[str],
    ) -> bool:
        """Return whether the transaction is slow."""
        # If the user did not change the response time to evaluate, the thresholds from the summary.json have already
        # been used (in GrafanaK6SlowTransactions._include_metric() below) to determine that this transaction is slow,
        # so return True in that case. Otherwise, evaluate the response time against the target response time.
        return (
            True
            if is_default_response_time(response_time_to_evaluate)
            else super().is_slow(
                response_time_to_evaluate, target_response_time, transaction_specific_target_response_times
            )
        )


class GrafanaK6SlowTransactions(SlowTransactionsCollector, JSONFileSourceCollector):
    """Collector for the number of slow transactions in a Grafana k6 JSON (summary.json) report."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the transactions from the JSON."""
        entities = Entities()
        metrics = cast(SummaryJSON, json).get("metrics", {})
        for metric_key, metric in metrics.items():
            if not self._include_metric(metric):
                continue
            values = metric["values"]
            entity = GrafanaK6TransactionEntity(
                key=metric_key,
                name=metric_key,
                count=str(values["count"]),
                average_response_time=str(values["avg"]),
                median_response_time=str(values["med"]),
                min_response_time=str(values["min"]),
                max_response_time=str(values["max"]),
                thresholds=self._format_thresholds(metric),
            )
            if self._is_to_be_included_and_is_slow(entity):
                entities.append(entity)
        return entities

    def _include_metric(self, metric: Metric) -> bool:
        """Return whether the metric should be included in the result."""
        if not is_default_response_time(self._response_time_to_evaluate):
            return True  # Defer evaluating the slowness to GrafanaK6TransactionEntity.is_slow(), see above.
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
