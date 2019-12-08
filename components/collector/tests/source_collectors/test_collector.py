"""Unit tests for the Collector class."""

from unittest.mock import patch, Mock

from metric_collectors import MetricCollector
from .source_collector_test_case import SourceCollectorTestCase


class CollectorTest(SourceCollectorTestCase):
    """Unit tests for the Collector class."""

    def setUp(self):
        self.sources = dict(source_uuid=dict(type="junit", parameters=dict(url="https://junit")))
        self.metric = dict(type="tests", addition="sum", sources=self.sources)
        self.junit_xml = "<testsuite><testcase/><testcase/></testsuite>"

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        response = self.collect(self.metric, get_request_text=self.junit_xml)
        self.assert_measurement(response, value="2", api_url="https://junit", landing_url="https://junit")

    def test_source_response_landing_url_different(self):
        """Test that the landing url for the source is returned."""
        self.sources["source_uuid"]["parameters"]["landing_url"] = "https://landing"
        response = self.collect(self.metric, get_request_text=self.junit_xml)
        self.assert_measurement(response, landing_url="https://landing")

    def test_multiple_sources(self):
        """Test that the measurement for the source is returned."""
        self.sources["junit2"] = dict(type="junit", parameters=dict(url="https://junit2"))
        response = self.collect(self.metric, get_request_text=self.junit_xml)
        self.assert_measurement(
            response, value="2", api_url="https://junit2", landing_url="https://junit2", source_index=1)

    def test_multiple_source_types(self):
        """Test that the measurement for the source is returned."""
        self.sources["sonarqube"] = dict(type="sonarqube", parameters=dict(url="https://sonarqube", component="id"))
        json = dict(component=dict(measures=[dict(metric="tests", value="88")]))
        response = self.collect(self.metric, get_request_text=self.junit_xml, get_request_json_return_value=json)
        self.assert_measurement(response, value="2", url="https://junit", source_index=0)
        self.assert_measurement(response, value="88", url="https://sonarqube", source_index=1)

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
