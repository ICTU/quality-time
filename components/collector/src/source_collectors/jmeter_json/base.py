"""Base classes for JMeter collectos."""

from collector_utilities.functions import match_string_or_regular_expression
from model import Entity


class TransactionEntity(Entity):
    """Entity representing a JMeter transaction."""

    def is_to_be_included(self, transactions_to_include: list[str], transactions_to_ignore: list[str]) -> bool:
        """Return whether the transaction should be included."""
        name = self["name"]
        if transactions_to_include and not match_string_or_regular_expression(name, transactions_to_include):
            return False
        return not match_string_or_regular_expression(name, transactions_to_ignore)

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
