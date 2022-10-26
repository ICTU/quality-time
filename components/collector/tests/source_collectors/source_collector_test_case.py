"""Base class for source collector unit tests."""

import io
import logging
import unittest
import zipfile
from unittest.mock import AsyncMock, PropertyMock, patch, DEFAULT as STOP_SENTINEL

import aiohttp

from base_collectors import MetricCollector


class SourceCollectorTestCase(unittest.IsolatedAsyncioTestCase):  # skipcq: PTC-W0046
    """Base class for source collector unit tests."""

    METRIC_TYPE = SOURCE_TYPE = "Subclass responsibility"
    METRIC_ADDITION = "sum"

    @classmethod
    def setUpClass(cls) -> None:
        """Override to disable logging and load the data model so it is available for all unit tests."""
        logging.disable(logging.CRITICAL)  # skipcq: PY-A6006

    @classmethod
    def tearDownClass(cls) -> None:
        """Override to reset logging."""
        logging.disable(logging.NOTSET)  # skipcq: PY-A6006

    def setUp(self) -> None:
        """Extend to set up the source and metric under test."""
        self.sources = dict(source_id=dict(type=self.SOURCE_TYPE, parameters=dict(url=f"https://{self.SOURCE_TYPE}")))
        self.metric = dict(type=self.METRIC_TYPE, sources=self.sources, addition=self.METRIC_ADDITION)

    async def collect(
        self,
        *,
        get_request_json_return_value=None,
        get_request_json_side_effect=None,
        get_request_side_effect=None,
        get_request_content="",
        get_request_text="",
        get_request_headers=None,
        get_request_links=None,
        post_request_side_effect=None,
        post_request_json_return_value=None,
        post_request_json_side_effect=None,
        return_mocks=False,
    ):  # pylint: disable=too-many-locals
        """Collect the metric."""
        get_response = self.__get_response(
            get_request_json_return_value,
            get_request_json_side_effect,
            get_request_content,
            get_request_text,
            get_request_headers,
            get_request_links,
        )
        post_response = self.__post_response(post_request_json_return_value, post_request_json_side_effect)
        get = AsyncMock(return_value=get_response, side_effect=get_request_side_effect)
        post = AsyncMock(return_value=post_response, side_effect=post_request_side_effect)
        with patch("aiohttp.ClientSession.get", get), patch("aiohttp.ClientSession.post", post):
            async with aiohttp.ClientSession() as session:
                result = await MetricCollector(session, self.metric).collect()
                return (result, get, post) if return_mocks else result

    @staticmethod
    def __get_response(json_return_value, json_side_effect, content, text, headers, links) -> AsyncMock:
        """Create the mock get response."""
        # pylint: disable=too-many-arguments
        get_response = AsyncMock()
        get_response.json = AsyncMock(return_value=json_return_value, side_effect=json_side_effect)
        get_response.read.return_value = content
        get_response.text.return_value = text
        type(get_response).headers = PropertyMock(return_value=headers or {})
        type(get_response).links = PropertyMock(return_value={}, side_effect=[links, {}] if links else None)
        type(get_response).filename = PropertyMock(return_value="")
        return get_response

    @staticmethod
    def __post_response(json_return_value, json_side_effect: list = None) -> AsyncMock:
        """Create the mock post response."""
        post_response = AsyncMock()
        if json_side_effect:
            if not json_return_value:  # put the last side effect into return value, if it was not already given
                json_return_value = json_side_effect[-1]
            json_side_effect.append(STOP_SENTINEL)  # AsyncMock apparently does catch StopAsyncIteration
        post_response.json = AsyncMock(return_value=json_return_value, side_effect=json_side_effect)
        return post_response

    def assert_measurement(self, measurement, *, source_index: int = 0, **attributes) -> None:
        """Assert that the measurement has the expected attributes."""
        for attribute_key in ("connection_error", "parse_error"):
            if (attribute_value := attributes.get(attribute_key)) is not None:
                attributes.update(value=None, total=None, entities=[])
                self.assertIn(attribute_value, getattr(measurement.sources[source_index], attribute_key))
            else:
                self.assertIsNone(getattr(measurement.sources[source_index], attribute_key))
        for attribute_key in ("value", "total", "entities", "api_url", "landing_url"):
            if (attribute_value := attributes.get(attribute_key, "value not specified")) != "value not specified":
                self.__assert_measurement_source_attribute(attribute_key, attribute_value, measurement, source_index)

    def __assert_measurement_source_attribute(self, attribute_key, expected_attribute_value, measurement, source_index):
        """Assert that the measurement source attribute has the expected value."""
        attribute_value = getattr(measurement.sources[source_index], attribute_key)
        if isinstance(expected_attribute_value, list):
            for pair in zip(expected_attribute_value, attribute_value):
                self.assertDictEqual(pair[0], pair[1])
            self.assertEqual(len(expected_attribute_value), len(attribute_value), attribute_key)
        else:
            self.assertEqual(expected_attribute_value, attribute_value, attribute_key)

    @staticmethod
    def zipped_report(*filenames_and_contents: tuple[str, str]) -> bytes:
        """Return a zipped report."""
        bytes_io = io.BytesIO()
        with zipfile.ZipFile(bytes_io, mode="w") as zipped_report:
            for filename, content in filenames_and_contents:
                zipped_report.writestr(filename, content)
        return bytes_io.getvalue()

    def set_source_parameter(self, key: str, value: str | list[str]) -> None:
        """Set a source parameter."""
        self.sources["source_id"]["parameters"][key] = value
