"""Unit tests for the Performancetest-runner source."""

from datetime import datetime
import unittest
from unittest.mock import Mock, patch

from metric_collectors import MetricCollector
from utilities.functions import days_ago


class PerformanceTestRunnerTest(unittest.TestCase):
    """Unit tests for the Performancetest-runner metrics."""

    def setUp(self):
        self.mock_response = Mock()
        self.sources = dict(source_id=dict(type="performancetest_runner", parameters=dict(url="report.html")))
        self.datamodel = dict(
            sources=dict(
                performancetest_runner=dict(
                    parameters=dict(
                        failure_type=dict(values=["canceled", "failed"]),
                        thresholds=dict(values=["high", "warning"])))))

    def test_no_transactions(self):
        """Test that the number of slow transactions is 0 if there are no transactions in the details table."""
        self.mock_response.text = '<html><table class="details"><tr></tr></table></html>'
        metric = dict(type="slow_transactions", sources=self.sources, addition="sum")
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric, self.datamodel).get()
        self.assertEqual("0", response["sources"][0]["value"])

    def test_one_slow_transaction(self):
        """Test that the number of slow transactions is 1 if there is 1 slow transactions in the details table."""
        self.mock_response.text = '<html><table class="details"><tr class="transaction"><td class="red evaluated"/>' \
            '</tr></table></html>'
        metric = dict(type="slow_transactions", sources=self.sources, addition="sum")
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric, self.datamodel).get()
        self.assertEqual("1", response["sources"][0]["value"])

    def test_ignore_fast_transactions(self):
        """Test that fast transactions are not counted."""
        self.mock_response.text = '<html><table class="details"><tr class="transaction"><td class="red evaluated"/>' \
            '</tr><tr class="transaction"><td class="green evaluated"/></tr></table></html>'
        metric = dict(type="slow_transactions", sources=self.sources, addition="sum")
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric, self.datamodel).get()
        self.assertEqual("1", response["sources"][0]["value"])

    def test_warning_only(self):
        """Test that only transactions that exceed the warning threshold are counted."""
        self.mock_response.text = '<html><table class="details"><tr class="transaction"><td class="red evaluated"/>' \
            '</tr><tr class="transaction"><td class="name">Name</td><td class="yellow evaluated"/></tr>' \
            '<tr class="transaction"><td class="green evaluated"/></tr></table></html>'
        self.sources["source_id"]["parameters"]["thresholds"] = ["warning"]
        metric = dict(type="slow_transactions", sources=self.sources, addition="sum")
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric, self.datamodel).get()
        self.assertEqual([dict(key="Name", name="Name", threshold="warning")], response["sources"][0]["entities"])
        self.assertEqual("1", response["sources"][0]["value"])

    def test_source_up_to_dateness(self):
        """Test that the test age is returned."""
        self.mock_response.text = '<html><table class="config"><tr><td class="name">Start of the test</td>' \
            '<td id="start_of_the_test">2019.06.22.06.23.00</td></tr></table></html>'
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="max")
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric, self.datamodel).get()
        expected_age = days_ago(datetime(2019, 6, 22, 6, 23, 0))
        self.assertEqual(str(expected_age), response["sources"][0]["value"])

    def test_duration(self):
        """Test that the test duration is returned."""
        self.mock_response.text = '<html><table class="config"><tr><td class="name">Duration</td>' \
            '<td id="duration">00:35:00</td></tr></table></html>'
        metric = dict(type="performancetest_duration", sources=self.sources, addition="min")
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric, self.datamodel).get()
        self.assertEqual("35", response["sources"][0]["value"])

    def test_tests(self):
        """Test that the number of performancetest transactions is returned."""
        self.mock_response.text = '<html><table class="config">' \
            '<tr><td class="name">Success</td><td id="success">670</td></tr>' \
            '<tr><td class="name">Failed</td><td id="failed">37</td></tr>' \
            '<tr><td class="name">Canceled</td><td id="canceled">5</td></tr></table></html>'
        metric = dict(type="tests", sources=self.sources, addition="sum")
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric, self.datamodel).get()
        self.assertEqual("712", response["sources"][0]["value"])

    def test_failed_tests(self):
        """Test that the number of failed performancetest transactions is returned."""
        self.mock_response.text = '<html><table class="config">' \
            '<tr><td class="name">Failed</td><td id="failed">37</td></tr>' \
            '<tr><td class="name">Canceled</td><td id="canceled">5</td></tr></table></html>'
        metric = dict(type="failed_tests", sources=self.sources, addition="sum")
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric, self.datamodel).get()
        self.assertEqual("42", response["sources"][0]["value"])

    def test_stability(self):
        """Test that the percentage of the duration of the performancetest at which the test becomes unstable is
        returned."""
        self.mock_response.text = '''<html><table class="config">
            <tr><td class="name">Trendbreak 'stability' (%)</td><td id="trendbreak_stability">90</td></tr>
            </table></html>'''
        metric = dict(type="performancetest_stability", sources=self.sources, addition="min")
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric, self.datamodel).get()
        self.assertEqual("90", response["sources"][0]["value"])

    def test_scalability(self):
        """Test that the percentage of the max users of the performancetest at which the ramp-up of throughput breaks is
        returned."""
        self.mock_response.text = '''<html><table class="config">
            <tr><td class="name">Trendbreak 'scalability' (%)</td><td id="trendbreak_scalability">74</td></tr>
            </table></html>'''
        metric = dict(type="scalability", sources=self.sources, addition="min")
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric, self.datamodel).get()
        self.assertEqual("74", response["sources"][0]["value"])

    def test_scalability_without_breaking_point(self):
        """Test that if the percentage of the max users of the performancetest at which the ramp-up of throughput breaks
        is 100%, the metric reports an error (since there is no breaking point)."""
        self.mock_response.text = '''<html><table class="config">
            <tr><td class="name">Trendbreak 'scalability' (%)</td><td id="trendbreak_scalability">100</td></tr>
            </table></html>'''
        metric = dict(type="scalability", sources=self.sources, addition="min")
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric, self.datamodel).get()
        self.assertEqual(None, response["sources"][0]["value"])
        self.assertTrue(response["sources"][0]["parse_error"].startswith("Traceback"))
