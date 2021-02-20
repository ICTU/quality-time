"""Unit tests for the Performancetest-runner slow transactions collector."""

from .base import PerformanceTestRunnerTestCase


class PerformanceTestRunnerSlowTransactionsTest(PerformanceTestRunnerTestCase):
    """Unit tests for the Performancetest-runner slow transaction collector."""

    METRIC_TYPE = "slow_transactions"

    async def test_no_transactions(self):
        """Test that the number of slow transactions is 0 if there are no transactions in the details table."""
        html = '<html><table class="details"><tr></tr></table></html>'
        response = await self.collect(get_request_text=html)
        self.assert_measurement(response, value="0")

    async def test_one_slow_transaction(self):
        """Test that the number of slow transactions is 1 if there is 1 slow transactions in the details table."""
        html = (
            '<html><table class="details"><tr class="transaction"><td class="name">Name</td>'
            '<td class="red evaluated"/></tr></table></html>'
        )
        response = await self.collect(get_request_text=html)
        self.assert_measurement(response, value="1")

    async def test_ignore_fast_transactions(self):
        """Test that fast transactions are not counted."""
        html = (
            '<html><table class="details"><tr class="transaction"><td class="name">Name</td>'
            '<td class="red evaluated"/></tr><tr class="transaction"><td class="green evaluated"/></tr></table>'
            "</html>"
        )
        response = await self.collect(get_request_text=html)
        self.assert_measurement(response, value="1")

    async def test_warning_only(self):
        """Test that only transactions that exceed the warning threshold are counted."""
        html = (
            '<html><table class="details"><tr class="transaction"><td class="red evaluated"/>'
            '</tr><tr class="transaction"><td class="name">Name</td><td class="yellow evaluated"/></tr>'
            '<tr class="transaction"><td class="green evaluated"/></tr></table></html>'
        )
        self.set_source_parameter("thresholds", ["warning"])
        response = await self.collect(get_request_text=html)
        self.assert_measurement(response, value="1", entities=[dict(key="Name", name="Name", threshold="warning")])

    async def test_ignore_transactions_by_name(self):
        """Test that transactions can be ignored by name."""
        html = (
            '<html><table class="details">'
            '<tr class="transaction"><td class="name">T1</td><td class="red evaluated"/></tr>'
            '<tr class="transaction"><td class="name">T2</td><td class="yellow evaluated"/></tr>'
            '<tr class="transaction"><td class="name">T3</td><td class="green evaluated"/></tr>'
            "</table></html>"
        )
        self.set_source_parameter("transactions_to_ignore", ["T[1|3]"])
        response = await self.collect(get_request_text=html)
        self.assert_measurement(response, value="1", entities=[dict(key="T2", name="T2", threshold="warning")])

    async def test_include_transactions_by_name(self):
        """Test that transactions can be included by name."""
        html = (
            '<html><table class="details">'
            '<tr class="transaction"><td class="name">T1</td><td class="red evaluated"/></tr>'
            '<tr class="transaction"><td class="name">T2</td><td class="yellow evaluated"/></tr>'
            '<tr class="transaction"><td class="name">T3</td><td class="green evaluated"/></tr>'
            "</table></html>"
        )
        self.set_source_parameter("transactions_to_include", ["T2"])
        response = await self.collect(get_request_text=html)
        self.assert_measurement(response, value="1", entities=[dict(key="T2", name="T2", threshold="warning")])
