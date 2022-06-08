"""Unit tests for the data models collection."""

import unittest
from unittest.mock import Mock

from shared.database.datamodels import insert_new_datamodel, latest_datamodel


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

    def test_insert_data_model_with_id(self):
        """Test that a new data model can be inserted."""
        insert_new_datamodel(self.database, dict(_id="id"))
        self.database.datamodels.insert_one.assert_called_once()

    def test_insert_data_model_without_id(self):
        """Test that a new data model can be inserted."""
        insert_new_datamodel(self.database, {})
        self.database.datamodels.insert_one.assert_called_once()
