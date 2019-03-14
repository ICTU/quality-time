"""Unit tests for the collector main script."""

import logging
import unittest
from unittest.mock import patch, Mock

from collector import collect, fetch_measurements


class CollectorTest(unittest.TestCase):
    """Unit tests for the collection methods."""
    def setUp(self):
        self.mock_response = Mock()
        logging.getLogger().disabled = True

    def tearDown(self):
        logging.getLogger().disabled = False

    def test_fetch_without_sources(self):
        """Test fetching measurement for a metric without sources."""
        self.mock_response.json.return_value = dict(metric_uuid=dict(report_uuid="report_uuid", sources=dict()))
        with patch("requests.get", return_value=self.mock_response):
            with patch("requests.post") as post:
                fetch_measurements("http://server")
        post.assert_called_once_with(
            "http://server/measurements",
            json=dict(sources=[], value=None, metric_uuid="metric_uuid", report_uuid="report_uuid"))

    def test_fetch_with_get_error(self):
        """Test fetching measurement when getting fails."""
        with patch("requests.get", side_effect=RuntimeError):
            with patch("requests.post") as post:
                fetch_measurements("http://server")
        post.assert_not_called()

    def test_fetch_with_post_error(self):
        """Test fetching measurement when posting fails."""
        self.mock_response.json.return_value = dict(metric_uuid=dict(report_uuid="report_uuid", sources=dict()))
        with patch("requests.get", return_value=self.mock_response):
            with patch("requests.post", side_effect=RuntimeError) as post:
                fetch_measurements("http://server")
        post.assert_called_once_with(
            "http://server/measurements",
            json=dict(sources=[], value=None, metric_uuid="metric_uuid", report_uuid="report_uuid"))

    def test_collect(self):
        """Test the collect method."""
        self.mock_response.json.return_value = dict(metric_uuid=dict(report_uuid="report_uuid", sources=dict()))
        with patch("requests.get", return_value=self.mock_response):
            with patch("requests.post") as post:
                with patch("time.sleep", side_effect=[RuntimeError]):
                    self.assertRaises(RuntimeError, collect)
        post.assert_called_once_with(
            "http://localhost:8080/measurements",
            json=dict(sources=[], value=None, metric_uuid="metric_uuid", report_uuid="report_uuid"))
