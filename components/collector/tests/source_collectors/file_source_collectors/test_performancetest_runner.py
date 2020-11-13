"""Unit tests for the Performancetest-runner source."""

from datetime import datetime

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase

from collector_utilities.functions import days_ago


class PerformanceTestRunnerTestCase(SourceCollectorTestCase):
    """Base class for testing the Performancetest-runner collectors."""

    def setUp(self):
        """Extend to set up the metric sources."""
        super().setUp()
        self.sources = dict(source_id=dict(type="performancetest_runner", parameters=dict(url="report.html")))


class PerformanceTestRunnerSlowTransactionsTest(PerformanceTestRunnerTestCase):
    """Unit tests for the Performancetest-runner slow transaction collector."""

    def setUp(self):
        """Set up a metric fixture."""
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

    async def test_ignore_transactions_by_name(self):
        """Test that transactions can be ignored by name."""
        html = '<html><table class="details">' \
               '<tr class="transaction"><td class="name">T1</td><td class="red evaluated"/></tr>' \
               '<tr class="transaction"><td class="name">T2</td><td class="yellow evaluated"/></tr>' \
               '<tr class="transaction"><td class="name">T3</td><td class="green evaluated"/></tr>' \
               '</table></html>'
        self.sources["source_id"]["parameters"]["transactions_to_ignore"] = ["T[1|3]"]
        response = await self.collect(self.metric, get_request_text=html)
        self.assert_measurement(response, value="1", entities=[dict(key="T2", name="T2", threshold="warning")])

    async def test_include_transactions_by_name(self):
        """Test that transactions can be included by name."""
        html = '<html><table class="details">' \
               '<tr class="transaction"><td class="name">T1</td><td class="red evaluated"/></tr>' \
               '<tr class="transaction"><td class="name">T2</td><td class="yellow evaluated"/></tr>' \
               '<tr class="transaction"><td class="name">T3</td><td class="green evaluated"/></tr>' \
               '</table></html>'
        self.sources["source_id"]["parameters"]["transactions_to_include"] = ["T2"]
        response = await self.collect(self.metric, get_request_text=html)
        self.assert_measurement(response, value="1", entities=[dict(key="T2", name="T2", threshold="warning")])


class PerformanceTestRunnerSourceUpToDatenessTest(PerformanceTestRunnerTestCase):
    """Unit tests for the Performancetest-runner source up-to-dateness collector."""

    async def test_source_up_to_dateness(self):
        """Test that the test age is returned."""
        html = '<html><table class="config"><tr><td class="name">Start of the test</td>' \
            '<td id="start_of_the_test">2019.06.22.06.23.00</td></tr></table></html>'
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="max")
        response = await self.collect(metric, get_request_text=html)
        expected_age = days_ago(datetime(2019, 6, 22, 6, 23, 0))
        self.assert_measurement(response, value=str(expected_age))


class PerformanceTestRunnerDurationTest(PerformanceTestRunnerTestCase):
    """Unit tests for the Performancetest-runner duration collector."""

    async def test_duration(self):
        """Test that the test duration is returned."""
        html = '<html><table class="config"><tr><td class="name">Duration</td>' \
            '<td id="duration">00:35:00</td></tr></table></html>'
        metric = dict(type="performancetest_duration", sources=self.sources, addition="min")
        response = await self.collect(metric, get_request_text=html)
        self.assert_measurement(response, value="35")


