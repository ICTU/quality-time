"""Base class for source collector unit tests."""

import json
import pathlib
from unittest.mock import patch, AsyncMock, Mock

import aiohttp
import aiounittest

from metric_collectors import MetricCollector
from collector_utilities.type import Measurement


class SourceCollectorTestCase(aiounittest.AsyncTestCase):
    """Base class for source collector unit tests."""

    @classmethod
    def setUpClass(cls) -> None:
        module_dir = pathlib.Path(__file__).resolve().parent
        data_model_path = module_dir.parent.parent.parent / "server" / "src" / "data" / "datamodel.json"
        with data_model_path.open() as json_data_model:
            cls.data_model = json.load(json_data_model)

    async def collect(self, metric, *,
                      get_request_json_return_value=None,
                      get_request_json_side_effect=None,
                      get_request_content="",
                      get_request_encoding="",
                      get_request_text="",
                      post_request_side_effect=None,
                      post_request_json_return_value=None) -> Measurement:
        """Collect the metric."""
        mock_get_request = Mock()
        if get_request_json_side_effect:
            mock_get_request.json.side_effect = get_request_json_side_effect
        else:
            mock_get_request.json.return_value = get_request_json_return_value
        if get_request_encoding != "":
            mock_get_request.encoding = get_request_encoding
        mock_get_request.content = get_request_content
        mock_get_request.text = get_request_text
        mock_async_post_request = AsyncMock()
        mock_async_post_request.raise_for_status = Mock()
        mock_async_post_request.json.return_value = post_request_json_return_value
        with patch(
                "aiohttp.ClientSession.post",
                AsyncMock(return_value=mock_async_post_request, side_effect=post_request_side_effect)):
            with patch("requests.get", return_value=mock_get_request):
                async with aiohttp.ClientSession() as session:
                    return await MetricCollector(session, metric, self.data_model).get()

    def assert_measurement(self, measurement: Measurement, *, source_index: int = 0, **attributes) -> None:
        """Assert that the measurement has the expected attributes."""
        for attribute_key in ("connection_error", "parse_error"):
            if (attribute_value := attributes.get(attribute_key)) is not None:
                self.assertIn(attribute_value, measurement["sources"][source_index][attribute_key])
            else:
                self.assertIsNone(measurement["sources"][source_index][attribute_key])
        for attribute_key in ("value", "total", "entities", "api_url", "landing_url"):
            if (attribute_value := attributes.get(attribute_key)) is not None:
                self.assertEqual(attribute_value, measurement["sources"][source_index][attribute_key])
