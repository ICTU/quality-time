"""Unit tests for the collector main script."""

import datetime
import logging
import unittest
from typing import List
from unittest.mock import call, patch, Mock

import requests

import quality_time_collector
from metric_collectors import MetricsCollector
from source_collectors import source_collector
from utilities.type import Value


class CollectorTest(unittest.TestCase):
    """Unit tests for the collection methods."""

    def setUp(self):
        class SourceMetric(source_collector.SourceCollector):
            """Fake collector."""

            next_collection_datetime = None

            def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:  # pylint: disable=unused-argument
                """Return the answer."""
                return "42"

            def _parse_source_responses_total(self, responses: List[requests.Response]) -> Value:  # pylint: disable=unused-argument
                """Return the answer."""
                return "84"

            def next_collection(self) -> datetime:
                return self.next_collection_datetime if self.next_collection_datetime else super().next_collection()

        self.source_metric_class = SourceMetric
        self.datamodel_response = Mock()
        self.datamodel_response.json.return_value = dict(
            sources=dict(source=dict(parameters=dict(url=dict(mandatory=True, metrics=["metric"])))))
        self.metrics_response = Mock()
        logging.disable()

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_fetch_without_sources(self):
        """Test fetching measurement for a metric without sources."""
        self.metrics_response.json.return_value = dict(
            metric_uuid=dict(report_uuid="report_uuid", type="metric", addition="sum", sources=dict()))
        with patch("requests.get", side_effect=[self.datamodel_response, self.metrics_response]):
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
        self.metrics_response.json.return_value = dict(
            metric_uuid=dict(report_uuid="report_uuid", addition="sum", type="metric",
                             sources=dict(source_id=dict(type="source", parameters=dict(url="https://url")))))

        with patch("requests.get", side_effect=[self.datamodel_response, self.metrics_response, Mock()]):
            with patch("requests.post", side_effect=RuntimeError) as post:
                MetricsCollector().fetch_measurements()
        post.assert_called_once_with(
            "http://localhost:5001/measurements",
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
        with patch("requests.get", side_effect=[self.datamodel_response, self.metrics_response, Mock()]):
            with patch("requests.post") as post:
                with patch("time.sleep", side_effect=[RuntimeError]):
                    self.assertRaises(RuntimeError, quality_time_collector.collect)
        post.assert_called_once_with(
            "http://localhost:5001/measurements",
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
        with patch("requests.get", side_effect=[self.datamodel_response, self.metrics_response]):
            self.assertRaises(
                LookupError, MetricsCollector().fetch_measurements)

    def test_fetch_twice(self):
        """Test that the metric is skipped on the second fetch."""
        self.metrics_response.json.return_value = dict(
            metric_uuid=dict(report_uuid="report_uuid", addition="sum", type="metric",
                             sources=dict(source_id=dict(type="source", parameters=dict(url="https://url")))))
        side_effect = [
            self.datamodel_response, self.metrics_response, Mock(), self.datamodel_response, self.metrics_response]
        with patch("requests.get", side_effect=side_effect):
            with patch("requests.post") as post:
                metric_collector = MetricsCollector()
                metric_collector.fetch_measurements()
                metric_collector.fetch_measurements()
        post.assert_called_once_with(
            "http://localhost:5001/measurements",
            json=dict(
                sources=[
                    dict(api_url="https://url", landing_url="https://url", value="42", total="84", entities=[],
                         connection_error=None, parse_error=None, source_uuid="source_id")],
                metric_uuid="metric_uuid", report_uuid="report_uuid"))

    def test_fetch_twice_no_skip(self):
        """Test that the metric is not skipped on the second fetch if it wants to be collected as soon as possible."""
        self.source_metric_class.next_collection_datetime = datetime.datetime.min
        self.metrics_response.json.return_value = dict(
            metric_uuid=dict(report_uuid="report_uuid", addition="sum", type="metric",
                             sources=dict(source_id=dict(type="source", parameters=dict(url="https://url")))))
        side_effect = [self.datamodel_response, self.metrics_response, Mock()] * 2
        with patch("requests.get", side_effect=side_effect):
            with patch("requests.post") as post:
                metric_collector = MetricsCollector()
                metric_collector.fetch_measurements()
                metric_collector.fetch_measurements()
        post_call = call(
            "http://localhost:5001/measurements",
            json=dict(
                sources=[
                    dict(api_url="https://url", landing_url="https://url", value="42", total="84", entities=[],
                         connection_error=None, parse_error=None, source_uuid="source_id")],
                metric_uuid="metric_uuid", report_uuid="report_uuid")),
        post.assert_has_calls(post_call, post_call)

    def test_fetch_twice_with_invalid_credentials(self):
        """Test that the metric is skipped on the second fetch if the credentials are invalid."""
        self.metrics_response.json.return_value = dict(
            metric_uuid=dict(report_uuid="report_uuid", addition="sum", type="metric",
                             sources=dict(source_id=dict(type="source", parameters=dict(url="https://url")))))
        response_401 = Mock()
        response_401.status_code = 401
        side_effect = [
            self.datamodel_response, self.metrics_response, response_401, self.datamodel_response,
            self.metrics_response]
        with patch("requests.get", side_effect=side_effect):
            with patch("requests.post") as post:
                metric_collector = MetricsCollector()
                metric_collector.fetch_measurements()
                metric_collector.fetch_measurements()
        post.assert_called_once_with(
            "http://localhost:5001/measurements",
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
        with patch("requests.get", side_effect=[self.datamodel_response, self.metrics_response]):
            with patch("requests.post") as post:
                MetricsCollector().fetch_measurements()
        post.assert_not_called()
