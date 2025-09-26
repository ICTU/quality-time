"""Unit tests for the Gatling slow transactions collector."""

from .base import GatlingTestCase


class GatlingSlowTransactionsTest(GatlingTestCase):
    """Unit tests for the Gatling slow transactions collector."""

    METRIC_TYPE = "slow_transactions"

    def setUp(self):
        """Extend to set the expected entities."""
        super().setUp()
        self.expected_entities = [
            {
                "key": self.TRANSACTION1,
                "name": self.TRANSACTION1,
                "sample_count": "1",
                "error_count": "0",
                "error_percentage": "0",
                "mean_response_time": "317",
                "min_response_time": "317",
                "max_response_time": "317",
                "percentile_50_response_time": "317",
                "percentile_75_response_time": "317",
                "percentile_95_response_time": "317",
                "percentile_99_response_time": "317",
            },
            {
                "key": self.TRANSACTION2,
                "name": self.TRANSACTION2,
                "sample_count": "2520",
                "error_count": "4",
                "error_percentage": str(round((4.0 / 2520) * 100)),
                "mean_response_time": "10",
                "min_response_time": "6",
                "max_response_time": "756",
                "percentile_50_response_time": "8",
                "percentile_75_response_time": "9",
                "percentile_95_response_time": "13",
                "percentile_99_response_time": "24",
            },
        ]
        self.set_source_parameter("target_response_time", "20")

    async def test_no_transactions(self):
        """Test that the number of slow transactions is 0 if there are no transactions in the JSON."""
        response = await self.collect(get_request_text="<div/>")
        self.assert_measurement(response, value="0")

    async def test_all_transactions(self):
        """Test retrieving all slow transactions."""
        response = await self.collect(get_request_text=self.GATLING_STATS_HTML)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:1])

    async def test_ignore_transaction(self):
        """Test that a transaction can be ignored."""
        self.set_source_parameter("transactions_to_ignore", [self.TRANSACTION2])
        response = await self.collect(get_request_text=self.GATLING_STATS_HTML)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:1])

    async def test_include_transaction(self):
        """Test that a transaction can be included."""
        self.set_source_parameter("transactions_to_include", [self.TRANSACTION1])
        response = await self.collect(get_request_text=self.GATLING_STATS_HTML)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:1])

    async def test_evaluate_different_response_time(self):
        """Test that a different response time type can be evaluated against the target response time."""
        self.set_source_parameter("response_time_to_evaluate", "min_response_time")
        self.set_source_parameter("target_response_time", "317")
        response = await self.collect(get_request_text=self.GATLING_STATS_HTML)
        self.assert_measurement(response, value="0")
        self.set_source_parameter("target_response_time", "7")
        response = await self.collect(get_request_text=self.GATLING_STATS_HTML)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:1])
        self.set_source_parameter("target_response_time", "5")
        response = await self.collect(get_request_text=self.GATLING_STATS_HTML)
        self.assert_measurement(response, value="2", entities=self.expected_entities)

    async def test_transaction_specific_response_time_target(self):
        """Test that a transaction specific target response time can be set."""
        self.set_source_parameter("transaction_specific_target_response_times", ["[Tt]ransaction 1:400"])
        response = await self.collect(get_request_text=self.GATLING_STATS_HTML)
        self.assert_measurement(response, value="0")
        self.set_source_parameter("transaction_specific_target_response_times", ["[Tt]ransaction 1:400", ".*2:5"])
        response = await self.collect(get_request_text=self.GATLING_STATS_HTML)
        self.assert_measurement(response, value="1", entities=self.expected_entities[1:])
