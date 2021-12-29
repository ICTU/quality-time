"""JMeter CSV slow transactions collector."""

import statistics

from base_collectors import SlowTransactionsCollector, TransactionEntity
from model import Entities, SourceResponses

from .base import JMeterCSVCollector


class JMeterCSVSlowTransactions(JMeterCSVCollector, SlowTransactionsCollector):
    """Collector for the number of slow transactions in a JMeter CSV report."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the security warnings from the CSV."""
        entities = Entities()
        async for samples in self._samples(responses):
            label = samples[0]["label"]
            sample_count = len(samples)
            error_count = self._error_count(samples)
            latencies = [int(sample["elapsed"]) for sample in samples]
            entity = TransactionEntity(
                key=label,
                name=label,
                sample_count=sample_count,
                error_count=error_count,
                error_percentage=self._round((error_count / sample_count) * 100),
                mean_response_time=self._round(statistics.mean(latencies)),
                median_response_time=self._round(statistics.median(latencies)),
                min_response_time=self._round(min(latencies)),
                max_response_time=self._round(max(latencies)),
                percentile_90_response_time=self._round(statistics.quantiles(latencies, n=10)[-1]),
                percentile_95_response_time=self._round(statistics.quantiles(latencies, n=20)[-1]),
                percentile_99_response_time=self._round(statistics.quantiles(latencies, n=100)[-1]),
            )
            if self._is_to_be_included_and_is_slow(entity):
                entities.append(entity)
        return entities
