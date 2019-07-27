"""Unit tests for the Collector class."""

from unittest.mock import patch, Mock

from metric_collectors import MetricCollector
from .source_collector_test_case import SourceCollectorTestCase


class CollectorTest(SourceCollectorTestCase):
    """Unit tests for the Collector class."""

    def setUp(self):
        metric = dict(
            type="tests", addition="sum", sources=dict(a=dict(type="junit", parameters=dict(url="http://url"))))
        self.response = self.collect(metric, get_request_text="<testsuite tests='2'></testsuite>")

    def test_source_response_api_url(self):
        """Test that the api url used for contacting the source is returned."""
        self.assert_api_url("http://url", self.response)

    def test_source_response_landing_url(self):
        """Test that the landing url for the source is returned."""
        self.assert_landing_url("http://url", self.response)

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        self.assert_value("2", self.response)


class CollectorWithMultipleSourcesTest(SourceCollectorTestCase):
    """Unit tests for the collector with multiple sources."""

    def setUp(self):
        metric = dict(
            type="tests", addition="sum",
            sources=dict(
                a=dict(type="junit", parameters=dict(url="http://url")),
                b=dict(type="junit", parameters=dict(url="http://url2"))))
        self.response = self.collect(metric, get_request_text="<testsuite tests='2'></testsuite>")

    def test_source_response_api_url(self):
        """Test that the api url used for contacting the source is returned."""
        self.assert_api_url("http://url2", self.response, source_index=1)

    def test_source_response_landing_url(self):
        """Test that the landing url for the source is returned."""
        self.assert_landing_url("http://url2", self.response, source_index=1)

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        self.assert_value("2", self.response, source_index=1)


class CollectorWithMultipleSourceTypesTest(SourceCollectorTestCase):
    """Unit tests for collecting measurements from different source types."""

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        json = dict(
            jobs=[dict(name="job", url="http://job", buildable=True, color="red",
                       builds=[dict(result="red", timestamp="1552686540953")])])
        metric = dict(
            type="failed_jobs", addition="sum",
            sources=dict(
                a=dict(type="jenkins", parameters=dict(url="http://jenkins", failure_type=["Red"])),
                b=dict(type="random")))
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_value("1", response)
        self.assertTrue(response["sources"][1]["value"])


class CollectorErrorTest(SourceCollectorTestCase):
    """Unit tests for error handling."""

    def setUp(self):
        self.metric = dict(
            type="tests", addition="sum", sources=dict(a=dict(type="junit", parameters=dict(url="http://url"))))

    def test_connection_error(self):
        """Test that an error retrieving the data is handled."""
        with patch("requests.get", side_effect=Exception):
            response = MetricCollector(self.metric, dict()).get()
        self.assertTrue(response["sources"][0]["connection_error"].startswith("Traceback"))

    def test_parse_error(self):
        """Test that an error retrieving the data is handled."""
        mock_response = Mock()
        mock_response.text = "1"
        response = self.collect(self.metric, get_request_text="1")
        self.assertTrue(response["sources"][0]["parse_error"].startswith("Traceback"))
