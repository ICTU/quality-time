"""JMeter CVS tests collector."""

from model import SourceMeasurement, SourceResponses

from .base import JMeterCSVCollector


class JMeterCSVTests(JMeterCSVCollector):
    """Collector for the number of (successful and/or failing) performance test transactions."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the transactions from the responses and return the transactions with the desired status."""
        counts = {"failed": 0, "success": 0}
        async for samples in self._samples(responses):
            label = samples[0]["label"]
            if self._matches_filter(label, "transactions_to_include", "transactions_to_ignore"):
                counts["success"] += self._success_count(samples)
                counts["failed"] += self._error_count(samples)
        value = sum(counts[status] for status in self._parameter("test_result"))
        return SourceMeasurement(value=str(value), total=str(sum(counts.values())))
