"""JMeter JSON slow transactions collector."""

from typing import cast

from base_collectors import JSONFileSourceCollector, SlowTransactionsCollector, TransactionEntity
from collector_utilities.type import JSON, JSONDict
from model import Entities


class JMeterJSONSlowTransactions(SlowTransactionsCollector, JSONFileSourceCollector):
    """Collector for the number of slow transactions in a JMeter JSON report."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the transactions from the JSON."""
        entities = Entities()
        transactions = [transaction for key, transaction in cast(JSONDict, json).items() if key != "Total"]
        for transaction in transactions:
            entity = TransactionEntity(
                key=transaction["transaction"],
                name=transaction["transaction"],
                sample_count=transaction["sampleCount"],
                error_count=transaction["errorCount"],
                error_percentage=self._round(transaction["errorPct"]),
                mean_response_time=self._round(transaction["meanResTime"]),
                median_response_time=self._round(transaction["medianResTime"]),
                min_response_time=self._round(transaction["minResTime"]),
                max_response_time=self._round(transaction["maxResTime"]),
                percentile_90_response_time=self._round(transaction["pct1ResTime"]),
                percentile_95_response_time=self._round(transaction["pct2ResTime"]),
                percentile_99_response_time=self._round(transaction["pct3ResTime"]),
            )
            if self._is_to_be_included_and_is_slow(entity):
                entities.append(entity)
        return entities
