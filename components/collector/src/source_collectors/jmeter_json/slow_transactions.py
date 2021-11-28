"""JMeter JSON slow transactions collector."""

from base_collectors import JSONFileSourceCollector
from collector_utilities.functions import match_string_or_regular_expression
from model import Entities, Entity, SourceResponses


class JMeterJSONSlowTransactions(JSONFileSourceCollector):
    """Collector for the number of slow transactions in a JMeter JSON report."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the security warnings from the JSON."""
        transactions_to_include = self._parameter("transactions_to_include")
        transactions_to_ignore = self._parameter("transactions_to_ignore")
        response_time_type_to_evaluate = self._parameter("response_time_to_evaluate")
        target_response_time = float(self._parameter("target_response_time"))

        def include(transaction) -> bool:
            """Return whether the transaction should be included."""
            name = transaction["transaction"]
            if transactions_to_include and not match_string_or_regular_expression(name, transactions_to_include):
                return False
            return not match_string_or_regular_expression(name, transactions_to_ignore)

        entities = Entities()
        for response in responses:
            json = await response.json(content_type=None)
            transactions = [transaction for key, transaction in json.items() if key != "Total" and include(transaction)]
            for transaction in transactions:
                entity = Entity(
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
                if entity[response_time_type_to_evaluate] > target_response_time:
                    entities.append(entity)
        return entities

    @staticmethod
    def __round(value: float | int) -> float:
        """Round the value at exactly one decimal."""
        return round(float(value), 1)
