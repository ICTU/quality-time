"""Unit tests for importing the datamodel."""

import unittest
from unittest.mock import Mock, patch, mock_open

from src.initialization.datamodel import import_datamodel


class DataModelImportTest(unittest.TestCase):
    """Unit tests for the data model import function."""

    def setUp(self):
        self.database = Mock()

    def test_first_import(self):
        """Test that a data model can be imported if there are no data models in the database."""
        self.database.datamodels.find_one.return_value = None
        data_model_json = '{"subjects": []}'
        with patch("builtins.open", mock_open(read_data=data_model_json)):
            import_datamodel(self.database)
        self.database.datamodels.insert_one.assert_called_once()

    def test_import(self):
        """Test that a data model can be imported."""
        self.database.datamodels.find_one.return_value = dict(_id="id", timestamp="timestamp")
        data_model_json = '{"subjects": []}'
        with patch("builtins.open", mock_open(read_data=data_model_json)):
            import_datamodel(self.database)
        self.database.datamodels.insert_one.assert_called_once()

    def test_skip_import(self):
        """Test that a data model is not imported if it's unchanged."""
        self.database.datamodels.find_one.return_value = dict(_id="id", timestamp="timestamp")
        data_model_json = '{}'
        with patch("builtins.open", mock_open(read_data=data_model_json)):
            import_datamodel(self.database)
        self.database.datamodels.insert_one.assert_not_called()
