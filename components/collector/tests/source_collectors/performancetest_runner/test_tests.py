"""Unit tests for the Performancetest-runner tests collector."""

from .base import PerformanceTestRunnerTestCase


class PerformanceTestRunnerTestsTest(PerformanceTestRunnerTestCase):
    """Unit tests for the Performancetest-runner tests collector."""

    METRIC_TYPE = "tests"
    HTML = """
<html>
    <table id="responsetimestable_begin">
        <tr class="transaction"><td class="name">T1</td><td>7</td><td/><td/><td/><td/><td/><td>3</td></tr>
        <tr class="transaction"><td class="name">T2</td><td>13</td><td/><td/><td/><td/><td/><td>5</td></tr>
    </table>
</html>"""

    async def test_tests(self):
        """Test that the number of performance test transactions is returned."""
        response = await self.collect(self.metric, get_request_text=self.HTML)
        self.assert_measurement(response, value="28", total="28")

    async def test_failed_tests(self):
        """Test that the number of failed performance test transactions is returned."""
        # We also pass an obsolete status ("canceled") to test that obsolete statuses are ignored:
        self.set_source_parameter("test_result", ["failed", "canceled"])
        response = await self.collect(self.metric, get_request_text=self.HTML)
        self.assert_measurement(response, value="8", total="28")

    async def test_succeeded_tests(self):
        """Test that the number of succeeded performance test transactions is returned."""
        self.set_source_parameter("test_result", ["success"])
        response = await self.collect(self.metric, get_request_text=self.HTML)
        self.assert_measurement(response, value="20", total="28")

    async def test_ignored_tests(self):
        """Test that the number of performance test transactions is returned for transactions that are not ignored."""
        self.set_source_parameter("transactions_to_ignore", [".*2"])
        response = await self.collect(self.metric, get_request_text=self.HTML)
        self.assert_measurement(response, value="10", total="10")

    async def test_failed_and_ignored_tests(self):
        """Test that the number of not ignored failed performance test transactions is returned."""
        self.set_source_parameter("transactions_to_ignore", [".*2"])
        self.set_source_parameter("test_result", ["failed"])
        response = await self.collect(self.metric, get_request_text=self.HTML)
        self.assert_measurement(response, value="3", total="10")

    async def test_included_tests(self):
        """Test that the number of performance test transactions is returned for transactions that are included."""
        self.set_source_parameter("transactions_to_include", ["T1"])
        response = await self.collect(self.metric, get_request_text=self.HTML)
        self.assert_measurement(response, value="10", total="10")
