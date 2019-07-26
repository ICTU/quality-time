"""Base class for source collector unit tests."""

import json
import os.path
import pathlib
import unittest

from metric_collectors import MetricCollector
from utilities.type import Entities, Response, Value


class SourceCollectorTestCase(unittest.TestCase):
    """Base class for source collector unit tests."""

    @classmethod
    def setUpClass(cls) -> None:
        module_dir = os.path.dirname(os.path.abspath(__file__))
        data_model_path = pathlib.Path(module_dir, "..", "..", "..", "..", "server", "src", "data", "datamodel.json")
        with open(data_model_path) as json_data_model:
            cls.data_model = json.load(json_data_model)

    def collect(self, metric):
        """Collect the metric. Keep a reference to the collector so it can be queried."""
        self.collector = MetricCollector(metric, self.data_model)
        return self.collector.get()

    def assert_value(self, expected_value: Value, response: Response) -> None:
        """Assert that the measurement response has the expected value."""
        self.assertEqual(expected_value, response["sources"][0]["value"])

    def assert_entities(self, expected_entities: Entities, response: Response) -> None:
        """Assert that the measurement response has the expected entities."""
        self.assertEqual(expected_entities, response["sources"][0]["entities"])

    def assert_api_url(self, expected_url: str, response: Response) -> None:
        """Assert that the measurement response has the expected api url."""
        self.assertEqual(expected_url, response["sources"][0]["api_url"])

    def assert_landing_url(self, expected_url: str, response: Response) -> None:
        """Assert that the measurement response has the expected landing url."""
        self.assertEqual(expected_url, response["sources"][0]["landing_url"])
