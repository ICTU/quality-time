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
                get_request_raise_for_status_side_effect=None,
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
        if get_request_raise_for_status_side_effect:
            mock_get_request.raise_for_status.side_effect = get_request_raise_for_status_side_effect
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

    def assert_value(self, expected_value: Value, measurement: Measurement, source_index: int = 0) -> None:
        """Assert that the measurement has the expected value."""
        self.assertEqual(expected_value, measurement["sources"][source_index]["value"])

    def assert_total(self, expected_total: Value, measurement: Measurement, source_index: int = 0) -> None:
        """Assert that the measurement has the expected total."""
        self.assertEqual(expected_total, measurement["sources"][source_index]["total"])

    def assert_entities(self, expected_entities: Entities, measurement: Measurement, source_index: int = 0) -> None:
        """Assert that the measurement has the expected entities."""
        self.assertEqual(expected_entities, measurement["sources"][source_index]["entities"])

    def assert_api_url(self, expected_url: str, measurement: Measurement, source_index: int = 0) -> None:
        """Assert that the measurement has the expected api url."""
        self.assertEqual(expected_url, measurement["sources"][source_index]["api_url"])

    def assert_landing_url(self, expected_url: str, measurement: Measurement, source_index: int = 0) -> None:
        """Assert that the measurement has the expected landing url."""
        self.assertEqual(expected_url, measurement["sources"][source_index]["landing_url"])

    def assert_parse_error_contains(
            self, expected_parse_error: str, measurement: Measurement, source_index: int = 0) -> None:
        """Assert that the measurement has the expected parse error."""
        self.assertIn(expected_parse_error, measurement["sources"][source_index]["parse_error"])
