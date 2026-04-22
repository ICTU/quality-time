"""Grafana k6 tests collector."""

from typing import cast

from base_collectors import JSONFileSourceCollector
from model import SourceMeasurement, SourceResponses

from .json_types import SummaryJSON


class GrafanaK6Tests(JSONFileSourceCollector):
    """Collector for the number of (passed and/or failed) tests in a Grafana k6 summary.json report."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to count metrics with thresholds as tests."""
        test_results = cast(list[str], self._parameter("test_result"))
        counts = {"failed": 0, "passed": 0}
        for response in responses:
            json = cast(SummaryJSON, await response.json(content_type=None))
            for metric in json.get("metrics", {}).values():
                thresholds = metric.get("thresholds", {})
                if not thresholds:
                    continue
                status = "passed" if all(evaluation["ok"] for evaluation in thresholds.values()) else "failed"
                counts[status] += 1
        value = sum(counts[status] for status in test_results)
        return SourceMeasurement(value=str(value), total=str(sum(counts.values())))
