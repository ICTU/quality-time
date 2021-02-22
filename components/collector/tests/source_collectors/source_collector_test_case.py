"""Base class for source collector unit tests."""

import io
import json
import logging
import pathlib
import unittest
import zipfile
from typing import List, Tuple, Union
from unittest.mock import AsyncMock, PropertyMock, patch

import aiohttp

from base_collectors import MetricsCollector


class SourceCollectorTestCase(unittest.IsolatedAsyncioTestCase):
    """Base class for source collector unit tests."""

    METRIC_TYPE = SOURCE_TYPE = "Subclass responsibility"
    METRIC_ADDITION = "sum"

    @classmethod
    def setUpClass(cls) -> None:  # pylint: disable=invalid-name
        """Override to disable logging and load the data model so it is available for all unit tests."""
        logging.disable(logging.CRITICAL)
        module_dir = pathlib.Path(__file__).resolve().parent
        data_model_path = module_dir.parent.parent.parent / "server" / "src" / "data" / "datamodel.json"
        with data_model_path.open() as json_data_model:
            cls.data_model = json.load(json_data_model)

    @classmethod
    def tearDownClass(cls) -> None:  # pylint: disable=invalid-name
        """Override to reset logging."""
        logging.disable(logging.NOTSET)

    def setUp(self) -> None:  # pylint: disable=invalid-name
        """Extend to set up the source and metric under test."""
        self.sources = dict(source_id=dict(type=self.SOURCE_TYPE, parameters=dict(url=f"https://{self.SOURCE_TYPE}")))
        self.metric = dict(type=self.METRIC_TYPE, sources=self.sources, addition=self.METRIC_ADDITION)

    async def collect(
        self,
        *,
        get_request_json_return_value=None,
        get_request_json_side_effect=None,
        get_request_content="",
        get_request_text="",
        get_request_links=None,
        post_request_side_effect=None,
        post_request_json_return_value=None,
    ):
        """Collect the metric."""
        mock_async_get_request = self.__mock_get_request(
            get_request_json_side_effect,
            get_request_json_return_value,
            get_request_content,
            get_request_text,
            get_request_links,
        )
        mock_async_post_request = self.__mock_post_request(post_request_json_return_value)
        with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_async_get_request)):
            with patch(
                "aiohttp.ClientSession.post",
                AsyncMock(return_value=mock_async_post_request, side_effect=post_request_side_effect),
            ):
                async with aiohttp.ClientSession() as session:
                    collector = MetricsCollector()
                    collector.data_model = self.data_model
                    return await collector.collect_sources(session, self.metric)

    @staticmethod
    def __mock_get_request(json_side_effect, json_return_value, content, text, links) -> AsyncMock:
        """Create the mock get request."""
        mock_async_get_request = AsyncMock()
        mock_async_get_request.json.side_effect = json_side_effect
        mock_async_get_request.json.return_value = json_return_value
        mock_async_get_request.read.return_value = content
        mock_async_get_request.text.return_value = text
        type(mock_async_get_request).links = PropertyMock(return_value={}, side_effect=[links, {}] if links else None)
        type(mock_async_get_request).filename = PropertyMock(return_value="")
        return mock_async_get_request

    @staticmethod
    def __mock_post_request(json_return_value) -> AsyncMock:
        """Create the mock post request."""
        mock_async_post_request = AsyncMock()
        mock_async_post_request.json.return_value = json_return_value
        return mock_async_post_request

    def assert_measurement(self, measurement, *, source_index: int = 0, **attributes) -> None:
        """Assert that the measurement has the expected attributes."""
        for attribute_key in ("connection_error", "parse_error"):
            if (attribute_value := attributes.get(attribute_key)) is not None:
                self.assertIn(attribute_value, measurement["sources"][source_index][attribute_key])
            else:
                self.assertIsNone(measurement["sources"][source_index][attribute_key])
        for attribute_key in ("value", "total", "entities", "api_url", "landing_url"):
            if (attribute_value := attributes.get(attribute_key, "value not specified")) != "value not specified":
                self.assertEqual(attribute_value, measurement["sources"][source_index][attribute_key])

    @staticmethod
    def zipped_report(*filenames_and_contents: Tuple[str, str]) -> bytes:
        """Return a zipped report."""
        bytes_io = io.BytesIO()
        with zipfile.ZipFile(bytes_io, mode="w") as zipped_report:
            for filename, content in filenames_and_contents:
                zipped_report.writestr(filename, content)
        return bytes_io.getvalue()

    def set_source_parameter(self, key: str, value: Union[str, List[str]]) -> None:
        """Set a source parameter."""
        self.sources["source_id"]["parameters"][key] = value
