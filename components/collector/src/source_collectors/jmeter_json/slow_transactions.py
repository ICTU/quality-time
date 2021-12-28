"""JMeter JSON slow transactions collector."""

from typing import cast

from base_collectors import JSONFileSourceCollector
from collector_utilities.type import JSON, JSONDict
from model import Entities

from .base import TransactionEntity


class JMeterJSONSlowTransactions(JSONFileSourceCollector):
    """Collector for the number of slow transactions in a JMeter JSON report."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the transactions from the JSON."""
        transactions_to_include = cast(list[str], self._parameter("transactions_to_include"))
        transactions_to_ignore = cast(list[str], self._parameter("transactions_to_ignore"))
        response_time_to_evaluate = cast(str, self._parameter("response_time_to_evaluate"))
        target_response_time = float(cast(int, self._parameter("target_response_time")))
        transaction_specific_target_response_times = cast(
            list[str], self._parameter("transaction_specific_target_response_times")
        )
        entities = Entities()
        transactions = [transaction for key, transaction in cast(JSONDict, json).items() if key != "Total"]
        for transaction in transactions:
            entity = TransactionEntity(
                key=transaction["transaction"],
                name=transaction["transaction"],
                sample_count=transaction["sampleCount"],
                error_count=transaction["errorCount"],
                error_percentage=self.__round(transaction["errorPct"]),
                mean_response_time=self.__round(transaction["meanResTime"]),
                median_response_time=self.__round(transaction["medianResTime"]),
                min_response_time=self.__round(transaction["minResTime"]),
                max_response_time=self.__round(transaction["maxResTime"]),
                percentile_90_response_time=self.__round(transaction["pct1ResTime"]),
                percentile_95_response_time=self.__round(transaction["pct2ResTime"]),
                percentile_99_response_time=self.__round(transaction["pct3ResTime"]),
            )
            if entity.is_to_be_included(transactions_to_include, transactions_to_ignore) and entity.is_slow(
                response_time_to_evaluate, target_response_time, transaction_specific_target_response_times
            ):
                entities.append(entity)
        return entities

    @staticmethod
    def __round(value: float | int) -> float:
        """Round the value to exactly one decimal."""
        return round(float(value), 1)
