"""Unit tests for the Gatling tests collector."""

from .base import GatlingTestCase


class GatlingJSONTestsTest(GatlingTestCase):
    """Unit tests for the Gatling tests collector."""

    METRIC_TYPE = "tests"

    async def test_no_transactions(self):
        """Test that the number of tests is 0 if there are no transactions in the JSON."""
        response = await self.collect(get_request_text="<table/>")
        self.assert_measurement(response, value="0")

    async def test_all_samples(self):
        """Test retrieving all samples."""
        response = await self.collect(get_request_text=self.GATLING_STATS_HTML)
        self.assert_measurement(response, value="2521")

    async def test_failed_samples(self):
        """Test retrieving the failed samples."""
        self.set_source_parameter("test_result", ["failed"])
        response = await self.collect(get_request_text=self.GATLING_STATS_HTML)
        self.assert_measurement(response, value="4")

    async def test_successful_samples(self):
        """Test retrieving the successful samples."""
        self.set_source_parameter("test_result", ["success"])
        response = await self.collect(get_request_text=self.GATLING_STATS_HTML)
        self.assert_measurement(response, value="2517")

    async def test_ignore_transaction(self):
        """Test that a transaction can be ignored."""
        self.set_source_parameter("transactions_to_ignore", [self.TRANSACTION2])
        response = await self.collect(get_request_text=self.GATLING_STATS_HTML)
        self.assert_measurement(response, value="1")

    async def test_include_transaction(self):
        """Test that a transaction can be included."""
        self.set_source_parameter("transactions_to_include", [self.TRANSACTION1])
        response = await self.collect(get_request_text=self.GATLING_STATS_HTML)
        self.assert_measurement(response, value="1")
