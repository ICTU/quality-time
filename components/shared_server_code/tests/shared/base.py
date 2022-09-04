"""Base class for unit tests."""

import json
import unittest

from shared_data_model import DATA_MODEL_JSON


class DataModelTestCase(unittest.TestCase):
    """Base class for unit tests that use the data model from the database."""

    @classmethod
    def setUpClass(cls) -> None:
        """Override to set up the data model."""
        cls.data_model = json.loads(DATA_MODEL_JSON)
        cls.data_model["_id"] = "id"
        cls.data_model["timestamp"] = "now"
