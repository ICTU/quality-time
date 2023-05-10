"""Unit tests for the Collector class."""

from unittest.mock import Mock, patch

import aiohttp

from base_collectors import SourceCollector
from collector_utilities.type import URL
from model import Entity, Entities, SourceResponses

from .source_collector_test_case import SourceCollectorTestCase


class CollectorTest(SourceCollectorTestCase):
    """Unit tests for the Collector class."""

    SOURCE_TYPE = "junit"
    METRIC_TYPE = "tests"
    JUNIT_URL = "https://junit"
    JUNIT_XML = '<testsuite><testcase name="tc1" /><testcase name="tc2" /></testsuite>'

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
        self.sources["junit2"] = {"type": "junit", "parameters": {"url": junit_url2}}
        response = await self.collect(get_request_text=self.JUNIT_XML)
        self.assert_measurement(response, value="2", api_url=junit_url2, landing_url=junit_url2, source_index=1)

    async def test_multiple_source_types(self):
        """Test that the measurement for the source is returned."""
        sonarqube_url = "https://sonarqube"
        self.sources["sonarqube"] = {"type": "sonarqube", "parameters": {"url": sonarqube_url, "component": "id"}}
        json = {"component": {"measures": [{"metric": "tests", "value": "88"}]}}
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
                return URL("https://api_url")

            async def _landing_url(self, responses: SourceResponses) -> URL:
                """Override to raise an error."""
                raise NotImplementedError

        with patch("aiohttp.ClientSession.get", side_effect=Exception):
            async with aiohttp.ClientSession() as session:
                response = await FailingLandingUrl(session, self.sources["source_id"]).collect()
        self.assertEqual("https://api_url", response.landing_url)

    async def test_default_parameter_value_supersedes_empty_string(self):
        """Test that a parameter default value takes precedence over an empty string."""
        sources = {"source_uuid": {"type": "calendar", "parameters": {"date": ""}}}
        self.metric = {"type": "source_up_to_dateness", "addition": "max", "sources": sources}
        response = await self.collect()
        self.assert_measurement(response, value="0")

    async def test_including_entities(self):
        """Test that only entities marked for inclusion, are included."""

        class ThreeParsedEntities(SourceCollector):
            """Fake collector returning parsed entities."""

            async def _parse_entities(self, responses: SourceResponses) -> Entities:
                """Return three parsed entities."""
                return Entities([Entity(str(x)) for x in range(3)])

        with patch("base_collectors.SourceCollector._include_entity", side_effect=[True, False, True]):
            async with aiohttp.ClientSession() as session:
                collector = ThreeParsedEntities(session, {})
                res = await collector._parse_source_responses(SourceResponses())  # noqa: SLF001

        self.assertEqual(len(res.entities), 2)
        self.assertNotIn({"key": "1"}, res.entities)
        self.assertIn({"key": "2"}, res.entities)
