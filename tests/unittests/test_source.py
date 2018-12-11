"""Unit tests for the source class."""

import unittest
from unittest.mock import patch, Mock

import bottle

from quality_time.source import Source


class SourceTest(unittest.TestCase):
    """Unit tests for the source class."""

    def setUp(self):
        """Simple response fixture."""
        mock_response = Mock()
        mock_response.text = "2"
        with patch("requests.get", return_value=mock_response):
            request = bottle.Request(dict(QUERY_STRING="url=http://url"))
            self.response = Source(request).get("metric")

    def test_source_response_api_url(self):
        """Test that the api url used for contacting the source is returned."""
        self.assertEqual("http://url", self.response["source_responses"][0]["api_url"])

    def test_source_response_landing_url(self):
        """Test that the landing url for the source is returned."""
        self.assertEqual("http://url", self.response["source_responses"][0]["landing_url"])

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        self.assertEqual("2", self.response["source_responses"][0]["measurement"])


class SourceWithMultipleURLsTest(unittest.TestCase):
    """Unit tests for the source class with multiple URLs."""

    def setUp(self):
        """Simple response fixture."""
        mock_response = Mock()
        mock_response.text = "2"
        with patch("requests.get", return_value=mock_response):
            request = bottle.Request(dict(QUERY_STRING="url=http://url1&url=http://url2"))
            self.response = Source(request).get("metric")

    def test_source_response_api_url(self):
        """Test that the api url used for contacting the source is returned."""
        self.assertEqual("http://url2", self.response["source_responses"][1]["api_url"])

    def test_source_response_landing_url(self):
        """Test that the landing url for the source is returned."""
        self.assertEqual("http://url2", self.response["source_responses"][1]["landing_url"])

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        self.assertEqual("2", self.response["source_responses"][1]["measurement"])
