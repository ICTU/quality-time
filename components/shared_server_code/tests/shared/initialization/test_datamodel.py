"""Unit tests for importing the data model."""

import unittest
from unittest.mock import Mock

from shared_data_model import DATA_MODEL

from shared.initialization.datamodel import import_datamodel


class DataModelImportTest(unittest.TestCase):
    """Unit tests for the data model import function."""

    def setUp(self):
        """Override to set up the database."""
        self.data_model = DATA_MODEL.dict(exclude_none=True)
        self.database = Mock()
        self.database.datamodels.find_one.return_value = self.data_model

    def test_first_import(self):
        """Test that a data model can be imported if there are no data models in the database."""
        self.database.datamodels.find_one.return_value = None
        import_datamodel(self.database)
        self.database.datamodels.insert_one.assert_called_once()

    def test_import(self):
        """Test that a data model can be imported."""
        self.data_model["_id"] = "id"
        self.data_model["timestamp"] = "timestamp"
        self.data_model["changed"] = "make sure the data model is changed"
        import_datamodel(self.database)
        self.database.datamodels.insert_one.assert_called_once()

    def test_skip_import(self):
        """Test that a data model is not imported if it's unchanged."""
        self.data_model["_id"] = "id"
        self.data_model["timestamp"] = "timestamp"
        import_datamodel(self.database)
        self.database.datamodels.insert_one.assert_not_called()
