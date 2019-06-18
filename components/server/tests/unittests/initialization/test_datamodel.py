"""Unit tests for importing the datamodel."""

import unittest
from unittest.mock import Mock, patch, mock_open

from src.initialization.datamodel import import_datamodel


class DatamodelImportTest(unittest.TestCase):
    """Unit tests for the datamodel import function."""

    def test_first_import(self):
        """Test that a datamodel can be imported if there are no datamodels in the database."""
        database = Mock()
        database.datamodels.find_one.return_value = None
        datamodel_json = '{"subjects": []}'
        with patch("builtins.open", mock_open(read_data=datamodel_json)):
            import_datamodel(database)
        database.datamodels.insert_one.assert_called_once()

    def test_import(self):
        """Test that a datamodel can be imported."""
        database = Mock()
        database.datamodels.find_one.return_value = dict(_id="id", timestamp="timestamp")
        datamodel_json = '{"subjects": []}'
        with patch("builtins.open", mock_open(read_data=datamodel_json)):
            import_datamodel(database)
        database.datamodels.insert_one.assert_called_once()

    def test_skip_import(self):
        """Test that a datamodel is not imported if it's unchanged."""
        database = Mock()
        database.datamodels.find_one.return_value = dict(_id="id", timestamp="timestamp")
        datamodel_json = '{}'
        with patch("builtins.open", mock_open(read_data=datamodel_json)):
            import_datamodel(database)
        database.datamodels.insert_one.assert_not_called()
