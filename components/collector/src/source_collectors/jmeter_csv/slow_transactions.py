"""JMeter CSV slow transactions collector."""

import statistics
from typing import cast

from model import Entities, SourceResponses

from .base import JMeterCSVCollector
from ..jmeter_json.base import TransactionEntity


class JMeterCSVSlowTransactions(JMeterCSVCollector):
    """Collector for the number of slow transactions in a JMeter CSV report."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the security warnings from the CSV."""
        transactions_to_include = cast(list[str], self._parameter("transactions_to_include"))
        transactions_to_ignore = cast(list[str], self._parameter("transactions_to_ignore"))
        response_time_to_evaluate = cast(str, self._parameter("response_time_to_evaluate"))
        target_response_time = float(cast(int, self._parameter("target_response_time")))
        transaction_specific_target_response_times = cast(
            list[str], self._parameter("transaction_specific_target_response_times")
        )
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
                error_percentage=self.__round((error_count / sample_count) * 100),
                mean_response_time=self.__round(statistics.mean(latencies)),
                median_response_time=self.__round(statistics.median(latencies)),
                min_response_time=self.__round(min(latencies)),
                max_response_time=self.__round(max(latencies)),
                percentile_90_response_time=self.__round(statistics.quantiles(latencies, n=10)[-1]),
                percentile_95_response_time=self.__round(statistics.quantiles(latencies, n=20)[-1]),
                percentile_99_response_time=self.__round(statistics.quantiles(latencies, n=100)[-1]),
            )
            if entity.is_to_be_included(transactions_to_include, transactions_to_ignore) and entity.is_slow(
                response_time_to_evaluate, target_response_time, transaction_specific_target_response_times
            ):
                entities.append(entity)
        return entities

    @staticmethod
    def __round(value: float | int) -> float:
        """Round the value at exactly one decimal."""
        return round(float(value), 1)
