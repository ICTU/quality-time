"""Unit tests for the Collector class."""

from unittest.mock import patch, Mock

from metric_collectors import MetricCollector
from .source_collector_test_case import SourceCollectorTestCase


class CollectorTest(SourceCollectorTestCase):
    """Unit tests for the Collector class."""

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        metric = dict(
            type="tests", addition="sum", sources=dict(a=dict(type="junit", parameters=dict(url="https://url"))))
        response = self.collect(metric, get_request_text="<testsuite><testcase/><testcase/></testsuite>")
        self.assert_measurement(response, value="2", api_url="https://url", landing_url="https://url")


class CollectorTestLandingUrl(SourceCollectorTestCase):
    """Unit tests for the Collector class, when landing url initialized."""

    def test_source_response_landing_url_different(self):
        """Test that the landing url for the source is returned."""
        metric = dict(
            type="tests", addition="sum",
            sources=dict(a=dict(type="junit", parameters=dict(url="https://url", landing_url='https://landing'))))
        response = self.collect(metric, get_request_text="<testsuite><testcase/><testcase/></testsuite>")
        self.assert_measurement(response, landing_url="https://landing")


class CollectorWithMultipleSourcesTest(SourceCollectorTestCase):
    """Unit tests for the collector with multiple sources."""

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        metric = dict(
            type="tests", addition="sum",
            sources=dict(
                a=dict(type="junit", parameters=dict(url="https://url")),
                b=dict(type="junit", parameters=dict(url="https://url2"))))
        response = self.collect(metric, get_request_text="<testsuite><testcase/><testcase/></testsuite>")
        self.assert_measurement(response, value="2", api_url="https://url2", landing_url="https://url2", source_index=1)


class CollectorWithMultipleSourceTypesTest(SourceCollectorTestCase):
    """Unit tests for collecting measurements from different source types."""

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        json = dict(
            jobs=[dict(name="job", url="https://job", buildable=True, color="red",
                       builds=[dict(result="red", timestamp="1552686540953")])])
        metric = dict(
            type="failed_jobs", addition="sum",
            sources=dict(
                a=dict(type="jenkins", parameters=dict(url="https://jenkins", failure_type=["Red"])),
                b=dict(type="random")))
        response = self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="1")
        self.assertTrue(response["sources"][1]["value"])


class CollectorErrorTest(SourceCollectorTestCase):
    """Unit tests for error handling."""

    def setUp(self):
        self.metric = dict(
            type="tests", addition="sum", sources=dict(a=dict(type="junit", parameters=dict(url="https://url"))))

    def test_connection_error(self):
        """Test that an error retrieving the data is handled."""
        with patch("requests.get", side_effect=Exception):
            response = MetricCollector(self.metric, dict()).get()
        self.assert_measurement(response, connection_error="Traceback")

    def test_parse_error(self):
        """Test that an error retrieving the data is handled."""
        mock_response = Mock()
        mock_response.text = "1"
        response = self.collect(self.metric, get_request_text="1")
        self.assert_measurement(response, parse_error="Traceback")
