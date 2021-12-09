"""JMeter CVS tests collector."""

from typing import cast

from model import SourceMeasurement, SourceResponses

from .base import JMeterCSVCollector
from ..jmeter_json.base import TransactionEntity


class JMeterCSVTests(JMeterCSVCollector):
    """Collector for the number of (successful and/or failing) performance test transactions."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the transactions from the responses and return the transactions with the desired status."""
        transactions_to_include = cast(list[str], self._parameter("transactions_to_include"))
        transactions_to_ignore = cast(list[str], self._parameter("transactions_to_ignore"))
        counts = dict(failed=0, success=0)
        async for samples in self._samples(responses):
            label = samples[0]["label"]
            entity = TransactionEntity(key=label, name=label)
            if not entity.is_to_be_included(transactions_to_include, transactions_to_ignore):
                continue
            counts["success"] += self._success_count(samples)
            counts["failed"] += self._error_count(samples)
        value = sum(counts[status] for status in self._parameter("test_result"))
        return SourceMeasurement(value=str(value), total=str(sum(counts.values())))
