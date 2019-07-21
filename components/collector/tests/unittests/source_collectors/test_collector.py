"""Unit tests for the Collector class."""

import unittest
from unittest.mock import patch, Mock

from metric_collectors import MetricCollector


class CollectorTest(unittest.TestCase):
    """Unit tests for the Collector class."""

    def setUp(self):
        """Simple response fixture."""
        mock_response = Mock()
        mock_response.text = "<testsuite tests='2'></testsuite>"
        metric = dict(
            type="tests", addition="sum", sources=dict(a=dict(type="junit", parameters=dict(url="http://url"))))
        with patch("requests.get", return_value=mock_response):
            self.response = MetricCollector(metric).get()

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
        mock_response = Mock()
        mock_response.text = "<testsuite tests='2'></testsuite>"
        metric = dict(
            type="tests", addition="sum",
            sources=dict(
                a=dict(type="junit", parameters=dict(url="http://url")),
                b=dict(type="junit", parameters=dict(url="http://url2"))))
        with patch("requests.get", return_value=mock_response):
            self.response = MetricCollector(metric).get()

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
        mock_response = Mock()
        mock_response.json.return_value = dict(
            jobs=[dict(name="job", url="http://job", buildable=True, color="red",
                       builds=[dict(result="red", timestamp="1552686540953")])])
        metric = dict(
            type="failed_jobs", addition="sum",
            sources=dict(
                a=dict(type="jenkins", parameters=dict(url="http://jenkins", failure_type=["Red"])),
                b=dict(type="random")))
        with patch("requests.get", return_value=mock_response):
            self.response = MetricCollector(metric).get()

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        sources = self.response["sources"]
        self.assertEqual("1", sources[0]["value"])
        self.assertTrue(sources[1]["value"])


class CollectorErrorTest(unittest.TestCase):
    """Unit tests for error handling."""

    def setUp(self):
        """Clear cache."""
        self.metric = dict(
            type="tests", addition="sum", sources=dict(a=dict(type="junit", parameters=dict(url="http://url"))))

    def test_connection_error(self):
        """Test that an error retrieving the data is handled."""
        with patch("requests.get", side_effect=Exception):
            response = MetricCollector(self.metric).get()
        self.assertTrue(response["sources"][0]["connection_error"].startswith("Traceback"))

    def test_parse_error(self):
        """Test that an error retrieving the data is handled."""
        mock_response = Mock()
        mock_response.text = "1"
        with patch("requests.get", return_value=mock_response):
            response = MetricCollector(self.metric).get()
        self.assertTrue(response["sources"][0]["parse_error"].startswith("Traceback"))