class PerformanceTestRunnerTestsTest(PerformanceTestRunnerTestCase):
    """Unit tests for the Performancetest-runner tests collector."""

    def setUp(self):
        """Prepare a Performancetest-runner HTML-report and the tests metric."""
        super().setUp()
        self.metric = dict(type="tests", sources=self.sources, addition="sum")
        self.html = '''
<html>
    <table id="responsetimestable_begin">
        <tr class="transaction"><td class="name">T1</td><td>7</td><td/><td/><td/><td/><td/><td>3</td></tr>
        <tr class="transaction"><td class="name">T2</td><td>13</td><td/><td/><td/><td/><td/><td>5</td></tr>
    </table>
</html>'''

    async def test_tests(self):
        """Test that the number of performance test transactions is returned."""
        response = await self.collect(self.metric, get_request_text=self.html)
        self.assert_measurement(response, value="28", total="28")

    async def test_failed_tests(self):
        """Test that the number of failed performance test transactions is returned."""
        # We also pass an obsolete status ("canceled") to test that obsolete statuses are ignored:
        self.sources["source_id"]["parameters"]["test_result"] = ["failed", "canceled"]
        response = await self.collect(self.metric, get_request_text=self.html)
        self.assert_measurement(response, value="8", total="28")

    async def test_succeeded_tests(self):
        """Test that the number of succeeded performance test transactions is returned."""
        self.sources["source_id"]["parameters"]["test_result"] = ["success"]
        response = await self.collect(self.metric, get_request_text=self.html)
        self.assert_measurement(response, value="20", total="28")

    async def test_ignored_tests(self):
        """Test that the number of performance test transactions is returned for transactions that are not ignored."""
        self.sources["source_id"]["parameters"]["transactions_to_ignore"] = [".*2"]
        response = await self.collect(self.metric, get_request_text=self.html)
        self.assert_measurement(response, value="10", total="10")

    async def test_failed_and_ignored_tests(self):
        """Test that the number of not ignored failed performance test transactions is returned."""
        self.sources["source_id"]["parameters"]["transactions_to_ignore"] = [".*2"]
        self.sources["source_id"]["parameters"]["test_result"] = ["failed"]
        response = await self.collect(self.metric, get_request_text=self.html)
        self.assert_measurement(response, value="3", total="10")

    async def test_included_tests(self):
        """Test that the number of performance test transactions is returned for transactions that are included."""
        self.sources["source_id"]["parameters"]["transactions_to_include"] = ["T1"]
        response = await self.collect(self.metric, get_request_text=self.html)
        self.assert_measurement(response, value="10", total="10")


class PerformanceTestRunnerStabilityTest(PerformanceTestRunnerTestCase):
    """Unit tests for the Performancetest-runner performance test stability collector."""

    async def test_stability(self):
        """Test that the percentage of the duration at which the performance test becomes unstable is returned."""
        html = '''<html><table class="config">
            <tr><td class="name">Trendbreak 'stability' (%)</td><td id="trendbreak_stability">90</td></tr>
            </table></html>'''
        metric = dict(type="performancetest_stability", sources=self.sources, addition="min")
        response = await self.collect(metric, get_request_text=html)
        self.assert_measurement(response, value="90")


class PerformanceTestRunnerScalabilityTest(PerformanceTestRunnerTestCase):
    """Unit tests for the Performancetest-runner performance test scalability collector."""

    def setUp(self):
        """Set up the scalability metric."""
        super().setUp()
        self.metric = dict(type="scalability", sources=self.sources, addition="min")

    async def test_scalability(self):
        """Test that the percentage of the max users at which the ramp-up of throughput breaks is returned."""
        html = '''<html><table class="config">
            <tr><td class="name">Trendbreak 'scalability' (%)</td><td id="trendbreak_scalability">74</td></tr>
            </table></html>'''
        response = await self.collect(self.metric, get_request_text=html)
        self.assert_measurement(response, value="74")

    async def test_scalability_without_breaking_point(self):
        """Test the scalability without breaking point.

        Test that if the percentage of the max users at which the ramp-up of throughput breaks is 100%, the metric
        reports an error (since there is no breaking point).
        """
        html = '''<html><table class="config">
            <tr><td class="name">Trendbreak 'scalability' (%)</td><td id="trendbreak_scalability">100</td></tr>
            </table></html>'''
        response = await self.collect(self.metric, get_request_text=html)
        self.assert_measurement(response, value=None, parse_error="Traceback")
