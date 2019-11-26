"""Unit tests for the collector main script."""

import logging
import unittest
from typing import Tuple
from unittest.mock import patch, Mock

import quality_time_collector
from metric_collectors import MetricsCollector
from source_collectors import source_collector
from collector_utilities.type import Entities, Responses, Value


class CollectorTest(unittest.TestCase):
    """Unit tests for the collection methods."""

    def setUp(self):
        class SourceMetric(source_collector.SourceCollector):  # pylint: disable=unused-variable
            """Register a fake collector automatically."""

            def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
                return "42", "84", []

        self.data_model_response = Mock()
        self.data_model = dict(sources=dict(source=dict(parameters=dict(url=dict(mandatory=True, metrics=["metric"])))))
        self.data_model_response.json.return_value = self.data_model
        self.metrics_response = Mock()
        self.metrics_collector = MetricsCollector()
        logging.disable()

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_fetch_without_sources(self):
        """Test fetching measurement for a metric without sources."""
        self.metrics_response.json.return_value = dict(
            metric_uuid=dict(report_uuid="report_uuid", type="metric", addition="sum", sources=dict()))
        with patch("requests.get", return_value=self.metrics_response):
            with patch("requests.post") as post:
                self.metrics_collector.fetch_measurements(60)
        post.assert_not_called()

    def test_fetch_with_get_error(self):
        """Test fetching measurement when getting fails."""
        with patch("requests.get", side_effect=RuntimeError):
            with patch("requests.post") as post:
                self.metrics_collector.fetch_measurements(60)
        post.assert_not_called()

    def test_fetch_with_post_error(self):
        """Test fetching measurement when posting fails."""
        self.metrics_response.json.return_value = dict(
            metric_uuid=dict(report_uuid="report_uuid", addition="sum", type="metric",
                             sources=dict(source_id=dict(type="source", parameters=dict(url="https://url")))))

        with patch("requests.get", side_effect=[self.metrics_response, Mock()]):
            with patch("requests.post", side_effect=RuntimeError) as post:
                self.metrics_collector.data_model = self.data_model
                self.metrics_collector.fetch_measurements(60)
        post.assert_called_once_with(
            "http://localhost:5001/api/v1/measurements",
            json=dict(
                sources=[
                    dict(api_url="https://url", landing_url="https://url", value="42", total="84", entities=[],
                         connection_error=None, parse_error=None, source_uuid="source_id")],
                metric_uuid="metric_uuid", report_uuid="report_uuid"))

    def test_collect(self):
        """Test the collect method."""
        self.metrics_response.json.return_value = dict(
            metric_uuid=dict(report_uuid="report_uuid", addition="sum", type="metric",
                             sources=dict(source_id=dict(type="source", parameters=dict(url="https://url")))))
        with patch("requests.get", side_effect=[self.data_model_response, self.metrics_response, Mock()]):
            with patch("requests.post") as post:
                with patch("time.sleep", side_effect=[RuntimeError]):
                    self.assertRaises(RuntimeError, quality_time_collector.collect)
        post.assert_called_once_with(
            "http://localhost:5001/api/v1/measurements",
            json=dict(
                sources=[
                    dict(api_url="https://url", landing_url="https://url", value="42", total="84", entities=[],
                         connection_error=None, parse_error=None, source_uuid="source_id")],
                metric_uuid="metric_uuid", report_uuid="report_uuid"))

    def test_missing_collector(self):
        """Test that an exception is thrown if there's no collector for the source and metric type."""
        self.metrics_response.json.return_value = dict(
            metric_uuid=dict(
                type="metric", addition="sum", report_uuid="report_uuid",
                sources=dict(missing=dict(type="unknown_source", parameters=dict(url="https://url")))))
        with patch("requests.get", return_value=self.metrics_response):
            self.assertRaises(LookupError, self.metrics_collector.fetch_measurements, 60)

    def test_fetch_twice(self):
        """Test that the metric is skipped on the second fetch."""
        self.metrics_response.json.return_value = dict(
            metric_uuid=dict(report_uuid="report_uuid", addition="sum", type="metric",
                             sources=dict(source_id=dict(type="source", parameters=dict(url="https://url")))))
        with patch("requests.get", side_effect=[self.metrics_response, Mock(), self.metrics_response]):
            with patch("requests.post") as post:
                self.metrics_collector.data_model = self.data_model
                self.metrics_collector.fetch_measurements(60)
                self.metrics_collector.fetch_measurements(60)
        post.assert_called_once_with(
            "http://localhost:5001/api/v1/measurements",
            json=dict(
                sources=[
                    dict(api_url="https://url", landing_url="https://url", value="42", total="84", entities=[],
                         connection_error=None, parse_error=None, source_uuid="source_id")],
                metric_uuid="metric_uuid", report_uuid="report_uuid"))

    def test_missing_mandatory_parameter(self):
        """Test that a metric with sources but without a mandatory parameter is skipped."""
        self.metrics_response.json.return_value = dict(
            metric_uuid=dict(
                type="metric", addition="sum", report_uuid="report_uuid",
                sources=dict(missing=dict(type="source", parameters=dict(url="")))))
        with patch("requests.get", return_value=self.metrics_response):
            with patch("requests.post") as post:
                self.metrics_collector.data_model = self.data_model
                self.metrics_collector.fetch_measurements(60)
        post.assert_not_called()

    def test_fetch_data_model_after_failure(self):
        """Test that that the data model is fetched on the second try."""
        with patch("requests.get", side_effect=[None, self.data_model_response]):
            data_model = self.metrics_collector.fetch_data_model(0)
        self.assertEqual(self.data_model, data_model)
