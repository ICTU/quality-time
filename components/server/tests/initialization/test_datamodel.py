"""Unit tests for importing the data model."""

import pathlib
import unittest
from unittest.mock import Mock, mock_open, patch

from initialization.datamodel import import_datamodel


class DataModelImportTest(unittest.TestCase):
    """Unit tests for the data model import function."""

    def setUp(self):
        """Override to set up the database."""
        self.database = Mock()
        self.database.datamodels.find_one.return_value = dict(_id="id", timestamp="timestamp")

    def import_data_model(self, data_model_json: str) -> None:
        """Import the data model."""
        with patch.object(pathlib.Path, "open", mock_open(read_data=data_model_json)):
            import_datamodel(self.database)

    def test_first_import(self):
        """Test that a data model can be imported if there are no data models in the database."""
        self.database.datamodels.find_one.return_value = None
        self.import_data_model('{"subjects": []}')
        self.database.datamodels.insert_one.assert_called_once()

    def test_import(self):
        """Test that a data model can be imported."""
        self.import_data_model('{"subjects": []}')
        self.database.datamodels.insert_one.assert_called_once()

    def test_skip_import(self):
        """Test that a data model is not imported if it's unchanged."""
        self.import_data_model("{}")
        self.database.datamodels.insert_one.assert_not_called()
