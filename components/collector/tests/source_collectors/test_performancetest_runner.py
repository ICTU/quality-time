"""Unit tests for the Performancetest-runner source."""

from datetime import datetime

from collector_utilities.functions import days_ago
from .source_collector_test_case import SourceCollectorTestCase


class PerformanceTestRunnerTestCase(SourceCollectorTestCase):
    """Base class for testing the Performancetest-runner collectors."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="performancetest_runner", parameters=dict(url="report.html")))


class PerformanceTestRunnerSlowTransactionsTest(PerformanceTestRunnerTestCase):
    """Unit tests for the performancetest-runner slow transaction collector."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="slow_transactions", sources=self.sources, addition="sum")

    async def test_no_transactions(self):
        """Test that the number of slow transactions is 0 if there are no transactions in the details table."""
        html = '<html><table class="details"><tr></tr></table></html>'
        response = await self.collect(self.metric, get_request_text=html)
        self.assert_measurement(response, value="0")

    async def test_one_slow_transaction(self):
        """Test that the number of slow transactions is 1 if there is 1 slow transactions in the details table."""
        html = '<html><table class="details"><tr class="transaction"><td class="name">Name</td>' \
               '<td class="red evaluated"/></tr></table></html>'
        response = await self.collect(self.metric, get_request_text=html)
        self.assert_measurement(response, value="1")

    async def test_ignore_fast_transactions(self):
        """Test that fast transactions are not counted."""
        html = '<html><table class="details"><tr class="transaction"><td class="name">Name</td>' \
               '<td class="red evaluated"/></tr><tr class="transaction"><td class="green evaluated"/></tr></table>' \
               '</html>'
        response = await self.collect(self.metric, get_request_text=html)
        self.assert_measurement(response, value="1")

    async def test_warning_only(self):
        """Test that only transactions that exceed the warning threshold are counted."""
        html = '<html><table class="details"><tr class="transaction"><td class="red evaluated"/>' \
            '</tr><tr class="transaction"><td class="name">Name</td><td class="yellow evaluated"/></tr>' \
            '<tr class="transaction"><td class="green evaluated"/></tr></table></html>'
        self.sources["source_id"]["parameters"]["thresholds"] = ["warning"]
        response = await self.collect(self.metric, get_request_text=html)
        self.assert_measurement(response, value="1", entities=[dict(key="Name", name="Name", threshold="warning")])


class PerformanceTestRunnerSourceUpToDatenessTest(PerformanceTestRunnerTestCase):
    """Unit tests for the performancetest-runner source up-to-dateness collector."""

    async def test_source_up_to_dateness(self):
        """Test that the test age is returned."""
        html = '<html><table class="config"><tr><td class="name">Start of the test</td>' \
            '<td id="start_of_the_test">2019.06.22.06.23.00</td></tr></table></html>'
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="max")
        response = await self.collect(metric, get_request_text=html)
        expected_age = days_ago(datetime(2019, 6, 22, 6, 23, 0))
        self.assert_measurement(response, value=str(expected_age))


class PerformanceTestRunnerDurationTest(PerformanceTestRunnerTestCase):
    """Unit tests for the performancetest-runner duration collector."""

    async def test_duration(self):
        """Test that the test duration is returned."""
        html = '<html><table class="config"><tr><td class="name">Duration</td>' \
            '<td id="duration">00:35:00</td></tr></table></html>'
        metric = dict(type="performancetest_duration", sources=self.sources, addition="min")
        response = await self.collect(metric, get_request_text=html)
        self.assert_measurement(response, value="35")


class PerformanceTestRunnerTestsTest(PerformanceTestRunnerTestCase):
    """Unit tests for the performancetest-runner tests collector."""

    async def test_tests(self):
        """Test that the number of performancetest transactions is returned."""
        html = '<html><table class="config">' \
            '<tr><td class="name">Success</td><td id="success">670</td></tr>' \
            '<tr><td class="name">Failed</td><td id="failed">37</td></tr>' \
            '<tr><td class="name">Canceled</td><td id="canceled">5</td></tr></table></html>'
        metric = dict(type="tests", sources=self.sources, addition="sum")
        response = await self.collect(metric, get_request_text=html)
        self.assert_measurement(response, value="712")

    async def test_failed_tests(self):
        """Test that the number of failed performancetest transactions is returned."""
        html = '<html><table class="config">' \
            '<tr><td class="name">Failed</td><td id="failed">37</td></tr>' \
            '<tr><td class="name">Canceled</td><td id="canceled">5</td></tr></table></html>'
        self.sources["source_id"]["parameters"]["test_result"] = ["failed", "canceled"]
        metric = dict(type="tests", sources=self.sources, addition="sum")
        response = await self.collect(metric, get_request_text=html)
        self.assert_measurement(response, value="42")


class PerformanceTestRunnerStabilityTest(PerformanceTestRunnerTestCase):
    """Unit tests for the performancetest-runner performance test stability collector."""

    async def test_stability(self):
        """Test that the percentage of the duration of the performancetest at which the test becomes unstable is
        returned."""
        html = '''<html><table class="config">
            <tr><td class="name">Trendbreak 'stability' (%)</td><td id="trendbreak_stability">90</td></tr>
            </table></html>'''
        metric = dict(type="performancetest_stability", sources=self.sources, addition="min")
        response = await self.collect(metric, get_request_text=html)
        self.assert_measurement(response, value="90")


class PerformanceTestRunnerScalabilityTest(PerformanceTestRunnerTestCase):
    """Unit tests for the performancetest-runner performance test scalability collector."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="scalability", sources=self.sources, addition="min")

    async def test_scalability(self):
        """Test that the percentage of the max users of the performancetest at which the ramp-up of throughput breaks is
        returned."""
        html = '''<html><table class="config">
            <tr><td class="name">Trendbreak 'scalability' (%)</td><td id="trendbreak_scalability">74</td></tr>
            </table></html>'''
        response = await self.collect(self.metric, get_request_text=html)
        self.assert_measurement(response, value="74")

    async def test_scalability_without_breaking_point(self):
        """Test that if the percentage of the max users of the performancetest at which the ramp-up of throughput breaks
        is 100%, the metric reports an error (since there is no breaking point)."""
        html = '''<html><table class="config">
            <tr><td class="name">Trendbreak 'scalability' (%)</td><td id="trendbreak_scalability">100</td></tr>
            </table></html>'''
        response = await self.collect(self.metric, get_request_text=html)
        self.assert_measurement(response, value=None, parse_error="Traceback")
