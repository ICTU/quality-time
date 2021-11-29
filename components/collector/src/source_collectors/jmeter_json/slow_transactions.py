"""JMeter JSON slow transactions collector."""

from typing import cast

from base_collectors import JSONFileSourceCollector
from collector_utilities.functions import match_string_or_regular_expression
from model import Entities, Entity, SourceResponses


class TransactionEntity(Entity):
    """Entity representing a JMeter transaction."""

    def is_slow(
        self,
        response_time_to_evaluate: str,
        target_response_time: float,
        transaction_specific_target_response_times: list[str],
    ) -> bool:
        """Return whether the transaction is slow."""
        name, response_time = self["name"], self[response_time_to_evaluate]
        for transaction_specific_target_response_time in transaction_specific_target_response_times:
            re_or_name, target = transaction_specific_target_response_time.rsplit(":", maxsplit=1)
            if match_string_or_regular_expression(name, [re_or_name]) and response_time <= float(target):
                return False
        return bool(response_time > target_response_time)

    def is_to_be_included(self, transactions_to_include: list[str], transactions_to_ignore: list[str]) -> bool:
        """Return whether the transaction should be included."""
        name = self["name"]
        if transactions_to_include and not match_string_or_regular_expression(name, transactions_to_include):
            return False
        return not match_string_or_regular_expression(name, transactions_to_ignore)


class JMeterJSONSlowTransactions(JSONFileSourceCollector):
    """Collector for the number of slow transactions in a JMeter JSON report."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the security warnings from the JSON."""
        transactions_to_include = cast(list[str], self._parameter("transactions_to_include"))
        transactions_to_ignore = cast(list[str], self._parameter("transactions_to_ignore"))
        response_time_to_evaluate = cast(str, self._parameter("response_time_to_evaluate"))
        target_response_time = float(cast(int, self._parameter("target_response_time")))
        transaction_specific_target_response_times = cast(
            list[str], self._parameter("transaction_specific_target_response_times")
        )
        entities = Entities()
        for response in responses:
            json = await response.json(content_type=None)
            transactions = [transaction for key, transaction in json.items() if key != "Total"]
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
