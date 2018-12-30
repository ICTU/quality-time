"""Unit tests for the source class."""

import unittest
from unittest.mock import patch, Mock

import requests

from collector.source import Source
from collector.type import Measurement


class SourceTest(unittest.TestCase):
    """Unit tests for the source class."""

    def setUp(self):
        """Simple response fixture."""
        Source.RESPONSE_CACHE.clear()
        mock_response = Mock()
        mock_response.text = "2"
        with patch("requests.get", return_value=mock_response):
            self.response = Source(dict()).get(dict(request=dict(urls=["http://url"])))

    def test_source_response_api_url(self):
        """Test that the api url used for contacting the source is returned."""
        self.assertEqual("http://url", self.response["source"]["responses"][0]["api_url"])

    def test_source_response_landing_url(self):
        """Test that the landing url for the source is returned."""
        self.assertEqual("http://url", self.response["source"]["responses"][0]["landing_url"])

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        self.assertEqual("2", self.response["source"]["responses"][0]["measurement"])


class SourceWithMultipleURLsTest(unittest.TestCase):
    """Unit tests for the source class with multiple URLs."""

    def setUp(self):
        """Simple response fixture."""
        Source.RESPONSE_CACHE.clear()
        mock_response = Mock()
        mock_response.text = "2"
        with patch("requests.get", return_value=mock_response):
            self.response = Source(dict()).get(dict(request=dict(urls=["http://url", "http://url2"])))

    def test_source_response_api_url(self):
        """Test that the api url used for contacting the source is returned."""
        self.assertEqual("http://url2", self.response["source"]["responses"][1]["api_url"])

    def test_source_response_landing_url(self):
        """Test that the landing url for the source is returned."""
        self.assertEqual("http://url2", self.response["source"]["responses"][1]["landing_url"])

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        self.assertEqual("2", self.response["source"]["responses"][1]["measurement"])


class SourceErrorTest(unittest.TestCase):
    """Unit tests for error handling."""

    def setUp(self):
        """Clear cache."""
        Source.RESPONSE_CACHE.clear()

    def test_connection_error(self):
        """Test that an error retrieving the data is handled."""
        with patch("requests.get", side_effect=Exception):
            response = Source(dict()).get(dict(request=dict(urls=["http://url"])))
        self.assertTrue(response["source"]["responses"][0]["connection_error"].startswith("Traceback"))

    def test_parse_error(self):
        """Test that an error retrieving the data is handled."""

        class SourceUnderTest(Source):
            """Raise an exception when parsing the response."""

            def parse_source_response(self, response: requests.Response) -> Measurement:
                """Fail."""
                raise Exception

        mock_response = Mock()
        mock_response.text = "1"
        with patch("requests.get", return_value=mock_response):
            response = SourceUnderTest(dict()).get(dict(request=dict(urls=["http://url"])))
        self.assertTrue(response["source"]["responses"][0]["parse_error"].startswith("Traceback"))
