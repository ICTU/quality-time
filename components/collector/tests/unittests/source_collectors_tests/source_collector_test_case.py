"""Base class for source collector unit tests."""

import json
import os.path
import pathlib
import unittest
from unittest.mock import patch, Mock

from metric_collectors import MetricCollector
from utilities.type import Measurement


class SourceCollectorTestCase(unittest.TestCase):
    """Base class for source collector unit tests."""

    @classmethod
    def setUpClass(cls) -> None:
        module_dir = os.path.dirname(os.path.abspath(__file__))
        data_model_path = pathlib.Path(module_dir, "..", "..", "..", "..", "server", "src", "data", "datamodel.json")
        with open(data_model_path) as json_data_model:
            cls.data_model = json.load(json_data_model)

    def collect(self, metric, *,
                get_request_json_return_value=None,
                get_request_json_side_effect=None,
                get_request_text="",
                post_request_side_effect=None,
                post_request_json_return_value=None,
                post_request_json_side_effect=None) -> Measurement:
        """Collect the metric. Keep a reference to the collector so it can be queried."""
        mock_get_request = Mock()
        if get_request_json_side_effect:
            mock_get_request.json.side_effect = get_request_json_side_effect
        else:
            mock_get_request.json.return_value = get_request_json_return_value
        mock_get_request.text = get_request_text
        mock_post_request = Mock()
        if post_request_json_side_effect:
            mock_post_request.json.side_effect = post_request_json_side_effect
        else:
            mock_post_request.json.return_value = post_request_json_return_value
        with patch("requests.post", return_value=mock_post_request, side_effect=post_request_side_effect):
            with patch("requests.get", return_value=mock_get_request):
                with patch("requests.delete", return_value=None):
                    self.collector = MetricCollector(metric, self.data_model)
                    return self.collector.get()

    def assert_measurement(self, measurement: Measurement, *, source_index: int = 0, **attributes) -> None:
        """Assert that the measurement has the expected attributes."""
        for attribute_key in ("value", "total", "entities", "api_url", "landing_url"):
            if (attribute_value := attributes.get(attribute_key)) is not None:
                self.assertEqual(attribute_value, measurement["sources"][source_index][attribute_key])
        for attribute_key in ("connection_error", "parse_error"):
            if (attribute_value := attributes.get(attribute_key)) is not None:
                self.assertIn(attribute_value, measurement["sources"][source_index][attribute_key])
            else:
                self.assertIsNone(measurement["sources"][source_index][attribute_key])
