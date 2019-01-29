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
        mock_response.text = "<testsuite tests='2'></testsuite>"
        self.metric = dict(metric="tests", sources=dict(a=dict(source="junit", url="http://url")))
        with patch("requests.get", return_value=mock_response):
            self.response = Collector(self.metric).get()

    def test_source_response_api_url(self):
        """Test that the api url used for contacting the source is returned."""
        self.assertEqual("http://url", self.response["sources"][0]["api_url"])

    def test_source_response_landing_url(self):
        """Test that the landing url for the source is returned."""
        self.assertEqual("http://url", self.response["sources"][0]["landing_url"])

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        self.assertEqual("2", self.response["sources"][0]["measurement"])

    def test_sum(self):
        """Test that two measurements can be added."""
        self.assertEqual(Measurement("7"), Collector(self.metric).sum([Measurement("4"), Measurement("3")]))

    def test_safely_sum(self):
        """Test that two measurements can be added safely."""
        self.assertEqual((Measurement("7"), None),
                         Collector(self.metric).safely_sum([Measurement("4"), Measurement("3")]))

    def test_safely_sum_with_error(self):
        """Test that an error message is returned when adding fails."""
        measurement, error_message = Collector(self.metric).safely_sum([Measurement("4"), Measurement("abc")])
        self.assertEqual(None, measurement)
        self.assertTrue(error_message.startswith("Traceback"))

    def test_safely_sum_with_none(self):
        """Test that None is returned if one of the input measurements is None."""
        measurement, error_message = Collector(self.metric).safely_sum([Measurement("4"), None])
        self.assertEqual(None, measurement)
        self.assertEqual(None, error_message)


class CollectorWithMultipleURLsTest(unittest.TestCase):
    """Unit tests for the source class with multiple URLs."""

    def setUp(self):
        """Simple response fixture."""
        Collector.RESPONSE_CACHE.clear()
        mock_response = Mock()
        mock_response.text = "<testsuite tests='2'></testsuite>"
        self.metric = dict(
            metric="tests",
            sources=dict(a=dict(source="junit", url="http://url"), b=dict(source="junit", url="http://url2")))
        with patch("requests.get", return_value=mock_response):
            self.response = Collector(self.metric).get()

    def test_source_response_api_url(self):
        """Test that the api url used for contacting the source is returned."""
        self.assertEqual("http://url2", self.response["sources"][1]["api_url"])

    def test_source_response_landing_url(self):
        """Test that the landing url for the source is returned."""
        self.assertEqual("http://url2", self.response["sources"][1]["landing_url"])

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        self.assertEqual("2", self.response["sources"][1]["measurement"])


class CollectorWithMultipleSourceTypesTest(unittest.TestCase):
    """Unit tests for collecting measurements from different source types."""

    def setUp(self):
        """Simple response fixture."""
        Collector.RESPONSE_CACHE.clear()
        mock_response = Mock()
        mock_response.json.return_value = dict(jobs=[dict(buildable=True)])  # Works for both Gitlab and Jenkins
        self.metric = dict(
            metric="jobs",
            sources=dict(
                a=dict(source="jenkins", url="http://jenkins"),
                b=dict(source="gitlab", url="http://gitlab", component="project", private_token="token")))
        with patch("requests.get", return_value=mock_response):
            self.response = Collector(self.metric).get()

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        self.assertEqual("2", self.response["measurement"]["measurement"])


class CollectorErrorTest(unittest.TestCase):
    """Unit tests for error handling."""

    def setUp(self):
        """Clear cache."""
        Collector.RESPONSE_CACHE.clear()
        self.metric = dict(metric="tests", sources=dict(a=dict(source="junit", url="http://url")))

    def test_connection_error(self):
        """Test that an error retrieving the data is handled."""
        with patch("requests.get", side_effect=Exception):
            response = Collector(self.metric).get()
        self.assertTrue(response["sources"][0]["connection_error"].startswith("Traceback"))

    def test_parse_error(self):
        """Test that an error retrieving the data is handled."""

        class JunitMetric(Collector):
            """Raise an exception when parsing the response."""

            def parse_source_response(self, response: requests.Response) -> Measurement:
                """Fail."""
                raise Exception

        mock_response = Mock()
        mock_response.text = "1"
        with patch("requests.get", return_value=mock_response):
            response = Collector(self.metric).get()
        self.assertTrue(response["sources"][0]["parse_error"].startswith("Traceback"))
