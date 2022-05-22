"""Test the data models collection."""

import unittest
from unittest.mock import Mock

from internal.database.datamodels import latest_datamodel


class DataModelsTest(unittest.TestCase):
    """Unit tests for getting the data model from the data models collection."""

    def setUp(self) -> None:
        """Override to create a database fixture."""
        self.database = Mock()

    def test_latest_data_model(self):
        """Test that the data model can be retrieved."""
        self.database.datamodels.find_one.return_value = data_model = dict(_id="id", metrics=dict(metric_type={}))
        self.assertEqual(data_model, latest_datamodel(self.database))

    def test_no_latest_data_model(self):
        """Test that retrieving a missing data model returns an empty dict."""
        self.database.datamodels.find_one.return_value = None
        self.assertEqual({}, latest_datamodel(self.database))
