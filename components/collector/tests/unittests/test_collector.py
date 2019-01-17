"""Unit tests for the Collector class."""

import unittest
from unittest.mock import patch, Mock

import requests

from collector.collector import Collector
from collector.type import Measurement


class CollectorTest(unittest.TestCase):
    """Unit tests for the Collector class."""

    def setUp(self):
        """Simple response fixture."""
        Collector.RESPONSE_CACHE.clear()
        mock_response = Mock()
        mock_response.text = "2"
        with patch("requests.get", return_value=mock_response):
            self.response = Collector(dict()).get(dict(request=dict(urls=["http://url"])))

    def test_subclass_registration(self):
        """Test that a subclass to handle a specific API can be found."""

        class RegisteredCollector(Collector):  # pylint: disable=unused-variable
            """Collector subclass that gets registered."""
            def get(self, *args, **kwargs):
                """Return the response."""
                return dict(result="Success")

        collector = Collector.get_subclass("registered_collector")(dict())
        self.assertEqual(dict(result="Success"), collector.get(dict()))

    def test_source_response_api_url(self):
        """Test that the api url used for contacting the source is returned."""
        self.assertEqual("http://url", self.response["source"]["responses"][0]["api_url"])

    def test_source_response_landing_url(self):
        """Test that the landing url for the source is returned."""
        self.assertEqual("http://url", self.response["source"]["responses"][0]["landing_url"])

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        self.assertEqual("2", self.response["source"]["responses"][0]["measurement"])

    def test_sum(self):
        """Test that two measurements can be added."""
        self.assertEqual(Measurement("7"), Collector(dict()).sum([Measurement("4"), Measurement("3")]))

    def test_safely_sum(self):
        """Test that two measurements can be added safely."""
        self.assertEqual((Measurement("7"), None),
                         Collector(dict()).safely_sum([Measurement("4"), Measurement("3")]))

    def test_safely_sum_with_error(self):
        """Test that an error message is returned when adding fails."""
        measurement, error_message = Collector(dict()).safely_sum([Measurement("4"), Measurement("abc")])
        self.assertEqual(None, measurement)
        self.assertTrue(error_message.startswith("Traceback"))

    def test_safely_sum_with_none(self):
        """Test that None is returned if one of the input measurements is None."""
        measurement, error_message = Collector(dict()).safely_sum([Measurement("4"), None])
        self.assertEqual(None, measurement)
        self.assertEqual(None, error_message)


class CollectorWithMultipleURLsTest(unittest.TestCase):
    """Unit tests for the source class with multiple URLs."""

    def setUp(self):
        """Simple response fixture."""
        Collector.RESPONSE_CACHE.clear()
        mock_response = Mock()
        mock_response.text = "2"
        with patch("requests.get", return_value=mock_response):
            self.response = Collector(dict()).get(dict(request=dict(urls=["http://url", "http://url2"])))

    def test_source_response_api_url(self):
        """Test that the api url used for contacting the source is returned."""
        self.assertEqual("http://url2", self.response["source"]["responses"][1]["api_url"])

    def test_source_response_landing_url(self):
        """Test that the landing url for the source is returned."""
        self.assertEqual("http://url2", self.response["source"]["responses"][1]["landing_url"])

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        self.assertEqual("2", self.response["source"]["responses"][1]["measurement"])


class CollectorErrorTest(unittest.TestCase):
    """Unit tests for error handling."""

    def setUp(self):
        """Clear cache."""
        Collector.RESPONSE_CACHE.clear()

    def test_connection_error(self):
        """Test that an error retrieving the data is handled."""
        with patch("requests.get", side_effect=Exception):
            response = Collector(dict()).get(dict(request=dict(urls=["http://url"])))
        self.assertTrue(response["source"]["responses"][0]["connection_error"].startswith("Traceback"))

    def test_parse_error(self):
        """Test that an error retrieving the data is handled."""

        class CollectorUnderTest(Collector):
            """Raise an exception when parsing the response."""

            def parse_source_response(self, response: requests.Response) -> Measurement:
                """Fail."""
                raise Exception

        mock_response = Mock()
        mock_response.text = "1"
        with patch("requests.get", return_value=mock_response):
            response = CollectorUnderTest(dict()).get(dict(request=dict(urls=["http://url"])))
        self.assertTrue(response["source"]["responses"][0]["parse_error"].startswith("Traceback"))
