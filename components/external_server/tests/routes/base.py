"""Base classes for unit tests."""

import unittest
from unittest.mock import Mock

from shared_data_model import DATA_MODEL


class RouteTestCase(unittest.TestCase):
    """Base class for route unit tests."""

    def setUp(self):
        """Override to set up the database and prepare the data model."""
        self.database = Mock()


class DataModelTestCase(RouteTestCase):
    """Base class for unit tests that use the data model."""

    @classmethod
    def setUpClass(cls) -> None:
        """Override to set up the data model."""
        cls.data_model = DATA_MODEL.dict(exclude_none=True)
        cls.data_model["_id"] = "id"
        cls.data_model["timestamp"] = "now"

    def setUp(self):
        """Override to set up the database and prepare the data model."""
        super().setUp()
        self.database.datamodels.find_one.return_value = self.data_model
