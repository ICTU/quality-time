"""Unit tests for the Collector class."""

from unittest.mock import patch, Mock

from metric_collectors import MetricCollector
from .source_collector_test_case import SourceCollectorTestCase


class CollectorTest(SourceCollectorTestCase):
    """Unit tests for the Collector class."""

    def setUp(self):
        self.junit_url = "https://junit"
        self.sources = dict(source_uuid=dict(type="junit", parameters=dict(url=self.junit_url)))
        self.metric = dict(type="tests", addition="sum", sources=self.sources)
        self.junit_xml = "<testsuite><testcase/><testcase/></testsuite>"

    async def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        response = await self.collect(self.metric, get_request_text=self.junit_xml)
        self.assert_measurement(response, value="2", api_url=self.junit_url, landing_url=self.junit_url)

    async def test_source_response_landing_url_different(self):
        """Test that the landing url for the source is returned."""
        self.sources["source_uuid"]["parameters"]["landing_url"] = landing_url = "https://landing"
        response = await self.collect(self.metric, get_request_text=self.junit_xml)
        self.assert_measurement(response, api_url=self.junit_url, landing_url=landing_url)

    async def test_multiple_sources(self):
        """Test that the measurement for the source is returned."""
        junit_url2 = "https://junit2"
        self.sources["junit2"] = dict(type="junit", parameters=dict(url=junit_url2))
        response = await self.collect(self.metric, get_request_text=self.junit_xml)
        self.assert_measurement(response, value="2", api_url=junit_url2, landing_url=junit_url2, source_index=1)

    async def test_multiple_source_types(self):
        """Test that the measurement for the source is returned."""
        sonarqube_url = "https://sonarqube"
        self.sources["sonarqube"] = dict(type="sonarqube", parameters=dict(url=sonarqube_url, component="id"))
        json = dict(component=dict(measures=[dict(metric="tests", value="88")]))
        response = await self.collect(self.metric, get_request_text=self.junit_xml, get_request_json_return_value=json)
        self.assert_measurement(response, value="2", url=self.junit_xml, source_index=0)
        self.assert_measurement(response, value="88", url=sonarqube_url, source_index=1)

    async def test_connection_error(self):
        """Test that an error retrieving the data is handled."""
        with patch("requests.get", side_effect=Exception):
            response = await MetricCollector(self.metric, dict()).get()
        self.assert_measurement(response, connection_error="Traceback")

    async def test_parse_error(self):
        """Test that an error retrieving the data is handled."""
        mock_response = Mock()
        mock_response.text = "1"
        response = await self.collect(self.metric, get_request_text="1")
        self.assert_measurement(response, parse_error="Traceback")
