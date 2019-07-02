"""Unit tests for the Performancetest-runner source."""

from datetime import datetime
import unittest
from unittest.mock import Mock, patch

from src.collector import MetricCollector
from src.util import days_ago


class PerformanceTestRunnerTest(unittest.TestCase):
    """Unit tests for the Performancetest-runner metrics."""

    def setUp(self):
        self.mock_response = Mock()
        self.sources = dict(source_id=dict(type="performancetest_runner", parameters=dict(url="report.html")))

    def test_no_transactions(self):
        """Test that the number of slow transactions is 0 if there are no transactions in the details table."""
        self.mock_response.text = '<html><table class="details"><tr></tr></table></html>'
        metric = dict(type="slow_transactions", sources=self.sources, addition="sum")
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric).get()
        self.assertEqual("0", response["sources"][0]["value"])

    def test_one_slow_transaction(self):
        """Test that the number of slow transactions is 1 if there is 1 slow transactions in the details table."""
        self.mock_response.text = '<html><table class="details"><tr class="transaction"><td class="red evaluated"/>' \
            '</tr></table></html>'
        metric = dict(type="slow_transactions", sources=self.sources, addition="sum")
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric).get()
        self.assertEqual("1", response["sources"][0]["value"])

    def test_ignore_fast_transactions(self):
        """Test that fast transactions are not counted."""
        self.mock_response.text = '<html><table class="details"><tr class="transaction"><td class="red evaluated"/>' \
            '</tr><tr class="transaction"><td class="green evaluated"/></tr></table></html>'
        metric = dict(type="slow_transactions", sources=self.sources, addition="sum")
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric).get()
        self.assertEqual("1", response["sources"][0]["value"])

    def test_warning_only(self):
        """Test that only transactions that exceed the warning threshold are counted."""
        self.mock_response.text = '<html><table class="details"><tr class="transaction"><td class="red evaluated"/>' \
            '</tr><tr class="transaction"><td class="name">Name</td><td class="yellow evaluated"/></tr>' \
            '<tr class="transaction"><td class="green evaluated"/></tr></table></html>'
        self.sources["source_id"]["parameters"]["thresholds"] = ["warning"]
        metric = dict(type="slow_transactions", sources=self.sources, addition="sum")
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric).get()
        self.assertEqual([dict(key="Name", name="Name", threshold="warning")], response["sources"][0]["entities"])
        self.assertEqual("1", response["sources"][0]["value"])

    def test_source_up_to_dateness(self):
        """Test that the test age is returned."""
        self.mock_response.text = '<html><table class="config"><tr><td class="name">Start of the test</td>' \
            '<td id="start_of_the_test">2019.06.22.06.23.00</td></tr></table></html>'
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="max")
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric).get()
        expected_age = days_ago(datetime(2019, 6, 22, 6, 23, 0))
        self.assertEqual(str(expected_age), response["sources"][0]["value"])

    def test_duration(self):
        """Test that the test duration is returned."""
        self.mock_response.text = '<html><table class="config"><tr><td class="name">Duration</td>' \
            '<td id="duration">00:35:00</td></tr></table></html>'
        metric = dict(type="performancetest_duration", sources=self.sources, addition="min")
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric).get()
        self.assertEqual("35", response["sources"][0]["value"])
