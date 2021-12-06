"""JMeter CSV slow transactions collector."""

import csv
import statistics
from io import StringIO
from typing import AsyncIterator, cast

from base_collectors import CSVFileSourceCollector
from model import Entities, SourceResponses

from ..jmeter_json.base import TransactionEntity


class JMeterCSVSlowTransactions(CSVFileSourceCollector):
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
        async for samples in self.__samples(responses):
            label = samples[0]["label"]
            latencies = [int(sample["Latency"]) for sample in samples]
            entity = TransactionEntity(
                key=label,
                name=label,
                sample_count=(sample_count := len(samples)),
                error_count=(error_count := len([sample for sample in samples if sample["success"] == "false"])),
                error_percentage=self.__round(error_count / sample_count),
                mean_response_time=self.__round(statistics.mean(latencies)),
                median_response_time=self.__round(statistics.median(latencies)),
                min_response_time=self.__round(min(latencies)),
                max_response_time=self.__round(max(latencies)),
                percentile_90_response_time=self.__round(statistics.quantiles(latencies, n=10)[-1]),
            )
            if entity.is_to_be_included(transactions_to_include, transactions_to_ignore) and entity.is_slow(
                response_time_to_evaluate, target_response_time, transaction_specific_target_response_times
            ):
                entities.append(entity)
        return entities

    @classmethod
    async def __samples(cls, responses: SourceResponses) -> AsyncIterator[list[dict[str, str]]]:
        """Yield the samples grouped by label."""
        rows = await cls.__parse_csv(responses)
        samples = [row for row in rows if not row["responseMessage"].startswith("Number of samples in transaction")]
        labels = sorted(list(set(sample["label"] for sample in samples)))
        for label in labels:
            yield [sample for sample in samples if sample["label"] == label]

    @staticmethod
    async def __parse_csv(responses: SourceResponses) -> list[dict[str, str]]:
        """Parse the CSV rows from the responses."""
        rows = []
        for response in responses:
            csv_text = await response.text()
            rows.extend(list(csv.DictReader(StringIO(csv_text.strip(), newline=""))))
        return rows

    @staticmethod
    def __round(value: float | int) -> float:
        """Round the value at exactly one decimal."""
        return round(float(value), 1)
