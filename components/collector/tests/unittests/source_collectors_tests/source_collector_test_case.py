"""Base class for source collector unit tests."""

import json
import os.path
import pathlib
import unittest
from unittest.mock import patch, Mock

from metric_collectors import MetricCollector
from utilities.type import Entities, Measurement, Value


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

    def assert_measurement(
            self, measurement: Measurement, *, value: Value = None, total: Value = None, entities: Entities = None,
            api_url: str = None, landing_url: str = None, connection_error: bool = False,
            parse_error_fragment: str = None, source_index: int = 0) -> None:
        """Assert that the measurement has the expected attributes."""
        if value is not None:
            self.assertEqual(value, measurement["sources"][source_index]["value"])
        if total is not None:
            self.assertEqual(total, measurement["sources"][source_index]["total"])
        if entities is not None:
            self.assertEqual(entities, measurement["sources"][source_index]["entities"])
        if api_url is not None:
            self.assertEqual(api_url, measurement["sources"][source_index]["api_url"])
        if landing_url is not None:
            self.assertEqual(landing_url, measurement["sources"][source_index]["landing_url"])
        if parse_error_fragment is not None:
            self.assertIn(parse_error_fragment, measurement["sources"][source_index]["parse_error"])
        self.assertEqual(connection_error, bool(measurement["sources"][source_index]["connection_error"]))
