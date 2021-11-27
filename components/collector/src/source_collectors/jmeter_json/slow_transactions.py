"""JMeter JSON slow transactions collector."""

from base_collectors import JSONFileSourceCollector
from model import Entities, Entity, SourceResponses


class JMeterJSONSlowTransactions(JSONFileSourceCollector):
    """Collector for the number of slow transactions in a JMeter JSON report."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the security warnings from the JSON."""
        entities = Entities()
        for response in responses:
            json = await response.json(content_type=None)
            transactions = [value for key, value in json.items() if key != "Total"]
            for transaction in transactions:
                entities.append(
                    Entity(
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
                )
        return entities

    @staticmethod
    def __round(value: float | int) -> float:
        """Round the value at exactly one decimal."""
        return round(float(value), 1)
