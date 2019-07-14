"""Unit tests for the collector main script."""

import logging
import unittest
from unittest.mock import patch, Mock
from typing import List

import requests

from src import source_collector, collect
from src.metrics_collector import MetricsCollector
from src.type import Value


class CollectorTest(unittest.TestCase):
    """Unit tests for the collection methods."""

    def setUp(self):
        class SourceMetric(source_collector.SourceCollector):  # pylint: disable=unused-variable
            """Fake collector."""

            def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:  # pylint: disable=unused-argument
                """Return the answer."""
                return "42"

        self.mock_response = Mock()
        logging.getLogger().disabled = True

    def tearDown(self):
        logging.getLogger().disabled = False

    def test_fetch_without_sources(self):
        """Test fetching measurement for a metric without sources."""
        self.mock_response.json.return_value = dict(
            metric_uuid=dict(report_uuid="report_uuid", addition="sum", sources=dict()))
        with patch("requests.get", return_value=self.mock_response):
            with patch("requests.post") as post:
                MetricsCollector().fetch_measurements()
        post.assert_not_called()

    def test_fetch_with_get_error(self):
        """Test fetching measurement when getting fails."""
        with patch("requests.get", side_effect=RuntimeError):
            with patch("requests.post") as post:
                MetricsCollector().fetch_measurements()
        post.assert_not_called()

    def test_fetch_with_post_error(self):
        """Test fetching measurement when posting fails."""
        self.mock_response.json.return_value = dict(
            metric_uuid=dict(report_uuid="report_uuid", addition="sum", type="metric",
                             sources=dict(source_id=dict(type="source", parameters=dict(url="http://url")))))
        with patch("requests.get", return_value=self.mock_response):
            with patch("requests.post", side_effect=RuntimeError) as post:
                MetricsCollector().fetch_measurements()
        post.assert_called_once_with(
            "http://localhost:5001/measurements",
            json=dict(
                sources=[
                    dict(api_url="http://url", landing_url="http://url", value="42", entities=[], connection_error=None,
                         parse_error=None, source_uuid="source_id")],
                value=42, metric_uuid="metric_uuid", report_uuid="report_uuid"))

    def test_collect(self):
        """Test the collect method."""
        self.mock_response.json.return_value = dict(
            metric_uuid=dict(report_uuid="report_uuid", addition="sum", type="metric",
                             sources=dict(source_id=dict(type="source", parameters=dict(url="http://url")))))
        with patch("requests.get", return_value=self.mock_response):
            with patch("requests.post") as post:
                with patch("time.sleep", side_effect=[RuntimeError]):
                    self.assertRaises(RuntimeError, collect)
        post.assert_called_once_with(
            "http://localhost:5001/measurements",
            json=dict(
                sources=[
                    dict(api_url="http://url", landing_url="http://url", value="42", entities=[], connection_error=None,
                         parse_error=None, source_uuid="source_id")], value=42, metric_uuid="metric_uuid",
                report_uuid="report_uuid"))

    def test_missing_collector(self):
        """Test that an exception is thrown if there's no collector for the source and metric type."""
        self.mock_response.json.return_value = dict(
            metric_uuid=dict(
                type="metric", addition="sum", report_uuid="report_uuid",
                sources=dict(missing=dict(type="unknown_source", parameters=dict(url="http://url")))))
        with patch("requests.get", return_value=self.mock_response):
            self.assertRaises(
                LookupError, MetricsCollector().fetch_measurements)

    def test_fetch_twice(self):
        """Test that the metric is skipped on the second fetch."""
        self.mock_response.json.return_value = dict(
            metric_uuid=dict(report_uuid="report_uuid", addition="sum", type="metric",
                             sources=dict(source_id=dict(type="source", parameters=dict(url="http://url")))))
        with patch("requests.get", return_value=self.mock_response):
            with patch("requests.post") as post:
                metric_collector = MetricsCollector()
                metric_collector.fetch_measurements()
                metric_collector.fetch_measurements()
        post.assert_called_once_with(
            "http://localhost:5001/measurements",
            json=dict(
                sources=[
                    dict(api_url="http://url", landing_url="http://url", value="42", entities=[], connection_error=None,
                         parse_error=None, source_uuid="source_id")], value=42, metric_uuid="metric_uuid",
                report_uuid="report_uuid"))

    def test_no_urls(self):
        """Test that a metric with sources but without urls is skipped."""
        self.mock_response.json.return_value = dict(
            metric_uuid=dict(
                type="metric", addition="sum", report_uuid="report_uuid",
                sources=dict(missing=dict(type="source", parameters=dict(url="")))))
        with patch("requests.get", return_value=self.mock_response):
            with patch("requests.post") as post:
                MetricsCollector().fetch_measurements()
        post.assert_not_called()
