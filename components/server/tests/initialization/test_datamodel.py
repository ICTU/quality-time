"""Unit tests for importing the data model."""

import json
import unittest
from unittest.mock import Mock

from initialization.datamodel import import_datamodel
from data.data_model import DATA_MODEL_JSON


class DataModelImportTest(unittest.TestCase):
    """Unit tests for the data model import function."""

    def setUp(self):
        """Override to set up the database."""
        self.database = Mock()
        self.database.datamodels.find_one.return_value = dict(_id="id", timestamp="timestamp")

    def test_first_import(self):
        """Test that a data model can be imported if there are no data models in the database."""
        self.database.datamodels.find_one.return_value = None
        import_datamodel(self.database)
        self.database.datamodels.insert_one.assert_called_once()

    def test_import(self):
        """Test that a data model can be imported."""
        import_datamodel(self.database)
        self.database.datamodels.insert_one.assert_called_once()

    def test_skip_import(self):
        """Test that a data model is not imported if it's unchanged."""
        data_model = json.loads(DATA_MODEL_JSON)
        data_model["_id"] = "id"
        data_model["timestamp"] = "timestamp"
        self.database.datamodels.find_one.return_value = data_model
        import_datamodel(self.database)
        self.database.datamodels.insert_one.assert_not_called()
