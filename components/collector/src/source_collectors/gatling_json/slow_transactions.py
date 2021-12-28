"""Gatling JSON slow transactions collector."""

from typing import cast

from base_collectors import JSONFileSourceCollector
from collector_utilities.type import JSON, JSONDict
from model import Entities

from ..jmeter_json.base import TransactionEntity


class GatlingJSONSlowTransactions(JSONFileSourceCollector):
    """Collector for the number of slow transactions in a Gatling JSON (stats.json) report."""

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
        transactions = [transaction["stats"] for transaction in cast(JSONDict, json).get("contents", {}).values()]
        for transaction in transactions:
            sample_count = transaction["numberOfRequests"]["total"]
            error_count = transaction["numberOfRequests"]["ko"]
            entity = TransactionEntity(
                key=transaction["name"],
                name=transaction["name"],
                sample_count=sample_count,
                error_count=error_count,
                error_percentage=self.__round((float(error_count) / float(sample_count)) * 100),
                mean_response_time=self.__round(transaction["meanResponseTime"]["total"]),
                min_response_time=self.__round(transaction["minResponseTime"]["total"]),
                max_response_time=self.__round(transaction["maxResponseTime"]["total"]),
                percentile_50_response_time=self.__round(transaction["percentiles1"]["total"]),
                percentile_75_response_time=self.__round(transaction["percentiles2"]["total"]),
                percentile_95_response_time=self.__round(transaction["percentiles3"]["total"]),
                percentile_99_response_time=self.__round(transaction["percentiles4"]["total"]),
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
