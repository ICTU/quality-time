"""JMeter JSON tests collector."""

from base_collectors import JSONFileSourceCollector
from model import SourceMeasurement, SourceResponses


class JMeterJSONTests(JSONFileSourceCollector):
    """Collector for the number of (successful and/or failing) performance test transactions."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the transactions from the responses and return the transactions with the desired status."""
        counts = {"failed": 0, "success": 0}
        for response in responses:
            json = await response.json(content_type=None)
            transactions = [transaction for key, transaction in json.items() if key != "Total"]
            for transaction in transactions:
                name = transaction["transaction"]
                if self._matches_filter(name, "transactions_to_include", "transactions_to_ignore"):
                    sample_count = transaction["sampleCount"]
                    error_count = transaction["errorCount"]
                    counts["success"] += sample_count - error_count
                    counts["failed"] += error_count
        value = sum(counts[status] for status in self._parameter("test_result"))
        return SourceMeasurement(value=str(value), total=str(sum(counts.values())))
