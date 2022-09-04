"""Base classes for unit tests."""

import json
import unittest
from unittest.mock import Mock

from shared_data_model import DATA_MODEL_JSON


class RouteTestCase(unittest.TestCase):  # skipcq: PTC-W0046
    """Base class for route unit tests."""

    def setUp(self):
        """Override to set up the database and prepare the data model."""
        self.database = Mock()


class DataModelTestCase(RouteTestCase):  # skipcq: PTC-W0046
    """Base class for unit tests that use the data model."""

    def setUp(self):
        """Override to set up the database and prepare the data model."""
        super().setUp()
        self.data_model = json.loads(DATA_MODEL_JSON)
        self.data_model["_id"] = "id"
        self.data_model["timestamp"] = "now"
        self.database.datamodels.find_one.return_value = self.data_model
