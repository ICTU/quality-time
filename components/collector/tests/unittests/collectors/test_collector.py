"""Unit tests for the Collector class."""

import unittest
from unittest.mock import patch, Mock

from collector.collector import Collector, collect_measurement


class CollectorTest(unittest.TestCase):
    """Unit tests for the Collector class."""

    def setUp(self):
        """Simple response fixture."""
        Collector.RESPONSE_CACHE.clear()
        mock_response = Mock()
        mock_response.text = "<testsuite tests='2'></testsuite>"
        metric = dict(type="tests", sources=dict(a=dict(type="junit", parameters=dict(url="http://url"))))
        with patch("requests.get", return_value=mock_response):
            self.response = collect_measurement(metric)

    def test_source_response_api_url(self):
        """Test that the api url used for contacting the source is returned."""
        self.assertEqual("http://url", self.response["sources"][0]["api_url"])

    def test_source_response_landing_url(self):
        """Test that the landing url for the source is returned."""
        self.assertEqual("http://url", self.response["sources"][0]["landing_url"])

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        self.assertEqual("2", self.response["sources"][0]["value"])


class CollectorWithMultipleSourcesTest(unittest.TestCase):
    """Unit tests for the collector with multiple sources."""

    def setUp(self):
        """Simple response fixture."""
        Collector.RESPONSE_CACHE.clear()
        mock_response = Mock()
        mock_response.text = "<testsuite tests='2'></testsuite>"
        metric = dict(
            type="tests",
            sources=dict(
                a=dict(type="junit", parameters=dict(url="http://url")),
                b=dict(type="junit", parameters=dict(url="http://url2"))))
        with patch("requests.get", return_value=mock_response):
            self.response = collect_measurement(metric)

    def test_source_response_api_url(self):
        """Test that the api url used for contacting the source is returned."""
        self.assertEqual("http://url2", self.response["sources"][1]["api_url"])

    def test_source_response_landing_url(self):
        """Test that the landing url for the source is returned."""
        self.assertEqual("http://url2", self.response["sources"][1]["landing_url"])

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        self.assertEqual("2", self.response["sources"][1]["value"])


class CollectorWithMultipleSourceTypesTest(unittest.TestCase):
    """Unit tests for collecting measurements from different source types."""

    def setUp(self):
        """Simple response fixture."""
        Collector.RESPONSE_CACHE.clear()
        mock_response = Mock()
        mock_response.json.return_value = dict(
            jobs=[dict(name="job", url="http://job", buildable=True)])  # Works for both Gitlab and Jenkins
        metric = dict(
            type="jobs",
            sources=dict(
                a=dict(type="jenkins", parameters=dict(url="http://jenkins")),
                b=dict(type="gitlab", parameters=dict(url="http://gitlab", project="project", private_token="token"))))
        with patch("requests.get", return_value=mock_response):
            self.response = collect_measurement(metric)

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        sources = self.response["sources"]
        self.assertEqual([{'key': 'job', 'name': 'job', 'url': 'http://job'}], sources[0]["units"])
        self.assertEqual("1", sources[0]["value"])
        self.assertEqual([], sources[1]["units"])
        self.assertEqual("1", sources[1]["value"])


class CollectorErrorTest(unittest.TestCase):
    """Unit tests for error handling."""

    def setUp(self):
        """Clear cache."""
        Collector.RESPONSE_CACHE.clear()
        self.metric = dict(type="tests", sources=dict(a=dict(type="junit", parameters=dict(url="http://url"))))

    def test_connection_error(self):
        """Test that an error retrieving the data is handled."""
        with patch("requests.get", side_effect=Exception):
            response = collect_measurement(self.metric)
        self.assertTrue(response["sources"][0]["connection_error"].startswith("Traceback"))

    def test_parse_error(self):
        """Test that an error retrieving the data is handled."""
        mock_response = Mock()
        mock_response.text = "1"
        with patch("requests.get", return_value=mock_response):
            response = collect_measurement(self.metric)
        self.assertTrue(response["sources"][0]["parse_error"].startswith("Traceback"))
