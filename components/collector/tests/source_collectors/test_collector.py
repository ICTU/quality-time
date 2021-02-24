"""Unit tests for the Collector class."""

from datetime import datetime
from unittest.mock import Mock, patch

import aiohttp

from base_collectors import SourceCollector
from collector_utilities.type import URL
from source_model import SourceResponses

from .source_collector_test_case import SourceCollectorTestCase


class CollectorTest(SourceCollectorTestCase):
    """Unit tests for the Collector class."""

    SOURCE_TYPE = "junit"
    METRIC_TYPE = "tests"
    JUNIT_URL = "https://junit"
    JUNIT_XML = "<testsuite><testcase/><testcase/></testsuite>"

    async def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        response = await self.collect(get_request_text=self.JUNIT_XML)
        self.assert_measurement(response, value="2", api_url=self.JUNIT_URL, landing_url=self.JUNIT_URL)

    async def test_source_response_landing_url_different(self):
        """Test that the landing url for the source is returned."""
        self.set_source_parameter("landing_url", landing_url := "https://landing")
        response = await self.collect(get_request_text=self.JUNIT_XML)
        self.assert_measurement(response, api_url=self.JUNIT_URL, landing_url=landing_url)

    async def test_multiple_sources(self):
        """Test that the measurement for the source is returned."""
        junit_url2 = "https://junit2"
        self.sources["junit2"] = dict(type="junit", parameters=dict(url=junit_url2))
        response = await self.collect(get_request_text=self.JUNIT_XML)
        self.assert_measurement(response, value="2", api_url=junit_url2, landing_url=junit_url2, source_index=1)

    async def test_multiple_source_types(self):
        """Test that the measurement for the source is returned."""
        sonarqube_url = "https://sonarqube"
        self.sources["sonarqube"] = dict(type="sonarqube", parameters=dict(url=sonarqube_url, component="id"))
        json = dict(component=dict(measures=[dict(metric="tests", value="88")]))
        response = await self.collect(get_request_json_return_value=json, get_request_text=self.JUNIT_XML)
        self.assert_measurement(response, value="2", url=self.JUNIT_XML, source_index=0)
        self.assert_measurement(response, value="88", url=sonarqube_url, source_index=1)

    async def test_parse_error(self):
        """Test that an error retrieving the data is handled."""
        mock_response = Mock()
        mock_response.text = "1"
        response = await self.collect(get_request_text="1")
        self.assert_measurement(response, parse_error="Traceback")

    async def test_landing_url_error(self):
        """Test that an error retrieving the data is handled."""

        class FailingLandingUrl(SourceCollector):
            """Add a landing_url implementation that fails."""

            async def _api_url(self) -> URL:
                """Override to return an URL fixture."""
                return "https://api_url"

            async def _landing_url(self, responses: SourceResponses) -> URL:
                """Override to raise an error."""
                raise NotImplementedError

        with patch("aiohttp.ClientSession.get", side_effect=Exception):
            async with aiohttp.ClientSession() as session:
                response = await FailingLandingUrl(session, self.metric, {}).get()
        self.assertEqual("https://api_url", response["landing_url"])

    async def test_default_parameter_value_supersedes_empty_string(self):
        """Test that a parameter default value takes precedence over an empty string."""
        sources = dict(source_uuid=dict(type="calendar", parameters=dict(date="")))
        self.metric = dict(type="source_up_to_dateness", addition="max", sources=sources)
        response = await self.collect()
        self.assert_measurement(response, value=str((datetime.today() - datetime(2020, 1, 1)).days))
