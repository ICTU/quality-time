"""Unit tests for the data models collection."""

import unittest
from unittest.mock import Mock

from shared.database.datamodels import latest_datamodel


class DataModelsTest(unittest.TestCase):
    """Unit tests for the data models collection."""

    def setUp(self) -> None:
        """Override to setup the database."""
        self.database = Mock()

    def test_latest_datamodel(self):
        """Test that the latest data model is returned and the id is converted to string."""
        self.database.datamodels.find_one.return_value = dict(_id=123)
        self.assertEqual(dict(_id="123"), latest_datamodel(self.database))

    def test_missing_datamodel(self):
        """Test that the an empty data model is returned when the data models collection is empty."""
        self.database.datamodels.find_one.return_value = None
        self.assertEqual({}, latest_datamodel(self.database))
